# -*- coding: utf-8 -*-

"""
flake8 extension check that every test has Polarion ID attach to it.
"""

import ast
import re


PID001 = "PID001: [{f_name} ({params})], Polarion ID is missing"
PID002 = "PID002: [{f_name} {pid}], Polarion ID is wrong"
PID003 = "PID003: [{f_name} {pid}], Polarion ID is duplicate"


def iter_test_functions(tree):
    """
    Get all test function from python file
    """

    def is_test(elm):
        return elm.name.startswith("test_")

    def is_func(elm):
        return isinstance(elm, ast.FunctionDef)

    def test_func_in_class(elm):
        for cls_elm in elm.body:
            if isinstance(cls_elm, ast.ClassDef):
                yield from test_func_in_class(elm=cls_elm)

            if is_func(cls_elm) and is_test(cls_elm):
                yield cls_elm

    for elm in tree.body:
        if isinstance(elm, ast.ClassDef):
            func = test_func_in_class(elm=elm)
            if func:
                yield from func

        elif is_func(elm) and is_test(elm):
            yield elm


def find_func_in_tree(tree, name):
    for elm in tree.body:
        if isinstance(elm, ast.FunctionDef):
            if elm.name == name:
                return elm


def iter_polarion_ids_from_pytest_fixture(tree, name):
    func = find_func_in_tree(tree=tree, name=name)
    if func:
        if not func.decorator_list:
            return None

        for deco in func.decorator_list:
            if not hasattr(deco, "func"):
                continue

            if deco.func.value.id == "pytest" and deco.func.attr == "fixture":
                for deco_keyword in deco.keywords:
                    if deco_keyword.arg == "params":
                        for deco_elts in deco_keyword.value.elts:
                            has_polarion_id = False
                            for deco_elts_keyword in deco_elts.keywords:
                                if deco_elts_keyword.arg == "marks":
                                    if isinstance(
                                        deco_elts_keyword.value, ast.Tuple
                                    ):
                                        for (
                                            dekv
                                        ) in deco_elts_keyword.value.elts:
                                            if dekv.func.attr == "polarion":
                                                has_polarion_id = True
                                                yield dekv.args[0]
                                    else:
                                        if (
                                            deco_elts_keyword.value.func.attr
                                            == "polarion"
                                        ):
                                            has_polarion_id = True
                                            yield deco_elts_keyword.value.args[
                                                0
                                            ]

                            if not has_polarion_id:
                                yield deco_elts


class PolarionIds(object):
    """
    flake8 extension check that every test has Polarion ID attach to it.
    """

    off_by_default = True
    name = "PolarionIds"
    version = "1.0.0"

    def __init__(self, tree):
        self.tree = tree
        self.polarion_ids = []

    @classmethod
    def add_options(cls, option_manager):
        option_manager.add_option(
            long_option_name="--skip-duplicate-polarion-ids-check",
            default="False",
            parse_from_config=True,
            comma_separated_list=False,
            help="Skip check for duplicate Polarion Ids.",
        )

    @classmethod
    def parse_options(cls, options):
        cls.skip_duplicate_ids_check = ast.literal_eval(
            options.skip_duplicate_polarion_ids_check
        )

    def _non_decorated(self, f, params=""):
        yield (
            f.lineno,
            f.col_offset,
            PID001.format(f_name=f.name, params=params),
            self.name,
        )

    def _non_decorated_elt(self, f, elt, params=""):
        yield (
            elt.lineno,
            elt.col_offset,
            PID001.format(f_name=f.name, params=params),
            self.name,
        )

    def _if_bad_pid(self, f, polarion_id):
        if not re.match(r"CNV-\d+", polarion_id):
            yield (
                f.lineno,
                f.col_offset,
                PID002.format(f_name=f.name, pid=polarion_id),
                self.name,
            )
        else:
            yield from self._is_polarion_id_duplicate(
                f=f, polarion_id=polarion_id
            )

    def _non_decorated_fixture(self, f, polarion_id):
        param = ""
        if isinstance(polarion_id, ast.Call):
            if isinstance(polarion_id.args[0], ast.Str):
                param = polarion_id.args[0].s
            if isinstance(polarion_id.args[0], ast.List):
                for parg in polarion_id.args[0].elts:
                    if isinstance(parg, ast.Str):
                        param = parg.s

        yield (
            polarion_id.lineno,
            polarion_id.col_offset,
            PID001.format(f_name=f.name, params=param),
            self.name,
        )

    def _if_bad_pid_fixture(self, f, polarion_id):
        if not re.match(r"CNV-\d+", polarion_id.s):
            yield (
                polarion_id.lineno,
                polarion_id.col_offset,
                PID002.format(f_name=f.name, pid=polarion_id.s),
                self.name,
            )
        else:
            yield from self._is_polarion_id_duplicate(
                f=f, polarion_id=polarion_id
            )

    def _check_pytest_fixture_polarion_ids(self, f):
        exist = False
        for f_arg in f.args.args:
            for polarion_id in iter_polarion_ids_from_pytest_fixture(
                self.tree, f_arg.arg
            ):
                exist = True
                if isinstance(polarion_id, ast.Str):
                    yield from self._if_bad_pid_fixture(
                        f=f, polarion_id=polarion_id
                    )
                else:
                    yield from self._non_decorated_fixture(
                        f=f, polarion_id=polarion_id
                    )
        if not exist:
            yield from self._non_decorated(f=f)

    def _is_polarion_id_duplicate(self, f, polarion_id):
        if self.skip_duplicate_ids_check:
            return

        if polarion_id in self.polarion_ids:
            yield (
                f.lineno,
                f.col_offset,
                PID003.format(f_name=f.name, pid=polarion_id),
                self.name,
            )
        else:
            self.polarion_ids.append(polarion_id)

    def run(self):
        """
        Check that every test has a Polarion ID
        """
        for f in iter_test_functions(self.tree):
            sorted_doce_list = []
            polarion_mark_exists = False
            if not f.decorator_list:
                # Test is missing Polarion ID, check if test use parametrize fixture
                # with Polarion ID.
                yield from self._check_pytest_fixture_polarion_ids(f=f)
                continue

            for deco in f.decorator_list:
                if not hasattr(deco, "func"):
                    continue

                if (
                    deco.func.value.value.id == "pytest"
                    and deco.func.value.attr == "mark"
                ):
                    if deco.func.attr == "polarion":
                        sorted_doce_list.insert(0, deco)

                    elif deco.func.attr == "parametrize":
                        sorted_doce_list.append(deco)

            for deco in sorted_doce_list:
                if deco.func.attr == "polarion":
                    polarion_mark_exists = True
                    if deco.args:
                        yield from self._if_bad_pid(
                            f=f, polarion_id=deco.args[0].s
                        )
                    else:
                        yield from self._non_decorated(f=f)
                    break

                elif deco.func.attr == "parametrize":
                    if deco.args:
                        for arg in deco.args:
                            if not isinstance(arg, ast.List):
                                continue

                            for elt in arg.elts:
                                if isinstance(elt, ast.Dict):
                                    continue

                                if not isinstance(elt, ast.Call):
                                    yield from self._non_decorated_elt(
                                        f=f, elt=elt, params=elt.s
                                    )
                                    continue

                                if not elt.keywords:
                                    yield from self._non_decorated_elt(
                                        f=f, elt=elt
                                    )

                                for pk in elt.keywords:
                                    # In case parametrize have id=
                                    if pk.arg == "id":
                                        continue

                                    # In case of multiple marks on test param
                                    if isinstance(pk.value, ast.Tuple):
                                        for elt_val in pk.value.elts:
                                            if elt_val.func.attr == "polarion":
                                                polarion_mark_exists = True
                                                yield from self._if_bad_pid(
                                                    f=f,
                                                    polarion_id=elt_val.args[
                                                        0
                                                    ].s,
                                                )

                                    # In case one mark on test param
                                    elif (
                                        pk.arg == "marks"
                                        and pk.value.func.attr == "polarion"
                                    ):
                                        polarion_mark_exists = True
                                        yield from self._if_bad_pid(
                                            f=f, polarion_id=pk.value.args[0].s
                                        )

                                    else:
                                        # In case no mark on test param
                                        yield from self._non_decorated(
                                            f=f, params=elt.args[0].s
                                        )
                else:
                    yield from self._non_decorated(f=f)

            if not polarion_mark_exists:
                yield from self._non_decorated(f=f)
