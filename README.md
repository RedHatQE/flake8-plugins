# Flake8 python plugins
A collection of flake8 plugins for python code.


## FunctionCallForceNames (FCFN)
A plugin to force call functions with keywords arguments.

## PolarionIds (PID)
A plugin to force Polarion ID for each pytest test.

## UniqueFixturesNames (UFN)
A plugin to force unique fixtures names in pytest.

## Usage
All plugins are off by default and can be enabled by:
1. In .flake8 under enable-extensions section
   enable-extensions =
    FCFN,
    UFN,
    PID,
2. When calling flake8 cli:
   python -m flake8 --enable-extensions=UFN,FCFN,PID

## Code check
We use pre-commit for code check.
```bash
pre-commit install
```
