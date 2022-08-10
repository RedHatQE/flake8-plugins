# -*- coding: utf-8 -*-

"""
flake8 extension to check import from conftest.py..
"""

import re


NIT001 = "NIT001: Import from tests is not allowed."


class NoImportFromTests(object):
    """
    flake8 extension to check import from tests..
    """

    off_by_default = True
    name = "NoImportFromTests"
    version = "1.0.0"

    def __init__(self, tree, lines, filename):
        self.tree = tree
        self.lines = lines
        self.filename = filename

    @classmethod
    def add_options(cls, option_manager):
        option_manager.add_option(
            long_option_name="--nift_exclude_imports",
            default="",
            parse_from_config=True,
            comma_separated_list=True,
            help="Import to exclude from checking.",
        )

    @classmethod
    def parse_options(cls, options):
        cls.exclude_imports = options.nift_exclude_imports

    def run(self):
        """
        Check if file import from tests
        """
        imports = [
            line
            for line in self.lines
            if "tests" in line
            and (line.startswith("import") or line.startswith("from"))
            and "conftest" not in line
        ]
        for _import in imports:
            tests_list = re.findall(r"tests\.\w+", _import)
            tests_str = tests_list[0].replace(".", "/")
            if [imp for imp in self.exclude_imports if imp in _import]:
                continue

            if tests_str not in self.filename:
                yield (
                    self.lines.index(_import) + 1,
                    1,
                    NIT001,
                    self.name,
                )
