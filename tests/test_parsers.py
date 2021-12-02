#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 02 2021

Copyright (c) 2021 Deutsche Gesellschaft für Cybersicherheit mbH & Co. KG

@author Merlin Mittelbach

test parsers
"""
from argparse import ArgumentTypeError
from pytest import raises
from pytest import mark

from action.parsers import JestCoverageJsonSummaryParser, Parser, PythonCoverageParser


def test_base_class():
    with raises(TypeError):
        parser = Parser()

    class TestParser(Parser):
        pass

    with raises(TypeError):
        parser = TestParser()

    class TestParser2(Parser):
        def parse(_):
            return None

    assert TestParser2()


@mark.parametrize(
    "metric, expected_cov",
    [
        ("lines", 56),
        ("statements", 57),
        ("branches", 17),
        ("functions", 30),
    ]
)
def test_jest_coverage_json_summary_parser(metric, expected_cov):
    with raises(ArgumentTypeError):
        parser = JestCoverageJsonSummaryParser("bla")
    parser = JestCoverageJsonSummaryParser(metric)
    assert parser.metric == metric
    with open("data/test/jest-coverage-summary.json") as fh:
        parser.parse(fh)
    assert parser.get_relative_coverage() == expected_cov


@mark.parametrize(
    "metric, expected_cov",
    [
        ("lines", 92),
        ("statements", 93),
        ("branches", 100),
    ]
)
def test_python_coverage_parser(metric, expected_cov):
    with raises(ArgumentTypeError):
        parser = PythonCoverageParser("functions")
    parser = PythonCoverageParser(metric)
    assert parser.metric == metric
    with open("data/test/python-coverage.json") as fh:
        parser.parse(fh)
    assert parser.get_relative_coverage() == expected_cov
