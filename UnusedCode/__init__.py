# -*- coding: utf-8 -*-

"""
flake8 extension to check unique fixtures names.
"""

import ast
import subprocess


UUC001 = "UUC001: [{f_name}], Is not used anywhere in the code."


class UnusedCode(object):
    """
    flake8 extension to check if code is not used.
    """

    off_by_default = True
    name = "UnusedCode"
    version = "1.0.0"

    def __init__(self, tree):
        self.tree = tree

    @classmethod
    def add_options(cls, option_manager):
        option_manager.add_option(
            long_option_name="--uuc_ignore_prefix",
            default="",
            parse_from_config=True,
            comma_separated_list=True,
            help="Import to exclude from checking.",
        )

    @classmethod
    def parse_options(cls, options):
        cls.uuc_ignore_prefix = options.uuc_ignore_prefix

    @staticmethod
    def is_fixture_autouse(func):
        if func.decorator_list:
            for deco in func.decorator_list:
                if not hasattr(deco, "func"):
                    continue

                if deco.func.attr == "fixture" and deco.func.value.id == "pytest":
                    for _key in deco.keywords:
                        if _key.arg == "autouse":
                            return _key.value.s

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
            if [func.name for ignore_prefix in self.uuc_ignore_prefix if func.name.startswith(ignore_prefix)]:
                continue

            if self.is_fixture_autouse(func=func):
                continue

            _used = subprocess.check_output(f"git grep {func.name} | wc -l", shell=True)
            used = int(_used.strip())
            if used < 2:
                yield (
                    func.lineno,
                    func.col_offset,
                    UUC001.format(f_name=func.name),
                    self.name,
                )
