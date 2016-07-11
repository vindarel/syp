# Default settings for syp.py
# Create it with syp --init
# and tweak them in ~/.syp/settings.py

#: The base directory where lies the configuration files.
REQUIREMENTS_ROOT_DIR = "~/dotfiles/"

#: a mapping: name of package manager (the shell command) -> dict
# with:
# - the name of the config file to write all packages,
# - the name of # the package manager (if different from key),
# - the "install" command # (if not "install"),
# - the uninstall command.
REQUIREMENTS_FILES = {
    "apt": {
        "file": "apt.txt", # the path is prepended with the root directory above.
        "pacman": "apt-get",
        "install": "install -y",
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
