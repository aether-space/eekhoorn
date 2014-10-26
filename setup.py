# encoding: utf-8

from setuptools import setup

from eekhoorn import __version__


setup(
    name="eekhoorn",
    version=__version__,
    description="A fancy SQL console",
    packages=["eekhoorn", "eekhoorn.tests"],
    entry_points={
        "console_scripts": [
            "eekhoorn = eekhoorn.__main__:main"
        ]
    },
    install_requires=[
        "ansicolors",
        "pyrepl",
        "six",
        "sqlalchemy >= 0.7",
        "sqlparse"
    ])
