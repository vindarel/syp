# Default settings for syp.py

"""
Create this file with syp --init
and tweak the settings in ~/.syp/settings.py.

One can overwrite the REQUIREMENTS_FILES dictionnary:

REQUIREMENTS_FILES['apt'] = {
    "file": "my-apt-requirements.txt",
    "pacman": "aptitude",
    "install": "install -y",
    "uninstall": "remove",
}
"""

#: The base directory where lies the configuration files.
REQUIREMENTS_ROOT_DIR = "~/dotfiles/"

#: a mapping: name of package manager (the shell command) -> dict
# with:
# - the name of the config file to write all packages,
# - the name of the package manager (if different from key),
# - the "install" command # (if not "install"),
# - the uninstall command.
REQUIREMENTS_FILES = {
    "apt": {
        "file": "apt.txt", # the path is prepended with the root directory above.
        "pacman": "apt-get",
        "install": "install -y --force-yes",
        "uninstall": "remove",
        },
    "pip": {
        "file": "pip.txt",
        },
    "pip3": {
        "file": "pip3.txt",
        },
    "npm": {
        "file": "npm.txt",
        "install": "install -g",
        "uninstall": "remove",
        },
    "gem": {
        "file": "ruby.txt",
        },

    "guix": {
        "file": "guix.txt",
        "pacman": "guix",
        "install": "guix package -i",
        "uninstall": "guix package -r",
        },

    "docker": {
        "file": "docker.txt",
        "install": "pull",
        "uninstall": "rm",
        "sudo": "",
        },
}

#: Where to put the config, where to cache the files.
CONF = "~/.syp/"

#: System package manager, as a default.
SYSTEM_PACMAN = "apt-get"
