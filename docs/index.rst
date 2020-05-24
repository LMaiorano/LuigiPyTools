.. LuigiPyTools documentation master file, created by
   sphinx-quickstart on Sat May 23 16:08:27 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to LuigiPyTools' documentation!
========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



LuigiPyTools
============

LuigiPyTools provides tools commonly used in engineering and course-related projects. It is intended simplify the use of common code and enable easy updates when new features are needed.


Usage
-----

Basic usage example::

   #!/usr/bin/env python

   from LuigiPyTools import LatexPandas, GooglePy


   SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
   gen_api_creds = 'py_general_creds.json'

   G = GooglePy(SCOPES, gen_api_creds)
   df = G.get_spreadsheet(sheet_id, data_range)

   LP = LatexPandas(df, col_width=col_width)
   LP.tex_table('Example Table', 'GoogleSheet.tex')


Features
--------

- Extract Google sheets to python
- Read Google Calendar events
- Convert Pandas DataFrame to LaTeX formatted tables


Installation
------------

Install LuigiPyTools by running:

    install LuigiPyTools


License
-------

The project is licensed under the MIT license.