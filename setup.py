import os

import pypandoc
from setuptools import find_packages
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "syp",
    version = "0.1.3",
    packages = find_packages(),
    scripts = ['syp/syp.py', 'syp/settings.py', 'README.org'],

    install_requires = [
        "termcolor", # colored print
        "clize",     # build cli args from the method (kw)args
        "six",
        "future",
        "addict",
    ],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        # '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        # 'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "vindarel",
    author_email = "ehvince@mailz.org",
    description = "Sync your packages with your dotfiles (and vice versa).",
    long_description = pypandoc.convert('README.org', 'rst'),
    license = "GNU GPLv3",
    keywords = "utility packages shell",
    url = "https://github.com/vindarel/syp",

    entry_points = {
        "console_scripts": [
            "syp = syp.syp:run",
        ],
    },

    tests_require = {

    },

    classifiers = [
        "Environment :: Console",
        "License :: Public Domain",
        "Topic :: Utilities",
    ],

)
