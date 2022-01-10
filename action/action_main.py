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
from os import environ

from .reports import JESTJunitXML, PytestJunitXML
from .coverage import JestCoverageJsonSummaryParser, PythonCoverageParser

SUPPORTED_LANGUAGES = [
    "python",
    "javascript"
]


def main(language, github_token):
    github = Github(github_token)
    commit_hash = environ["GITHUB_SHA"]
    repo = github.get_repo(environ["GITHUB_REPOSITORY"])

    if language == "javascript":
        with open("junit.xml") as junit_file:
            junit = JESTJunitXML.from_file(junit_file)
        with open("coverage.json") as cov_file:
            coverage = JestCoverageJsonSummaryParser()
            coverage.parse(cov_file)
    elif language == "python":
        with open("junit.xml") as junit_file:
            junit = PytestJunitXML.from_file(junit_file)
        with open("coverage.json") as cov_file:
            coverage = PythonCoverageParser()
            coverage.parse(cov_file)
    else:
        raise ArgumentError("Unknown language.")

    # upload PR Check
    repo.create_check_run(junit.create_check_run(commit_hash))


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "language", choices=SUPPORTED_LANGUAGES,
        help="Select language."
    )
    parser.add_argument("github_token", help="Github token for API connection")
    args = parser.parse_args()
    main(args.language, args.github_token)
