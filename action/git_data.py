#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 2021

Copyright (c) 2021 Deutsche Gesellschaft für Cybersicherheit mbH & Co. KG

@author Merlin Mittelbach

github data classes
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class BaseGitData:
    def to_dict(self) -> Dict[str, Any]:
        return dict([
            (key, val)
            for key, val in vars(self).items()
            if val is not None
        ])


@dataclass
class CheckRunAnnotation(BaseGitData):
    """Adds information from your analysis to specific lines of code.
    Annotations are visible on GitHub in the Checks and Files changed tab of
    the pull request. The Checks API limits the number of annotations to a
    maximum of 50 per API request. To create more than 50 annotations, you have
    to make multiple requests to the Update a check run endpoint. Each time you
    update the check run, annotations are appended to the list of annotations
    that already exist for the check run. For details about how you can view
    annotations on GitHub, see "About status checks". See the annotations
    object description for details about how to use this parameter.
    Ref: https://docs.github.com/en/rest/reference/checks#create-a-check-run

    Args:
        path (str): The path of the file to add an annotation to.
            For example, assets/css/main.css.
        start_line (int): The start line of the annotation.
        end_line (int): The end line of the annotation.
        start_column (Optional[int]): The start column of the annotation.
            Annotations only support start_column and end_column on the same
            line. Omit this parameter if start_line and end_line have different
            values.
        end_column (Optional[int]): The end column of the annotation.
            Annotations only support start_column and end_column on the same
            line. Omit this parameter if start_line and end_line have different
            values.
        annotation_level (str): The level of the annotation.
            Can be one of notice, warning, or failure.
        message (str): A short description of the feedback for these lines of
            code. The maximum size is 64 KB.
        title (Optional[str]): The title that represents the annotation.
            The maximum size is 255 characters.
        raw_details (Optional[str]): Details about this annotation.
            The maximum size is 64 KB.
    """
    path: str
    start_line: int
    end_line: int
    annotation_level: str
    message: str
    start_column: Optional[int] = None
    end_column: Optional[int] = None
    title: Optional[str] = None
    raw_details: Optional[str] = None

    def __post_init__(self):
        assert self.annotation_level in ["notice", "warning", "failure"]


@dataclass
class CheckRunOutput(BaseGitData):
    """Check runs can accept a variety of data in the output object, including
    a title and summary and can optionally provide descriptive details about
    the run. See the output object description.
    Ref: https://docs.github.com/en/rest/reference/checks#create-a-check-run

    Args:
        title (str): The title of the check run.
        summary (str): The summary of the check run.
            This parameter supports Markdown.
        text (Optional[str]): The details of the check run.
            This parameter supports Markdown.
        annotations (List[CheckRunAnnotation]):
            Empty check run annotation list.
    """
    title: str
    summary: str
    text: Optional[str] = None
    annotations: List[CheckRunAnnotation] = field(
        init=False, default_factory=list
    )

    def add_annotation(self, annotation: CheckRunAnnotation) -> None:
        """add dict representation of check run annotation to internal
        annotations list

        Args:
            annotation (CheckRunAnnotation): annotation instance to add
        """
        if len(self.annotations) < 50:
            self.annotations.append(annotation.to_dict())


@dataclass
class CheckRun(BaseGitData):
    """A check run is an individual test that is part of a check suite.
    Each run includes a status and conclusion.

    Args:
        name (str): The name of the check. For example, "code-coverage".
        head_sha (str): The SHA of the commit.
        status (str): The current status. Can be one of queued, in_progress,
            or completed.
        conclusion (str): The final conclusion of the check.
            Can be one of action_required, cancelled, failure, neutral,
            success, skipped, stale, or timed_out. When the conclusion is
            action_required, additional details should be provided on the
            site specified by details_url.
            Note: Providing conclusion will automatically set the status
                parameter to completed. You cannot change a check run
                conclusion to stale, only GitHub can set this.
        started_at (str): The time that the check run began.
            This is a timestamp in ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ.
        completed_at (str): The time the check completed.
            This is a timestamp in ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ.
        details_url (Optional[str]): The URL of the integrator's site that has
            the full details of the check. If the integrator does not provide
            this, then the homepage of the GitHub app is used.
        external_id (Optional[str]): A reference for the run on the
            integrator's system.
        output (Dict[str, Any]): dict representation of CheckRunOutput instance
    """
    name: str
    head_sha: str
    status: str
    conclusion: str
    started_at: str
    completed_at: str
    details_url: Optional[str] = None
    external_id: Optional[str] = None
    output: Dict[str, Any] = None

    def add_output(self, output: CheckRunOutput) -> None:
        self.output = output.to_dict()
