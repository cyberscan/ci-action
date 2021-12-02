#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 02 2021

Copyright (c) 2021 Deutsche Gesellschaft für Cybersicherheit mbH & Co. KG

@author Merlin Mittelbach

test colors
"""
from argparse import ArgumentTypeError
from action import ShieldIO6Color
from pytest import raises


def test_shields_color():
    color = ShieldIO6Color("90,80,60,50,40")
    assert color.thresholds == [90, 80, 60, 50, 40]
    assert repr(color) == 'ShieldIO6Color(thresholds=[90, 80, 60, 50, 40])'
    assert color.palette == ShieldIO6Color.palette
    for rel_cov, index in [(95, 0), (90, 0), (55, 3), (35, 5)]:
        assert color.get_color(rel_cov) == ShieldIO6Color.palette[index]
    with raises(ArgumentTypeError):
        color = ShieldIO6Color("90,80,60,s,50")
    with raises(ArgumentTypeError):
        color = ShieldIO6Color("90,80,60,50")
    with raises(ArgumentTypeError):
        color = ShieldIO6Color("90,80,60,50,55")
    with raises(ArgumentTypeError):
        color = ShieldIO6Color("105,80,60,50,55")
    with raises(ArgumentTypeError):
        color = ShieldIO6Color("100,80,60,50,55,-1")
