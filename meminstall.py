#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""We list all the packages we install on our system in a single file
(one for each package manager: one for debian packages, another for
pip, etc). Each file is under version control. We want to be able to
edit those files (add, remove packages) and "sync" our system
with the modifications.

We also want to call a program with a package as argument and that
program to add the package name to the right file.

"""

from __future__ import print_function

import operator
import os
import shutil
import sys
from builtins import input
from functools import reduce
from io import open
from os.path import expanduser
from os.path import join

import clize
from sigtools.modifiers import annotate
from sigtools.modifiers import kwoargs
from termcolor import colored

CFG_FILE = "~/.meminstall/settings.py"
cfg_file = expanduser(CFG_FILE)
if os.path.isfile(cfg_file):
    sys.path.insert(0, expanduser("~/.meminstall"))
    from settings import (REQUIREMENTS_ROOT_DIR,
                          REQUIREMENTS_FILES,
                          CONF,
                          SYSTEM_PACMAN)

else:
    print("We didn't find settings at {}. Loading default settings.".format(cfg_file))
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

def cache_init(req_file, root_dir=REQUIREMENTS_ROOT_DIR):
    """Copy the package listings to the conf cache.
    """
    curr_apt = join(expanduser(root_dir), req_file)
    cache_apt = join(expanduser(CONF), req_file)
    # Create new directories if needed.
    split = req_file.split("/")[0:-1]
    for i in range(len(split)):
        maybe_dir = join(expanduser(CONF), split[i:i+1][0])
        if not os.path.isdir(maybe_dir):
            os.makedirs(expanduser(maybe_dir))
    # At last, copy it.
    shutil.copyfile(curr_apt, cache_apt)

def get_diff(cached_list, curr_list):
    """Diff two lists, return a tuple of lists to be installed, to be
    deleted.

    """
    to_install = list(set(curr_list) - set(cached_list))
    to_delete = list(set(cached_list) - set(curr_list))
    return (to_install, to_delete)

def get_shell_cmd(req_file, rm=False):
    """Form the shell command with the right package manager.
    It must be ready to append the packages list.

    req_file: str representing the file we read the packages from.
    """
    pacman = None
    if req_file == REQUIREMENTS_FILES["apt"]:
        pacman = "apt-get {} -y"
    elif req_file == REQUIREMENTS_FILES["npm"]:
        pacman = "npm {} -g"
    elif req_file == REQUIREMENTS_FILES["ruby"]:
        pacman = "gem {}"
    elif req_file == REQUIREMENTS_FILES["pip"]:
        pacman = "pip {}"
    else:
        print("Package manager not found. Abort.")
        return 0

    un_install = "install"
    if rm:
        un_install = "remove"
    pacman = pacman.format(un_install)
    cmd = "sudo {}".format(pacman)
    return cmd

def run_package_manager(to_install, to_delete, req_file):
    """Construct the command, run the right package manager.

    Install and delete packages.

    return 0 when ok, 1 when there was a pb, or nothing to install nor uninstall.
    """
    if to_install or to_delete:
        go = input("Install and delete packages ? [Y/n]")
        ret_rm = 0
        ret_install = 0
        if go in ["y", "yes", "o", ""]:
            if to_delete:
                print("Removing…")
                cmd_rm = get_shell_cmd(req_file, rm=True)
                cmd_rm = " ".join([cmd_rm] + to_delete)
                ret_rm = os.system(cmd_rm)

            if to_install:
                cmd_install = get_shell_cmd(req_file)
                cmd_install = " ".join([cmd_install] + to_install)
                print("Installing…")
                ret_install = os.system(cmd_install)

            return ret_install or ret_rm

    return 1

def filter_packages(lines):
    """Get rid of comments. Return the packages list.

    warning: it removes everything after a '#'. Do some requirement
    files use it to specify the package version ?

    """
    packages = []
    for line in lines:
        if (not line.startswith('#')) and (line.strip()):
            if '#' in line:
                line = line.split('#')[0]
            packages.append(line.strip())
    return packages

def read_packages(conf_file, root_dir=""):
    conf_file = expanduser(os.path.join(root_dir, conf_file))
    lines = []
    if os.path.isfile(conf_file):
        with open(conf_file, "r") as f:
            lines = f.readlines()
            lines = filter_packages(lines)

    return lines

def write_packages(packages, conf_file=None, message=None, root_dir=""):
    """Add the packages to the given conf file. Don't write duplicates.
    """
    conf_file = expanduser(os.path.join(root_dir, conf_file))
    existing = read_packages(conf_file, root_dir=root_dir)
    packages = list(packages)
    for pack in packages:
        if pack in existing:
            print("'{}' is already present".format(pack))
            packages.remove(pack)

    if packages:
        if os.path.isfile(conf_file):
            lines = []
            # Lines of packages, with the comment once inline.
            for pack in packages:
                if message:
                    lines.append(u"{} \t# {}\n".format(pack, message))
                    message = None  # write it only once.
                else:
                    lines.append(u"{}\n".format(pack))
            with open(conf_file, "a") as f:
                f.writelines(lines)
                print("Added '{}' to {} package list...".format(" ".join(packages), conf_file))
                return 0
        else:
            print("mmh... the config file doesn't exist: {}".format(conf_file))
            exit(1)


def erase_packages(packages, conf_file=None, message=None, root_dir=""):
    conf_file = expanduser(os.path.join(root_dir, conf_file))
    if os.path.isfile(conf_file):
        with open(conf_file, "r") as f:
            lines = f.readlines()
            erased = []
            for pack in packages:
                lines = [line for line in lines if not line.startswith(pack)]

        with open(conf_file, "w") as f:
            f.writelines(lines)
            print("Removed {} from {} package list.".format(", ".join(packages), conf_file))

def check_file_and_get_package_list(afile, create_cache=False, root_dir=None):
    """From a given file, read its package list.
    Create the cache file if appropriate.
    """
    packages = []
    if os.path.isfile(afile):
        with open(afile, "rt") as f:
            lines = f.readlines()
        packages = filter_packages(lines)
    else:
        if create_cache:
            print("No cache. Will initialize for {}.".format(afile))
            cache_init(afile, root_dir=root_dir)
        else:
            print("We don't find the package list at {}.".format(afile))

    return packages

def copy_file(curr_f, cached_f):
    shutil.copyfile(curr_f, cached_f)

def sync_packages(req_file, root_dir=REQUIREMENTS_ROOT_DIR):


    # Get the previous state
    cached_f = expanduser(join(CONF, req_file))
    cached_f_list = check_file_and_get_package_list(cached_f, create_cache=True, root_dir=root_dir)

    # Get the current package list.
    curr_list = []
    curr_f = expanduser(join(root_dir, req_file))
    curr_list = check_file_and_get_package_list(curr_f)

    # Diff: which are new, which are to be deleted ?
    to_install, to_delete = get_diff(cached_f_list, curr_list)

    # Pretty output
    print("In {}:".format(req_file))
    if not len(to_install) and not len(to_delete):
        print("\tnothing to do")
    else:
        txt = "\tFound {} packages to install: {}".format(len(to_install), to_install)
        if len(to_install):
            txt = colored(txt, "green")
        print(txt)
        txt = "\tFound {} packages to delete: {}".format(len(to_delete), to_delete)
        if len(to_delete):
            txt = colored(txt, "red")
        print(txt)

    # Run the package managers.
    ret = run_package_manager(to_install, to_delete, req_file)
    if ret == 0:
        #XXX check which of install or rm worked, write corresponding item in file.
        copy_file(curr_f, cached_f)

    return ret

def check_conf_dir(conf=CONF, create_venv_conf=False):
    """If config directory doesn't exist, create it.
    """
    if not os.path.exists(expanduser(conf)):
        os.makedirs(expanduser(conf))
        print("Config directory created at {}".format(conf))

def get_conf_file(pacman):
    """Return the configuration file of the given package manager.
    """
    conf = REQUIREMENTS_FILES.get(pacman.lower())
    if not conf:
        print("There is no configuration file for this package manager. Abort.")
        return None

    return conf

def run_editor(root_dir, conf_file):
    conf = expanduser(os.path.join(root_dir, conf_file))
    cmd = " ".join([os.environ.get('EDITOR'), conf])
    ret = os.system(cmd)
    return ret


@annotate(pm="p", message="m", dest="d", editor="e")
@kwoargs("pm", "message", "dest", "rm", "editor")
def main(pm="", message="", dest="", rm=False, editor=False, *packages):
    """

    pm: specify a package manager.

    rm: remove installed packages. If no packages are specified, call $EDITOR on the configuration file.

    TODO: give list of available pacman.
    """
    root_dir = REQUIREMENTS_ROOT_DIR
    req_files = REQUIREMENTS_FILES.items()
    req_files = list(REQUIREMENTS_FILES.items())

    conf_file = get_conf_file(pm)
    if not conf_file:
        exit(1)
    if editor:
        run_editor(root_dir, conf_file)

    # Deal with another package manager
    if pm:
        # Sync only the conf file of the current package manager.
        req_files = [tup for tup in req_files if tup[0] == pm]
        print("Let's use {} to install packages {} !".format(pm, " ".join(packages)))
        print("with comment: " + message)
        # TODO: venv
        if not rm:
            write_packages(packages, message=message, conf_file=conf_file, root_dir=root_dir)
        else:
            if not packages:
                # Edit conf file directly
                conf = expanduser(os.path.join(root_dir, conf_file))
                cmd = " ".join([os.environ.get('EDITOR'), conf])
                ret = os.system(cmd)
            # Edit the file in cache.
            erase_packages(packages, message=message, conf_file=conf_file, root_dir=root_dir)

        print("Syncing {} packages...".format(pm.lower()))

    if dest:
        # We could be in a venv but in the root of anothe project and still
        # add a package to its requirement, that we give on the cli.
        print("destination to write: ", dest)
        exit

    check_conf_dir()
    ret_codes = []
    for _, val in req_files:
        ret_codes.append(sync_packages(val, root_dir=root_dir))

    return reduce(operator.or_, ret_codes, 0)

def run():
    exit(clize.run(main))

if __name__ == "__main__":
    exit(clize.run(main))
