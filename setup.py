import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "syp",
    version = "0.1",
    packages = find_packages(),
    scripts = ['syp.py', 'settings.py', 'README.org'],

    install_requires = [
        "termcolor", # colored print
        "clize",     # build cli args from the method (kw)args
        "six",
        "future",
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
    description = "Sync your packages in dotfiles.",
    long_description = read('README.org'),
    license = "GNU GPLv3",
    keywords = "utility packages shell",
    url = "https://gitlab.com/vindarel/syp",

    entry_points = {
        "console_scripts": [
            "syp = syp:run",
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
