#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 02 2021

Copyright (c) 2021 Deutsche Gesellschaft für Cybersicherheit mbH & Co. KG

@author Merlin Mittelbach

creating svg badges
"""
from dataclasses import InitVar, dataclass, field
from logging import getLogger
from typing import ClassVar, TextIO

from .colors import BadgeColor

logger = getLogger(__file__)


@dataclass
class CoverageBadge:
    """svg badge class
    """
    relative_coverage: int

    color_name: str = field(init=False)
    color_code: str = field(init=False, repr=False)
    svg: str = field(init=False, repr=False)

    color: InitVar[BadgeColor]

    template: ClassVar[str] = field(repr=False, default='''
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="96" height="20" role="img" aria-label="coverage: {relative_coverage}%">
    <title>coverage: {relative_coverage}%</title>
	<linearGradient id="s" x2="0" y2="100%">
		<stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
		<stop offset="1" stop-opacity=".1"/>
	</linearGradient>
	<clipPath id="r">
		<rect width="96" height="20" rx="3" fill="#fff"/>
	</clipPath>
	<g clip-path="url(#r)">
		<rect width="61" height="20" fill="#555"/>
		<rect x="61" width="35" height="20" fill="{color}"/>
		<rect width="96" height="20" fill="url(#s)"/>
	</g>
	<g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110">
		<text aria-hidden="true" x="315" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="510">coverage</text>
		<text x="315" y="140" transform="scale(.1)" fill="#fff" textLength="510">coverage</text>
		<text aria-hidden="true" x="775" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="250">{relative_coverage}%</text>
		<text x="775" y="140" transform="scale(.1)" fill="#fff" textLength="250">{relative_coverage}%</text>
	</g>
</svg>'''  # noqa
    )

    def __post_init__(self, color: BadgeColor):
        self.color_name, self.color_code = color.get_color(
            self.relative_coverage
        )
        self.svg = CoverageBadge.template.format(
            relative_coverage=self.relative_coverage,
            color=self.color_code
        )
        logger.debug(
            "Created %s coverage badge for relative coverage of %i.",
            self.color_name, self.relative_coverage
        )

    def dump(self, file_handler: TextIO):
        """Dump badge SVG to file.

        Args:
            file_handler (TextIO): file IO
        """
        file_handler.write(
            self.svg
        )
        logger.debug(
            "Dumped %s to file.",
            repr(self)
        )

    def dumps(self) -> str:
        """Dumps SVG file to string.

        Returns:
            str: svg string
        """
        logger.debug(
            "Dumped %s to string.",
            repr(self)
        )
        return self.svg
