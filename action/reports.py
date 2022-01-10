#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 2021

Copyright (c) 2021 Deutsche Gesellschaft für Cybersicherheit mbH & Co. KG

@author Merlin Mittelbach

collection of test reports
"""

from __future__ import annotations
from datetime import datetime, timedelta
from logging import getLogger
from pathlib import Path
from re import compile, MULTILINE
from typing import TextIO
try:
    from xml.etree.cElementTree import parse as parse_xml, ElementTree, Element
except ModuleNotFoundError:
    from xml.etree.ElementTree import parse as parse_xml, ElementTree, Element

from .git_data import CheckRun, CheckRunAnnotation, CheckRunOutput

logger = getLogger(__file__)
ROOTDIR = Path.cwd()


class UnknownTestSuiteException(Exception):
    """Test suite unknown.
    """


class JUnitXML:
    """JUnit XML test result class

    Args:
        xml (ElementTree): JUnit XML
    """
    root: Element
    title: str
    start_time: datetime = None
    end_time: datetime = None
    ntests: int
    nfailures: int
    nerrors: int
    nskipped: int
    time: float

    def __init__(self) -> None:
        raise NotImplementedError()

    def create_check_run_output(self) -> None:
        raise NotImplementedError()

    def create_check_run(self, commit_hash: str) -> CheckRun:
        check_run = CheckRun(
            name="unit-tests",
            head_sha=commit_hash,
            status="completed",
            conclusion="failure"
            if self.nfailures > 0 or self.nerrors > 0
            else "success",
            started_at=self.start_time,
            completed_at=self.end_time
        )
        check_run.add_output(self.create_check_run_output())
        return check_run

    def get_summary(self) -> str:
        return f"{self.ntests} tests in {self.time}s: " + \
            f"{self.nfailures} failures, " + \
            f"{self.nerrors} errors, {self.nskipped} skipped"

    @classmethod
    def from_file(cls, file_handle: TextIO) -> JUnitXML:
        xml = parse_xml(file_handle)
        assert xml.getroot().tag == "testsuites", \
            "root element of JUnit XML should be testsuites"
        return cls(xml)


class JESTJunitXML(JUnitXML):
    jest_message_pattern = compile(r"(.*)\n\s+at", MULTILINE)
    jest_path_pattern = compile(r"(/\S+):(\d+):(\d+)")

    def __init__(self, xml: ElementTree) -> None:
        self.root = xml.getroot()

        assert self.root.attrib.get("name") == "jest tests"
        logger.info("JEST JUnit XML deteted.")

        self.title = "jest tests"
        self.start_time = self.end_time = datetime.now()
        self.ntests = int(self.root.attrib.get("tests"))
        self.time = float(self.root.attrib.get("time"))
        self.nfailures = int(self.root.attrib.get("failures"))
        self.nerrors = int(self.root.attrib.get("errors"))
        self.nskipped = 0

        # jest is grouping tests in suites
        # to get skipped sum and starting timestamp we have to
        # iter through them
        for test_suite in self.root.findall("./testsuite"):
            timestamp = datetime.fromisoformat(
                test_suite.attrib.get("timestamp"))
            if timestamp < self.start_time:
                self.start_time = timestamp
                self.end_time = self.start_time + timedelta(seconds=self.time)
            self.nskipped += int(test_suite.get("skipped"))

    def create_check_run_output(self) -> CheckRunOutput:
        check_run_output = CheckRunOutput(
            title=self.title,
            summary=self.get_summary()
        )
        for test_case in self.root.findall(".//testcase"):
            name = test_case.attrib.get("name", "no name detected")
            time = test_case.attrib.get("time", "-")
            for result in test_case.findall("./*"):
                message = "Failed to match message text."
                path = "nofilematched"
                line = 1
                match = self.jest_message_pattern.search(result.text)
                if match is not None:
                    message = match[1]
                for filename, line_tmp, _ \
                        in self.jest_path_pattern.findall(result.text):
                    try:
                        path_tmp = str(Path(filename).relative_to(ROOTDIR))
                        if "node_modules" not in path_tmp:
                            path = path_tmp
                            line = int(line_tmp)
                            break
                    except ValueError:
                        continue

                check_run_output.add_annotation(
                    CheckRunAnnotation(
                        title="%s (%ss)" % (name, time),
                        start_line=line,
                        end_line=line,
                        path=path,
                        message=message,
                        annotation_level="warning"
                        if result.tag == "failure"
                        else "failure",
                        raw_details=result.text
                    )
                )
        return check_run_output


class PytestJunitXML(JUnitXML):
    pytest_path_pattern = compile(r"^(\w\S*.py):(\d+)", MULTILINE)

    def __init__(self, xml: ElementTree) -> None:
        self.root = xml.getroot()

        assert self.root.attrib.get("name") is None
        assert len(self.root.findall("./testsuite")) == 1
        assert self.root.find("./testsuite").attrib.get("name") == "pytest"

        self.root = self.root.find("./testsuite")
        self.title = "pytest tests"
        self.ntests = int(self.root.attrib.get("tests"))
        self.time = float(self.root.attrib.get("time"))
        self.nfailures = int(self.root.attrib.get("failures"))
        self.nerrors = int(self.root.attrib.get("errors"))
        self.nskipped = int(self.root.attrib.get("skipped"))
        self.start_time = datetime.fromisoformat(
            self.root.attrib.get("timestamp")
        )
        self.end_time = self.start_time + timedelta(seconds=self.time)

    def create_check_run_output(self) -> CheckRunOutput:
        check_run_output = CheckRunOutput(
            title=self.title,
            summary=self.get_summary()
        )
        for test_case in self.root.findall("./testcase"):
            name = test_case.attrib.get("name", "no name detected")
            time = test_case.attrib.get("time", "-")
            for result in test_case.findall("./*"):
                message = result.attrib.get(
                    "message", "Failed to match message text."
                )
                match = self.pytest_path_pattern.search(result.text)
                if match is None:
                    path = "nofilematched"
                    line = 1
                else:
                    path = match[1]
                    line = int(match[2])

                check_run_output.add_annotation(
                    CheckRunAnnotation(
                        title="%s (%ss)" % (name, time),
                        start_line=line,
                        end_line=line,
                        path=path,
                        message=message,
                        annotation_level="warning"
                        if result.tag == "failure"
                        else "failure",
                        raw_details=result.text
                    )
                )
        return check_run_output
