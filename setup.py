from setuptools import setup, find_packages
setup(
    name = "rpack",
    version = "0.1",
    packages = find_packages(),
    scripts = ['meminstall.py', 'settings.py'],

    install_requires = [],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        # '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        # 'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "vindarel",
    author_email = "ehvince@mailz.org",
    description = "Record installed packages in my dot files.",
    long_description = "I want to install packages (from apt, pip, npm,...) and record them in my dot files with one single command.",
    license = "GNU GPLv3",
    keywords = "utility packages shell",
    url = "https://gitlab.com/vindarel/meminstall",   # project home page, if any

    entry_points = {
        "console_scripts": [
            "rpack = meminstall:run",
        ],
    },

    tests_require = {

    },

)
