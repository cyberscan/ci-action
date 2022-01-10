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

from .reports import JESTJunitXML, PytestJunitXML
from .coverage import JestCoverageJsonSummaryParser, PythonCoverageParser

from pprint import pprint

SUPPORTED_LANGUAGES = [
    "python",
    "javascript"
]


def main(language, github_token):
    github = Github(github_token)
    commit_hash = environ["GITHUB_SHA"]
    repo = github.get_repo(environ["GITHUB_REPOSITORY"])
    with open(environ["GITHUB_EVENT_PATH"]) as filehandler:
        event_dict = jsonload(filehandler)

    if language == "javascript":
        with open("junit.xml") as junit_file:
            junit = JESTJunitXML.from_file(junit_file)
        with open("coverage.json") as cov_file:
            coverage = JestCoverageJsonSummaryParser()
    elif language == "python":
        with open("junit.xml") as junit_file:
            junit = PytestJunitXML.from_file(junit_file)
        # with open("coverage.json") as cov_file:
        #     coverage = PythonCoverageParser()
        #     coverage.parse(cov_file)
        with open("coverage.txt") as cov_file:
            coverage = cov_file.read()
    else:
        raise ArgumentError("Unknown language.")

    # upload PR Check
    print(commit_hash)
    pprint(event_dict)
    print(repo.create_check_run(**junit.create_check_run(commit_hash).to_dict()))
    issue = repo.get_issue(event_dict["pull_request"]["number"])
    issue.create_comment(f"```\n{coverage}```")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "language", choices=SUPPORTED_LANGUAGES,
        help="Select language."
    )
    parser.add_argument("github_token", help="Github token for API connection")
    args = parser.parse_args()
    main(args.language, args.github_token)
