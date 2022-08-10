#! /usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup


setup(
    name="flake8-python-plugins",
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=["flake8"],
    entry_points={
        "flake8.extension": [
            "FCN = FunctionCallForceNames:FunctionCallForceNames",
            "PID = PolarionIds:PolarionIds",
            "UFN = UniqueFixturesNames:UniqueFixturesNames",
            "NIC = NoImportFromConftest:NoImportFromConftest",
            "NIT = NoImportFromTests:NoImportFromTests",
            "UUC = UnusedCode:UnusedCode",
        ],
    },
)
