#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 02 2021

Copyright (c) 2021 Deutsche Gesellschaft für Cybersicherheit mbH & Co. KG

@author Merlin Mittelbach

test badge classes
"""
from action import CoverageBadge


def test_constructor():
    color = ColorMock()
    badge = CoverageBadge(72, color)
    assert badge.color_code == "lkdgnlk"
    assert badge.color_name == "adskl"
    assert badge.relative_coverage == 72
    assert badge.svg.count("72") == 4
    assert badge.svg.count(badge.color_code) == 1
    assert repr(badge) == \
        "CoverageBadge(relative_coverage=72, color_name='adskl')"


class ColorMock():
    def get_color(self, _: int):
        return ("adskl", "lkdgnlk")
