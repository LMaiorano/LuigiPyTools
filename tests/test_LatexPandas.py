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
from LuigiPyTools import LatexPandas, GooglePy
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

        print('the one i want')

        G = GooglePy(self.SCOPES, self.gen_api_creds)
        df = G.get_spreadsheet(id, data_range, header_row=False, dev=False)[0]

        LP = LatexPandas(df, col_width=20)


        filename = os.path.join(self.test_output_dir, name.replace(' ', '_') + '.tex')
        LP.gen_tex_table(filename, name, col_form='c', header=False)
        LP.group_table_rows(filename)

        assert filecmp.cmp(os.path.join(os.path.dirname(__file__), 'data', 'AOCS_N2_chart_ref.tex'),
                           filename,
                           shallow=False)


    @unittest.expectedFailure
    def test_longtable_fixedwidth(self):
        header = False
        small = True

        id = '1KW31J20B3s-nx_UxVzlym19yM6-gAFdctSvjBQq9yi8'
        name = 'System N2 chart'
        data_range = 'Lander N2 Chart!B2:I9'

        G = GooglePy(self.SCOPES, self.gen_api_creds)
        df, fmt, widths = G.get_spreadsheet(id, data_range, header_row=False, dev=True)[1]

        rgb_tex = fmt.applymap(rgb_cell)  # Extract RGB values to df of tex cellcolor commands

        tex_col_format = tex_col_format_gen(widths, fmt)

        LP = LatexPandas(df, col_width=col_width)
        LP._df = rgb_tex.apply(lambda x: x + LP._df[x.name])

        filename = os.path.join(self.LOCAL_DIR, name.replace(' ', '_') + '.tex')
        LP.gen_tex_table_v2(filename, name, col_form=tex_col_format, header=header, longtable=True, small=small)

        LP.group_table_rows(filename)

