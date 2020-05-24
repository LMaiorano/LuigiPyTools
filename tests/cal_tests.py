#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: cal_tests
project: LuigiPyTools
date: 5/23/2020
author: lmaio
"""

import os
from LuigiPyTools import GooglePy

def test_calendar_ids():
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    cal_api_creds = os.path.join(os.path.dirname(__file__), 'py_general_creds.json')

    G = GooglePy(SCOPES, cal_api_creds)
    ids = G.get_calendar_ids(output=True)
    events = G.get_calendar_events()
    print(events)


if __name__ == '__main__':
    test_calendar_ids()