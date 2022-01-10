#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 2021

Copyright (c) 2021 Deutsche Gesellschaft für Cybersicherheit mbH & Co. KG

@author Merlin Mittelbach

{module docstring goes here}
"""
from pathlib import Path
try:
    from xml.etree.cElementTree import parse as parse_xml
except ModuleNotFoundError:
    from xml.etree.ElementTree import parse as parse_xml
from action.reports import JESTJunitXML, PytestJunitXML
import action.reports


def test_junit():
    action.reports.ROOTDIR = Path(
        "/home/mmittelb/Projects/stolen-api-services/"
    )
    with open("data/test/junit-jest.xml") as file_handler:
        junit = JESTJunitXML.from_file(file_handler)
    with open("data/test/junit-jest.xml") as file_handler:
        xml = parse_xml(file_handler)
    assert junit.start_time != junit.end_time
    assert junit.get_summary() == \
        '655 tests in 230.708s: 333 failures, 0 errors, 0 skipped'
    assert junit.title == 'jest tests'
    check_run_output = junit.create_check_run_output()
    assert check_run_output.summary == junit.get_summary()
    assert len(check_run_output.annotations) == sum([
        len(testcase.findall("./*"))
        for testcase in xml.findall(".//testcase")
    ])


def test_pytest():
    action.reports.ROOTDIR = Path(
        "/home/mmittelb/Projects/ci-action/"
    )
    with open("data/test/junit-pytest.xml") as file_handler:
        junit = PytestJunitXML.from_file(file_handler)
    assert junit.start_time != junit.end_time
    assert junit.get_summary() == \
        '11 tests in 0.075s: 1 failures, 0 errors, 0 skipped'
    assert junit.title == 'pytest tests'
    check_run_output = junit.create_check_run_output()
    assert check_run_output.summary == junit.get_summary()
    assert len(check_run_output.annotations) == 1
    assert check_run_output.annotations[0]["path"] == "tests/test_reports.py"
    assert check_run_output.annotations[0]["start_line"] == 16
