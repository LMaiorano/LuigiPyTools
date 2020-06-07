#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: latex_pd
project: DSE-Mars-Reveal
date: 5/18/2020
author: lmaio

TODO:
    - allow individual column widths
    - add sub-table handler for \n

"""
import pandas as pd
import numpy as np
import ntpath

class LatexPandas():
    def __init__(self, dataframe, col_width=45):
        '''Convert Pandas Dataframe to latex table

        Parameters
        ----------
        dataframe: pd.Dataframe
            Pandas DataFrame to convert
        col_width: int, default 45
            Max character width per column, equal for all columns
        '''
        self._max_col_width = col_width
        self._df = dataframe
        self._df.fillna('', inplace=True)
        self._df = self._df.applymap(self._fix_chars)

    def _fix_chars(self, s, charset=('&', '$', '%')):
        for char in charset:
            s = s.replace(char, '\\' + char)
            s = s.replace('\n', '')

        return s

    def _make_sub_table(self, s):
        # FIXME: recognize existing line breaks in a cell
        s = self._fix_chars(s)

        lines = s.split('\n')
        for idx, s in enumerate(lines):

            if len(s) > self._max_col_width:
                words = s.split(' ')
                len_w = [len(word) + 1 for word in words]
                len_aft_w = np.cumsum(len_w)
                b = len_aft_w % self._max_col_width
                c = np.where((b[1:] - b[:-1]) < 0)

                break_idx = len_aft_w[c].tolist()

                ext = 0
                for i in break_idx:
                    i += ext
                    s = s[:i] + '\\\\' + s[i:]
                    ext += 2

                lines[idx] = s

        # Wrap with table header
        tab_st = '\\begin{tabular}[c]{@{}c@{}}'
        tab_end = '\\end{tabular}'

        # recombine list of lines into single string, joining with breakline \\\\
        create_table = False
        sub_table = lines[0]
        for line in lines[1:]:
            sub_table += '\\\\'
            sub_table += line
            create_table = True

        if '\\\\' in sub_table:
            sub_table = tab_st + sub_table + tab_end

        return sub_table


    def gen_tex_table(self, fname, caption, label=None, col_form='lcr', header=True):
        '''Save pandas dataframe to *.tex file, for direct usage in LaTeX report

        Parameters
        ----------
        fname: str
            Filename to save, include path for other directory
        caption: str
            Table caption. Required.
        label: str, optional
            Latex table label for references. ie: 'tab:my-table'
        col_form: str, default 'lcr'
            Alignment pattern of columns. Default will center all middle columns,
            left-align leftmost column, and right-align rightmost column
        header: bool, default True
            Include column names

        Returns
        -------
        *.tex file containing table data

        '''
        self._df = self._df.applymap(self._make_sub_table)
        if label is None:
            label = 'tab:'+caption.replace(' ', '')[:10]

        if col_form == 'lcr':
            col_form = 'l' + 'c' * len(self._df.columns) + 'r'
        elif len(col_form) == 1:
            col_form = col_form*len(self._df.columns)

        comment_header = '% ---- Generated using LuigiPyTools.LatexPandas module ---- \n\n\n% Include the following line in preamble' \
                         ' to specify space between grouped rows in tables \n% \\newcommand{\\tableskip}{5pt} \n\n% To' \
                         ' include this table, use at the desired location in the document: \n' \
                         '% \\input{'+ntpath.basename(fname)+'}\n\n'

        with open(fname, 'w') as tf:
            with pd.option_context("max_colwidth", 1000):
                tf.write(comment_header)
                tf.write('\\begin{table}[H]\n\\centering \n\\caption{'+caption+'}\\label{'+label+'} \n')
                tf.write('\\resizebox{\\textwidth}{!}{\n')
                tf.write(self._df.to_latex(float_format="%.3f", escape=False, index=False,
                                           column_format=col_form, header=header))
                tf.write('}\n\\end{table}')

    def group_table_rows(self, fname):
        '''Applies \tableskip vertical space between rows in table.

        This removes the need for horizontal lines in table; conforming to the
        LateX booktabs table style. \tableskip can be defined globally in the LateX
        main.tex file for consistent usage throughout document.

        Parameters
        ----------
        fname: str
            Filename ending in .tex containing LateX table to modify. Must be generated
            using LatexPandas.gen_tex_table

        Returns
        -------
        Modifies existing *.tex file.
        '''
        with open(fname, 'r') as fin:
            lines = fin.readlines()

        tabletop = [i for i, s in enumerate(lines) if 'toprule' in s][0]
        for i, line in enumerate(lines):
            if i > tabletop:
                if '\\bottomrule' in line:
                    break
                else:
                    lines[i] = line + '\\addlinespace[\\tableskip]\n'

        with open(fname, 'w') as fout:
            fout.writelines(lines)


    def gen_tex_table_v2(self, fname, caption, label=None, col_form='lcr', header=True, small=True, longtable=False):
        comment_header = '% ---- Generated using LuigiPyTools.LatexPandas module ---- ' \
                         '\n\n\n% Include the following lines in preamble:' \
                         ' \n% \\usepackage{array}' \
                         ' \n% \\usepackage{ragged2e}' \
                         ' \n% \\usepackage{xcolor, colortbl}' \
                         ' \n% \\usepackage{xltabular}' \
                         ' \n% \\usepackage{longtable}' \
                         ' \n% \\usepackage[font=small,textfont=it,labelfont=bf]{caption}' \
                         '\n\n% \\newcolumntype{L}[1]{>{\\raggedright\\arraybackslash}p{#1}}' \
                         ' \n% \\newcolumntype{C}[1]{>{\\centering\\arraybackslash}p{#1}}' \
                         ' \n% \\newcolumntype{R}[1]{>{\\raggedleft\\arraybackslash}p{#1}}' \
                         ' \n% \\captionsetup{justification = centering}' \
                         ' \n% \\newcommand{\\tableskip}{5pt}' \
                         '\n\n% To include this table, use at the desired location in the document: ' \
                         ' \n% \\input{' + ntpath.basename(fname) + '}\n\n'

        if label is None:
            label = 'tab:'+caption.replace(' ', '')[:10]

        with open(fname, 'w') as tf:
            with pd.option_context("max_colwidth", 1000):
                tf.write(comment_header)
                if not longtable:
                    tf.write('\\begin{table}[H]\n')
                    if small:
                        tf.write('\\small\n')

                    tf.write('\\centering \n\\caption{' + caption + '}\\label{' + label + '} \n')
                tf.write(self._df.to_latex(float_format="%.3f", escape=False, index=False,
                                           column_format=col_form, header=header, longtable=longtable))
                if not longtable:
                    tf.write('\\end{table}')

        if longtable:
            self._longtable_modify(fname, caption, label, small=small)


    def _longtable_modify(self, fname, caption, label, small):
        with open(fname, 'r') as fin:
            lines = fin.readlines()

        for i, line in enumerate(lines):
            if '\\begin{longtable}' in line:
                if small:
                    line = '\\begin{small}\n' + line
                line += '\\caption{' + caption + '}\\label{' + label + '}\\\\ \n'
            if '\\end{longtable}' in line:
                line = '\\bottomrule\n' + line
                if small:
                    line += '\\end{small}'
            lines[i] = line

        with open(fname, 'w') as fout:
            fout.writelines(lines)