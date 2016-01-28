# Default settings for syp.py
# Create it with syp --init
# and tweak them in ~/.syp/settings.py

#: The base directory where lies the configuration files.
REQUIREMENTS_ROOT_DIR = "~/dotfiles/"

#: a mapping: name of package manager (the shell command) -> name of
# the config file to write all packages.
REQUIREMENTS_FILES = {
    "apt": "apt.txt", # the path is prepended with the root directory above.
    "pip": "pip.txt",
    "npm": "npm.txt",
    "gem": "ruby.txt",
}

#: Where to put the config, where to cache the files.
CONF = "~/.syp/"

#: System package manager, as a default.
SYSTEM_PACMAN = "apt-get"
