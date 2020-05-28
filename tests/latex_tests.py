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
from LuigiPyTools import LatexPandas, GooglePy


def test_latex():

    dummy_df = pd.read_csv('./data/dummy_data.csv')
    LP = LatexPandas(dummy_df)
    LP.gen_tex_table(fname='test_out.tex', caption='test_table')


def test_gsheets_latex():
    name = 'AOCS N2 chart'
    id = '1rCUwaoJuMDvknxGJNu3-IufDKPDW8PX6VdqtPscUsnM'
    data_range = 'AOCS!A1:K11'

    LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/calendar.readonly']
    gen_api_creds = os.path.join(os.path.dirname(__file__), 'py_general_creds.json')

    G = GooglePy(SCOPES, gen_api_creds)
    df = G.get_spreadsheet(id, data_range, header_row=False)

    LP = LatexPandas(df, col_width=20)

    filename = os.path.join(LOCAL_DIR, name.replace(' ', '_') + '.tex')
    LP.gen_tex_table(filename, name, col_form='c', header=False)
    LP.group_table_rows(filename)


if __name__ == '__main__':
    # test_latex()
    # test_gsheets_latex()
    pass