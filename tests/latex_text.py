#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: latex_text
project: LuigiPyTools
date: 5/24/2020
author: lmaio
"""

import pandas as pd
from LuigiPyTools import LatexPandas



def test_latex():

    dummy_df = pd.read_csv('./data/dummy_data.csv')
    LP = LatexPandas(dummy_df)
    LP.gen_tex_table(fname='test_out.tex', caption='test_table')


    pass


if __name__ == '__main__':
    test_latex()