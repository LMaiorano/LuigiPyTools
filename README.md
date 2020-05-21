# LuigiPyTools


LuigiPyTools provides tools commonly used in engineering and course-related projects. It is intended simplify the use of common code and enable easy updates when new features are needed. Typical usage often looks like this:

    #!/usr/bin/env python

    import os
    import pandas as pd
    from LuigiPyTools import LatexPandas, GooglePy

    def main(sheet_id, data_range, col_width=45, name='gsheet_table'):
        LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        gen_api_creds = os.path.join(LOCAL_DIR, 'py_general_creds.json')

        G = GooglePy(SCOPES, gen_api_creds)
        values = G.get_spreadsheet(sheet_id, data_range)
        df = pd.DataFrame.from_records(values)

        LP = LatexPandas(df, col_width=col_width)

        filename = os.path.join(LOCAL_DIR, name.replace(' ','_') + '.tex')
        LP.tex_table(name, filename, col_form='c', header=False)


## Documentation
More to follow at a later time ...