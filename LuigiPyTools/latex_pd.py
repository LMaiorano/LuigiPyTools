#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: latex_pd
project: DSE-Mars-Reveal
date: 5/18/2020
author: lmaio
"""
import pandas as pd
import numpy as np

class LatexPandas():
    def __init__(self, dataframe, col_width=45):
        self.max_col_width = col_width
        self.df = dataframe
        self.df.fillna('', inplace=True)
        self.df = self.df.applymap(self.make_sub_table)


    def fix_chars(self, s, charset=('&', '$', '%')):
        for char in charset:
            s = s.replace(char, '\\'+char)
        return s

    def make_sub_table(self, s):
        s = self.fix_chars(s)
        if len(s) > self.max_col_width:
            words = s.split(' ')
            len_w = [len(word)+1 for word in words]
            len_aft_w = np.cumsum(len_w)
            b = len_aft_w % self.max_col_width
            c = np.where((b[1:] - b[:-1]) < 0)

            break_idx = len_aft_w[c].tolist()

            ext = 0
            for i in break_idx:
                i += ext
                s = s[:i] + '\\\\' + s[i:]
                ext += 2

            # Wrap with table header
            tab_st = '\\begin{tabular}[c]{@{}c@{}}'
            tab_end = '\\end{tabular}'

            s = tab_st + s + tab_end
        return s

    def save_tex(self, subsection_name, fname, subsec=True):
        with open(fname, 'w') as tf:
            if subsec:
                tf.write('\\subsection*{' + subsection_name + '}\n')
            else:
                tf.write('\\section*{' + subsection_name + '}\n')
        self.tex_table(caption=subsection_name, fname=fname)

    def tex_table(self, caption, fname, label=None, col_form='lcr', header=True):
        if label is None:
            label = 'tab:'+caption.replace(' ', '')[:10]
        else:
            label = 'tab:'+label
        if col_form == 'lcr':
            col_form = 'l' + 'c'*len(self.df.columns) + 'r'
        elif len(col_form) == 1:
            col_form = col_form*len(self.df.columns)
        with open(fname, 'w') as tf:
            with pd.option_context("max_colwidth", 1000):
                tf.write('\\begin{table}[H]\n\\centering \n\\caption{'+caption+'}\\label{'+label+'} \n')
                tf.write('\\resizebox{\\textwidth}{!}{\n')
                tf.write(self.df.to_latex(float_format="%.3f", escape=False, index=False,
                                          column_format=col_form, header=header))
                tf.write('}\n\\end{table}')