# -*- coding: utf-8 -*-

"""
flake8 extension to check import from conftest.py..
"""

import ast

NIFC001 = "NIFC: Import from conftest.py is not allowed."


class NoImportFromConftest(object):
    """
    flake8 extension to check import from conftest.py..
    """

    off_by_default = True
    name = "NoImportFromConftest"
    version = "1.0.0"

    def __init__(self, tree, lines):
        self.tree = tree
        self.lines = lines

    def run(self):
        """
        Check if file import from conftest.py
        """
        for elm in self.tree.body:
            if isinstance(elm, ast.Import) or isinstance(elm, ast.ImportFrom):
                line_number = elm.lineno
                line = self.lines[line_number]
                if "conftest import" in line or "import conftest" in line:
                    yield (
                        line_number,
                        elm.col_offset,
                        NIFC001,
                        self.name,
                    )
