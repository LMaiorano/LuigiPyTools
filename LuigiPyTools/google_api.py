#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: google_api
project: DSE-Mars-Reveal
date: 5/18/2020
author: lmaio



TODO:
    - examples

"""

import json
import os
import os.path
import pickle
import warnings
import inspect
from datetime import datetime

import pandas as pd
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GoogleService():
    def __init__(self, SCOPES, api_credentials, auth_dir=None):
        '''

        Parameters
        ----------
        SCOPES: list of str
            All scopes used for this program. See Google API documentation.
            Must match authorized scopes of provided api_credentials
        api_credentials: str
            Filepath to api client credentials json
        auth_dir: str, default './auth'
            Filepath to directory where authentication tokens should be stored.
            Directory should be included in .gitignore
        '''
        # Directory of script which is creating this object. Must run here in __init__
        frame = inspect.stack()[2]
        module = inspect.getmodule(frame[0])
        self.__call_module_dir = os.path.dirname(module.__file__)
        if not auth_dir:
            self._auth_dir = os.path.join(self.__call_module_dir, 'auth')
        else:
            self._auth_dir = auth_dir
        self._create_auth_dir()

        self._scopes = SCOPES
        self.__creds_file = api_credentials
        self._scope_type()

    def _create_auth_dir(self):
        '''Create directory for storing tokens and authentication'''
        if not os.path.exists(self._auth_dir):
            # Also create default auth dir if given is not valid
            os.makedirs(os.path.join(self.__call_module_dir, 'auth'))
            warnings.warn('Add "auth/" to your .gitignore for security purposes')

    def _scope_type(self):
        self.scope_types = []
        for scope in self._scopes:
            if 'spreadsheets' in scope:
                self.scope_types.append('sheets')
            if 'calendar' in scope:
                self.scope_types.append('calendar')

    def _service_connect(self, type):
        '''Connects to appropriate google api service

        Parameters
        ----------
        type: str
            'calendar' or 'sheets'
        '''
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token_file = os.path.join(self._auth_dir, 'token.pickle')
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
            # Check if loaded creds matches provided creds file
            with open(self.__creds_file, 'r') as f:
                prov_creds = json.load(f)
            if prov_creds['installed']['client_id'] != creds._client_id:
                creds = None
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.__creds_file, self._scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

        if type == 'sheets':
            service = build('sheets', 'v4', credentials=creds)
        elif type == 'calendar':
            service = build('calendar', 'v3', credentials=creds)
        else:
            raise KeyError("Scope type not recognised")

        return service



class GoogleSheets(GoogleService):
    '''
    Description
    -----------
    Interface with Google sheets and calendars

    '''
    def __init__(self, SCOPES, api_credentials, auth_dir=None):
        super().__init__(SCOPES, api_credentials, auth_dir=auth_dir)


    def _build_table(self, resp):
        '''Builds table using raw API response data, retaining formatting metadata

        Parameters
        ----------
        resp

        Returns
        -------

        '''

        # Ensure row has all cells, fill missing cells w/ default values
        def fill_missing_cells(cell_list, filler):
            diff = len(data['col_widths']) - len(cell_list)
            if diff > 0:
                cell_list += diff * [filler]
            return cell_list

        default_val = ''
        default_fmt = {'backgroundColor': {'red': 1, 'green': 1, 'blue': 1},
                       'padding': {'right': 3, 'left': 3},
                       'verticalAlignment': 'BOTTOM',
                       'wrapStrategy': 'OVERFLOW_CELL',
                       'textFormat': {'foregroundColor': {},
                                      'fontFamily': 'Calibri',
                                      'fontSize': 11,
                                      'bold': False,
                                      'italic': False,
                                      'strikethrough': False,
                                      'underline': False,
                                      'foregroundColorStyle': {'rgbColor': {}}},
                       'backgroundColorStyle': {'rgbColor': {'red': 1, 'green': 1, 'blue': 1}}}

        data = {}  # orderd by rows
        data['values'] = {}
        data['format'] = {}

        data['col_widths'] = [col['pixelSize'] for col in resp['sheets'][0]['data'][0]['columnMetadata']]

        rows = resp['sheets'][0]['data'][0]['rowData']
        for i, row in enumerate(rows):
            cell_vals = []
            cell_fmt = []
            for cell in row['values']:
                try:
                    cell_vals.append(cell['formattedValue'])
                except KeyError:
                    cell_vals.append(default_val)

                try:
                    cell_fmt.append(cell['effectiveFormat'])
                except KeyError:
                    cell_fmt.append(default_fmt)

            data['values'][f'row{i}'] = fill_missing_cells(cell_vals, default_val)
            data['format'][f'row{i}'] = fill_missing_cells(cell_fmt, default_fmt)

        return data


    def get_spreadsheet(self, spreadsheet_id, cell_range, **kwargs) -> tuple:
        '''
        Retrieve google spreadsheet data to Pandas DataFrame

        Parameters
        ----------
        spreadsheet_id: str
            Google sheet ID, found in the spreadsheet's URL
        cell_range: str
            Range of cells to be extracted. Eg: "Sheet1!A2:J15"
        header_row: bool, default False
            Convert first row of cell_range to table column names

        Returns
        -------
        DataFrame containing values from google sheet
        '''
        header_row = kwargs.pop('header_row', True)

        if 'sheets' not in self.scope_types:
            raise AttributeError('Incorrect api scope')
        # Call the Sheets API
        service = self._service_connect('sheets')
        full_resp = service.spreadsheets().get(spreadsheetId=spreadsheet_id, ranges=cell_range,
                                          includeGridData=True).execute()

        sheet_data = self._build_table(full_resp)

        if header_row:
            df = pd.DataFrame.from_dict(sheet_data['values'][1:], columns=sheet_data['values'][0], orient='index')
        else:
            df = pd.DataFrame.from_dict(sheet_data['values'], orient='index')

        fmt_df = pd.DataFrame.from_dict(sheet_data['format'], orient='index')

        metadata = {}
        metadata['fmt_df'] = fmt_df
        metadata['col_widths'] = sheet_data['col_widths']

        return df, metadata






class GoogleCalendar(GoogleService):
    def __init__(self, SCOPES, api_credentials, auth_dir=None):
        super().__init__(SCOPES, api_credentials, auth_dir=auth_dir)

    def get_calendar_ids(self, output=False) -> dict:
        '''
        Return a dictionary of user's calendar names and IDs.

        Parameters
        ----------
        output: bool, default False
            Print calendar name:ID pairs to console.

        Returns
        -------
        dict
        '''
        if 'calendar' not in self.scope_types:
            raise AttributeError('Incorrect api scope')

        service = self._service_connect('calendar')

        page_token = None
        name_ids = {}
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                name = calendar_list_entry['summary']
                id = calendar_list_entry['id']
                name_ids[name] = id
                if output:
                    print(f'{name} ---> {id}')
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

        return name_ids


    def get_calendar_events(self, cal_id='primary', start=None, end=None) -> list:
        '''
        Retrieve a list of calendar events stored as dictionaries

        Parameters
        ----------
        cal_id: str, default 'primary'
            Google calendar id, identified using 'get_calendar_ids' method
        start: datetime, optional
            Datetime in UTC isoformat. Defaults to 'now'.
            Example: datetime.utcnow().isoformat() + 'Z'
        end: datetime, optional
            Same format as 'start'.
            Must come after 'start', or after *now* if 'start' not specified.

        Returns
        -------
        List of dictionaries
        '''
        if 'calendar' not in self.scope_types:
            raise AttributeError('Incorrect api scope')

        if start is None:
            start = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

        service = self._service_connect('calendar')
        # Call the Calendar API
        events_result = service.events().list(calendarId=cal_id, timeMin=start,
                                              timeMax=end, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        return events






if __name__ == '__main__':
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/spreadsheets.readonly']
    cal_api_creds = 'py_general_creds.json'


    # Gcal._get_calendar_ids()

    # tu_timetable = '8r63unklasvr8dgcjenfm9odh2ptkk46@import.calendar.google.com'
    # events = Gcal.get_calendar(tu_timetable)
    # print(events)






