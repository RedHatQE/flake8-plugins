# -*- coding: utf-8 -*-

"""
flake8 extension to check import from conftest.py..
"""

import ast
import re


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
        if isinstance(_import, ast.Import) or isinstance(_import, ast.ImportFrom):
            return _import

    def _all_imports(self):
        for _import in self.tree.body:
            if self._is_import(_import=_import):
                yield _import

    def _import_in_exclude(self, imports):
        return any([_imp for _imp in imports if _imp in self.exclude_imports])

    def run(self):
        """
        Check if file import from tests
        """
        for _import in self._all_imports():
            import_name = None
            if isinstance(_import, ast.ImportFrom):
                import_name = _import.module
                if not import_name:
                    import_name = _import.names[-1].name
            elif isinstance(_import, ast.Import):
                import_name = _import.names[-1].name

            split_import_name = import_name.split(".")
            _base_import_path = split_import_name[0]
            import_from = split_import_name[1:]
            _imports_to_check_for_excluding = [import_name]
            if import_from:
                _imports_to_check_for_excluding.append(import_from[0])
            if self._import_in_exclude(imports=_imports_to_check_for_excluding):
                continue

            split_seq = 1
            base_import_path = re.findall(rf"/{_base_import_path}/", self.filename)
            if not base_import_path:
                split_seq = 1
                base_import_path = re.findall(rf"^{_base_import_path}/", self.filename)

            if not base_import_path:
                continue

            base_import_path = base_import_path[0]
            _base_file_name_path = self.filename.split(f"{base_import_path}", split_seq)[-1].split("/")
            base_file_name_path = list(filter(lambda x: x, _base_file_name_path))
            import_name_end = import_name.split(".")[-1]
            if import_name_end.startswith("test_") or _base_import_path == "tests":
                if import_from and base_file_name_path:
                    if import_from[0] != base_file_name_path[0]:
                        yield (
                            _import.lineno,
                            _import.col_offset,
                            NIT001,
                            self.name,
                        )
                else:
                    yield (
                        _import.lineno,
                        _import.col_offset,
                        NIT001,
                        self.name,
                    )
