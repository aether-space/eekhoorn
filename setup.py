# encoding: utf-8

try:
    from setuptools import setup
    has_setuptools = True
except ImportError:
    from distutils.core import setup
    has_setuptools = False

from eekhoorn import __version__


if has_setuptools:
    extra_kwargs = {
        "entry_points": {
            "console_scripts": [
                "eekhoorn = eekhoorn.__main__:main"
            ]
        },
        "install_requires": [
            "ansicolors",
            "pyrepl",
            "six",
            "sqlalchemy >= 0.7",
            "sqlparse"
        ]
    }
else:
    extra_kwargs = {}


setup(
    name="eekhoorn",
    version=__version__,
    description="A fancy SQL console",
    packages=["eekhoorn", "eekhoorn.tests"],
    **extra_kwargs)
