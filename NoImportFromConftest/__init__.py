# -*- coding: utf-8 -*-

"""
flake8 extension to check import from conftest.py..
"""

import ast

NIFC001 = "NIFT: Import from conftest.py is not allowed."


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
        imports = [
            line
            for line in self.lines
            if "conftest" in line and (line.startswith("import") or line.startswith("from"))
        ]

        for _import in imports:
            yield (
                self.lines.index(_import) + 1,
                1,
                NIFC001,
                self.name,
            )
        # for elm in self.tree.body:
        #     if isinstance(elm, ast.Import) or isinstance(elm, ast.ImportFrom):
        #         line_number = elm.lineno - 1
        #         line = self.lines[line_number]
        #         if "conftest import" in line or "import conftest" in line:
        #             yield (
        #                 line_number,
        #                 elm.col_offset,
        #                 NIFC001,
        #                 self.name,
        #             )
