#!/usr/bin/env python

"""We list all the packages we install on our system in a single file
(one for each package manager: one for debian packages, another for
pip, etc). Each file is under version control. We want to be able to
edit those files (remove packages, add some) and "sync" our system
with the modifications.

We also want to call a program with a package as argument and that
program to add the package name to the right file.


"""

import sys
import shutil
import os
from os.path import join, expanduser

DEPS_DIR = "~/dotfiles/requirements/"
APT_FILE = "apt-all.txt"

CONF = "~/.meminstall/"

SYSTEM_PACMAN = "apt-get"

def cache_init(prev_file, APT_FILE=APT_FILE):
    """Copy the package listings to the conf cache.
    """
    curr_apt = join(expanduser(DEPS_DIR), APT_FILE)
    cache_apt = join(expanduser(CONF), APT_FILE)
    shutil.copyfile(curr_apt, cache_apt)

def get_packages(lines):
    packages = []
    for line in lines:
        if (not line.startswith('#')) and (line.strip()):
            packages.append(line.strip())
    return packages

def get_diff(cached_list, curr_list):
    """Diff two lists, return a tuple of lists to be installed, to be
    deleted.

    """
    to_install = list(set(curr_list) - set(cached_list))
    to_delete = list(set(cached_list) - set(curr_list))
    return (to_install, to_delete)

def sync_packages():
    # Get the previous state
    cached = expanduser(join(CONF, APT_FILE))
    if os.path.isfile(cached):
        with open(cached, "rb") as f:
            lines = f.readlines()
        cached_list = get_packages(lines)
    else:
        print "No cache. Will initialize."
        cache_init(prev_file)

    # Get the current package liste.
    curr_list = []
    curr_f = expanduser(join(DEPS_DIR, APT_FILE))
    if os.path.isfile(curr_f):
        with open(curr_f, "rb") as f:
            lines = f.readlines()
        curr_list = get_packages(lines)
    else:
        print "mmh. We don't find the package list at {}.".format(curr_f)

    # Diff: which are new, which are to be deleted ?
    to_install, to_delete = get_diff(cached_list, curr_list)
    print "Found {} packages to delete: {}".format(len(to_delete), to_delete)
    print "Found {} packages to install: {}".format(len(to_install), to_install)

    # Run the package managers.
    import ipdb; ipdb.set_trace()


def check_conf_dir(conf=CONF):
    """If config directory doesn't exist, create it.
    """
    if not os.path.exists(expanduser(conf)):
        os.makedirs(expanduser(conf))
        print "Config directory created at {}".format(conf)

def main():
    check_conf_dir()
    return sync_packages()

if __name__ == "__main__":
    exit(main())
