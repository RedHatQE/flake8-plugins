# -*- coding: utf-8 -*-

"""
flake8 extension to check unique fixtures names.
"""

import ast


UFN001 = "UFN001: [{f_name}], Fixture name is not unique."
FIXTURES = []


class UniqueFixturesNames(object):
    """
    flake8 extension to check unique fixtures names.
    """

    off_by_default = True
    name = "UniqueFixturesNames"
    version = "1.0.0"

    def __init__(self, tree):
        self.tree = tree

    def _iter_functions(self):
        """
        Get all function from python file
        """

        def is_func(elm):
            return isinstance(elm, ast.FunctionDef)

        def is_test(elm):
            return elm.name.startswith("test_")

        for elm in self.tree.body:
            if is_func(elm=elm):
                if is_test(elm=elm):
                    continue

                yield elm

    def run(self):
        """
        Check if fixture name is unique.
        """
        for func in self._iter_functions():
            if func.decorator_list:
                for deco in func.decorator_list:
                    if not hasattr(deco, "func"):
                        continue

                    if deco.func.attr == "fixture" and deco.func.value.id == "pytest":
                        name = func.name
                        if name not in FIXTURES:
                            FIXTURES.append(name)
                        else:
                            yield (
                                func.lineno,
                                func.col_offset,
                                UFN001.format(f_name=func.name),
                                self.name,
                            )
