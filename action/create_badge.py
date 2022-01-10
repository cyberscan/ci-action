#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 02 2021

Copyright (c) 2021 Deutsche Gesellschaft für Cybersicherheit mbH & Co. KG

@author Merlin Mittelbach

main routines
"""
from argparse import ArgumentParser, ArgumentTypeError
from logging import DEBUG, INFO, Formatter, getLogger, StreamHandler
from pathlib import Path
from .badges import CoverageBadge

from .coverage import REGISTERED_PARSERS, CoverageReporter
from . import ShieldIO6Color

logger = getLogger(__file__)


class ExisitingPath(Path):
    def __init__(self) -> None:
        super().__init__()
        if not self.exists():
            raise ArgumentTypeError("File does not exist.")


def setup_logging(debug: bool) -> None:
    logger = getLogger()
    handler = StreamHandler()
    Formatter()
    handler.setFormatter(
        Formatter(
            "[%(asctime)s] %(levelname)s "
            "[%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            datefmt="%d/%b/%Y %H:%M:%S",
        )
    )
    logger.addHandler(handler)
    logger.setLevel(DEBUG if debug else INFO)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("-d", "--debug", action="store_true",
                        help="activate debug log")
    parser.add_argument(
        "-m", "--metric",
        choices=["statements", "lines", "branches", "functions"],
        default="lines",
        help="Choose which metric is used for coverage calculation. "
        "Default is 'lines'."
    )
    parser.add_argument(
        "-t", "--thresholds", type=ShieldIO6Color,
        help="The badge displays a color palette consisting of 6 colors "
        "reaching from red to green. Choose the threshold of which color is "
        "displayed as a function of the relative coverage by specifing 5 "
        "ordered comma separated int values, with color[i] being displayed, "
        "if rel_coverage >= threshold[i]. Every relative coverage below last "
        "threshold is automatically the last color defined in COLORS (red). "
        "Default is '90,80,70,60,50'.",
        default="90,80,70,60,50"
    )
    parser.add_argument(
        "type", choices=REGISTERED_PARSERS.keys(),
        help=f"Select report type from {list(REGISTERED_PARSERS.keys())}."
    )
    parser.add_argument(
        "reportpath", type=Path, help="Select report file."
    )
    parser.add_argument(
        "badgepath", type=Path, help="Select badge output file."
    )
    args = parser.parse_args()

    setup_logging(args.debug)

    coverage_parser: CoverageReporter = REGISTERED_PARSERS[args.type]()
    with open(args.reportpath) as filehandler:
        coverage_parser.parse(filehandler)
    badge = CoverageBadge(
        coverage_parser.get_relative_coverage(args.metric),
        args.thresholds
    )
    with open(args.badgepath, "w") as filehandler:
        badge.dump(filehandler)
