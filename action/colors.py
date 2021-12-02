#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 02 2021

Copyright (c) 2021 Deutsche Gesellschaft für Cybersicherheit mbH & Co. KG

@author Merlin Mittelbach

color palettes
"""
from argparse import ArgumentTypeError
from dataclasses import InitVar, dataclass, field
from typing import ClassVar, List, Tuple


@dataclass
class BadgeColor:
    thresholds: List[int] = field(init=False)
    palette: ClassVar[List[Tuple[str, str]]] = field(
        repr=False, default=list()
    )
    thresholds_str: InitVar[str]

    def __post_init__(self, thresholds_str: str):
        try:
            thresholds = [
                int(threshold)
                for threshold in thresholds_str.split(",")
            ]
        except ValueError:
            raise ArgumentTypeError(
                "Comma seperated integers expected."
            )
        if len(thresholds) != len(self.palette)-1:
            raise ArgumentTypeError(
                "Input of length 5 expected."
            )
        last_i = 100
        for i in thresholds+[0, ]:
            if i > last_i:
                raise ArgumentTypeError(
                    "Threshold values expected to be between 0 and 100 "
                    "+ in descending order."
                )
            else:
                last_i = i
        self.thresholds = thresholds

    def get_color(self, relative_coverage: int) -> Tuple[str, str]:
        index = 0
        while index < len(self.palette)-1:
            if relative_coverage >= self.thresholds[index]:
                break
            else:
                index += 1
        return self.palette[index]


@dataclass
class ShieldIO6Color(BadgeColor):
    palette: ClassVar[List[Tuple[str, str]]] = [
        ("brightgreen", "#4c1"),
        ("green", "#97ca00"),
        ("yellowgreen", "#a4a61d"),
        ("yellow", "#dfb317"),
        ("orange", "#fe7d37"),
        ("red", "#e05d44")
    ]
