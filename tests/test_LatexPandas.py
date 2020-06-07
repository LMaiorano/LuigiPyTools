#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: latex_text
project: LuigiPyTools
date: 5/24/2020
author: lmaio
"""

import pandas as pd
import os
import unittest
from LuigiPyTools import LatexPandas, GoogleSheets, GoogleCalendar
import filecmp
import shutil


class TestLatex(unittest.TestCase):
    def setUp(self) -> None:
        self.LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly',
                  'https://www.googleapis.com/auth/calendar.readonly']
        self.gen_api_creds = os.path.join(os.path.dirname(__file__), 'py_general_creds.json')

        self.test_output_dir = os.path.join(self.LOCAL_DIR, 'test_output')
        if not os.path.exists(self.test_output_dir):
            os.mkdir(self.test_output_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.test_output_dir)
        filecmp.clear_cache()


class BasicPandas(TestLatex):
    def test_latex(self):

        dummy_df = pd.read_csv('./data/dummy_data.csv')
        LP = LatexPandas(dummy_df)

        fileout = os.path.join(self.test_output_dir, 'test_out.tex')
        LP.gen_tex_table(fname=fileout, caption='test_table')

        assert filecmp.cmp(os.path.join(os.path.dirname(__file__), 'data', 'dummy_data_ref.tex'),
                           fileout,
                           shallow=False)


class SheetsDataframe(TestLatex):
    def test_standard_table(self):
        name = 'AOCS N2 chart'
        id = '1KW31J20B3s-nx_UxVzlym19yM6-gAFdctSvjBQq9yi8'
        data_range = 'AOCS!A1:K11'

        G = GoogleSheets(self.SCOPES, self.gen_api_creds)
        df = G.get_spreadsheet(id, data_range, header_row=False, dev=False)[0]

        LP = LatexPandas(df, col_width=20)


        filename = os.path.join(self.test_output_dir, name.replace(' ', '_') + '.tex')
        LP.gen_tex_table(filename, name, col_form='c', header=False)
        LP.group_table_rows(filename)

        assert filecmp.cmp(os.path.join(os.path.dirname(__file__), 'data', 'AOCS_N2_chart_ref.tex'),
                           filename,
                           shallow=False)



    def test_gsheet_formatting(self):
        header = False
        small = True

        id = '1KW31J20B3s-nx_UxVzlym19yM6-gAFdctSvjBQq9yi8'
        name = 'Formatted Sys N2 Chart'
        data_range = 'Lander N2 Chart!B2:I9'

        G = GoogleSheets(self.SCOPES, self.gen_api_creds)
        df, formatting = G.get_spreadsheet(id, data_range, header_row=False)

        LP = LatexPandas(df, metadata=formatting)


        filename = os.path.join(self.test_output_dir, name.replace(' ', '_') + '.tex')
        LP.gen_tex_table(filename, name, header=header, longtable=True, small=small)

        LP.group_table_rows(filename)

        assert filecmp.cmp(os.path.join(os.path.dirname(__file__), 'data', 'Formatted_Sys_N2_Chart_ref.tex'),
                           filename, shallow=False)
