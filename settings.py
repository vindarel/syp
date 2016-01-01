
#: The base directory where lie the configuration files.
REQUIREMENTS_ROOT_DIR = "~/dotfiles/requirements/"

#: mapping package-manager -> config file.
# Shall we do "any name" -> package manager -> config file ?
# Where the pacman could be defined inside the file.

# The mapping could also be inplicit. If we have a file mao.txt, the
# command "meminstall --pm mao foo" will write foo to mao.txt and will
# use the package manager defined inside it.
REQUIREMENTS_FILES = {
    "apt": "apt-all.txt",
    "npm": "npm-requirements.txt",
    "ruby": "ruby/ruby-packages.txt",
    "gem": "ruby/ruby-packages.txt",
    "pip": "pip.txt",
}

#: Where to put the config, where to cache the files.
CONF = "~/.meminstall/"

#: System package manager, as a default. This will be induced on next version.
SYSTEM_PACMAN = "apt-get"
