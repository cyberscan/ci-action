#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 2021

Copyright (c) 2021 Deutsche Gesellschaft für Cybersicherheit mbH & Co. KG

@author Merlin Mittelbach

main procedure of action
"""
from argparse import ArgumentError, ArgumentParser
from github.MainClass import Github
from json import load as jsonload
from os import environ
from re import search as research, MULTILINE

from .reports import JESTJunitXML, PytestJunitXML
from .coverage import JestCoverageJsonSummaryParser, PythonCoverageParser

from pprint import pprint

SUPPORTED_LANGUAGES = [
    "python",
    "javascript"
]


def main(language, github_token):
    github = Github(github_token)
    repo = github.get_repo(environ["GITHUB_REPOSITORY"])
    with open(environ["GITHUB_EVENT_PATH"]) as filehandler:
        event_dict = jsonload(filehandler)
    if "after" in event_dict:
        commit_hash = event_dict["after"]
    else:
        commit_hash = environ["GITHUB_SHA"]

    if language == "javascript":
        with open("junit.xml") as junit_file:
            junit = JESTJunitXML.from_file(junit_file)
        with open("coverage/coverage-summary.json") as cov_file:
            coverage = JestCoverageJsonSummaryParser()
            coverage.parse(cov_file)
        with open("jest.txt") as rawfile:
            coverage_lines = research(
                r"(^-+\|[\w\W]*\|-+$)", rawfile.read(), MULTILINE
            )[1].split("\n")
            summary = "\n".join(coverage_lines[:4])
            details = "\n".join(coverage_lines[4:])

    elif language == "python":
        with open("junit.xml") as junit_file:
            junit = PytestJunitXML.from_file(junit_file)
        with open("coverage.json") as cov_file:
            coverage = PythonCoverageParser()
            coverage.parse(cov_file)
        with open("coverage.txt") as cov_file:
            coverage_lines = cov_file.read().split("\n")
            summary = "\n".join(coverage_lines[:2] + coverage_lines[-2:-1])
            details = "\n".join(coverage_lines[2:-2])
    else:
        raise ArgumentError("Unknown language.")

    print(
        "::set-output name=coverage::%d" % (
            coverage.get_relative_coverage('statements')
        )
    )
    # upload PR Check
    check_run = junit.create_check_run(commit_hash)
    print(
        repo.create_check_run(**check_run.to_dict())
    )
    pprint(check_run.to_dict())
    pprint(event_dict)
    if "pull_request" in event_dict:
        coverage_raw = "<details><summary><link>expand</link>\n" + \
            f"<pre>{summary}</pre></summary><pre>{details}</pre></details>"
        issue = repo.get_issue(event_dict["pull_request"]["number"])
        issue.create_comment(coverage_raw)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "language", choices=SUPPORTED_LANGUAGES,
        help="Select language."
    )
    parser.add_argument("github_token", help="Github token for API connection")
    args = parser.parse_args()
    main(args.language, args.github_token)
