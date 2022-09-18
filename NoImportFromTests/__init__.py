# -*- coding: utf-8 -*-

"""
flake8 extension to check import from conftest.py..
"""
import ast


NIT001 = "NIT001: Import from tests is not allowed."


class NoImportFromTests(object):
    """
    flake8 extension to check import from tests.
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
            long_option_name="--nit_exclude_imports",
            default="",
            parse_from_config=True,
            comma_separated_list=True,
            help="Import to exclude from checking.",
        )

    @classmethod
    def parse_options(cls, options):
        cls.exclude_imports = options.nit_exclude_imports

    @staticmethod
    def _is_import(_import):
        if isinstance(_import, ast.Import) or isinstance(
            _import, ast.ImportFrom
        ):
            return _import

    def run(self):
        """
        Check if file import from tests
        """
        imports = [
            _import
            for _import in self.tree.body
            if self._is_import(_import=_import)
        ]
        for _import in imports:
            import_name = None
            if isinstance(_import, ast.ImportFrom):
                import_name = _import.module
                if not import_name:
                    import_name = _import.names[-1].name
            elif isinstance(_import, ast.Import):
                import_name = _import.names[-1].name

            import_name_end = import_name.split(".")[-1]
            if import_name_end.startswith("test_"):
                yield (
                    _import.lineno,
                    _import.col_offset,
                    NIT001,
                    self.name,
                )
