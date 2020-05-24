#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: google_api
project: DSE-Mars-Reveal
date: 5/18/2020
author: lmaio



TODO:
    - Add 'auth/' dir detection or creation for saving creds and tokens

"""

from datetime import datetime
import pickle
import os.path
import pandas as pd
import json
import os
from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import warnings


class GooglePy():
    '''
    Description
    -----------
    Interface with Google sheets and calendars

    '''
    def __init__(self, SCOPES, api_credentials):
        '''

        Parameters
        ----------
        SCOPES: list of str
            All scopes used for this program. See Google API documentation.
            Must match authorized scopes of provided api_credentials
        api_credentials: str
            Filepath to api client credentials json
        '''
        self._scopes = SCOPES
        '''list of str: Scopes for API call'''
        self.__creds_file = api_credentials
        self._scope_type()

    def _create_auth_dir(self):
        '''Create directory for storing tokens and authentication'''
        if not os.path.exists('auth'):
            os.makedirs('auth')
            warnings.warn('Add auth/ to your .gitignore for security purposes')

    def _scope_type(self):
        self.scope_types = []
        for scope in self._scopes:
            if 'spreadsheets' in scope:
                self.scope_types.append('sheets')
            if 'calendar' in scope:
                self.scope_types.append('calendar')

    def _service_connect(self, type):
        '''
        Connects to appropriate google api service

        Parameters
        ----------
        type: str
            'calendar' or 'sheets'

        Returns
        -------

        '''
        creds = None
        TOKEN_DIR = os.path.dirname(self.__creds_file)
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token_file = os.path.join(TOKEN_DIR, 'token.pickle')
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


    def _api_spreadsheet_values(self, spreadsheet_id, range_name):
        if 'sheets' not in self.scope_types:
            raise AttributeError('Incorrect api scope')
        # Call the Sheets API
        service = self._service_connect('sheets')
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                    range=range_name).execute()
        values = result.get('values', [])

        # full = service.spreadsheets().get(spreadsheetId=spreadsheet_id, ranges=range_name, includeGridData=True).execute()

        return values

    def get_spreadsheet(self, spreadsheet_id, cell_range, header_row=False) -> pd.DataFrame:
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

        values = self._api_spreadsheet_values(spreadsheet_id, cell_range)
        if header_row:
            df = pd.DataFrame.from_records(values[1:], columns=values[0])
        else:
            df = pd.DataFrame.from_records(values)
        return df

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

    Gcal = GooglePy(SCOPES, cal_api_creds)
    # Gcal._get_calendar_ids()

    # tu_timetable = '8r63unklasvr8dgcjenfm9odh2ptkk46@import.calendar.google.com'
    # events = Gcal.get_calendar(tu_timetable)
    # print(events)






