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
from __future__ import unicode_literals

import operator
import os
import shutil
import sys
from builtins import input
from functools import reduce
from io import open
from os.path import expanduser
from os.path import join

import addict
import clize
from future.utils import exec_
from sigtools.modifiers import annotate
from sigtools.modifiers import kwoargs
from termcolor import colored

# Import the default settings.
from settings import CONF
from settings import REQUIREMENTS_FILES
from settings import REQUIREMENTS_ROOT_DIR
from settings import SYSTEM_PACMAN

CFG_FILE = "~/.syp/settings.py"
cfg_file = expanduser(CFG_FILE)

# Overwrite the default settings with the user's own.
with open(cfg_file, "rb") as fd:
    user_config = fd.read()
exec_(user_config, globals(), locals())


def cache_init(req_file, root_dir=REQUIREMENTS_ROOT_DIR):
    """Copy the package listings to the conf cache.

    Create nested directories to mimic the dotfiles structure if needed.
    """
    fullfile = expanduser(join(root_dir, req_file))
    if not os.path.isfile(fullfile):
        print("The file {} does not exist. Maybe you should check the settings at ~/.syp/settings.py or use syp --init.".format(fullfile))
        return
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

def get_shell_cmd(pmconf, rm=False):
    """Form the shell command with the right package manager.
    It must be ready to append the packages list.

    - pmconf: tuple: name of pm, dict with conf (file, pacman, etc).

    Return: a cmd ready to run (str).
    """
    pacman = None
    un_install = "install"
    if rm:
        un_install = "uninstall"

    if not pmconf:
        print("Package manager not found. Abort.")
        return 0

    # cmd of the form: [sudo] apt-get install -y
    conf = pmconf[1]
    cmd = "{} {} {}".format(
        conf.get('sudo', 'sudo'), # sudo by default
        conf.get('pacman', pmconf[0]),
        conf.get(un_install, un_install),
        )

    return cmd

def run_package_manager(to_install, to_delete, pmconf):
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
                print("Removing...")
                cmd_rm = get_shell_cmd(pmconf, rm=True)
                if not cmd_rm:
                    return 0
                cmd_rm = " ".join([cmd_rm] + to_delete)
                ret_rm = os.system(cmd_rm)

            if to_install:
                cmd_install = get_shell_cmd(pmconf)
                if not cmd_install:
                    return 0
                cmd_install = " ".join([cmd_install] + to_install)
                print("Installing...")
                print(cmd_install)
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
    """Read file root_dir/conf_file and return a list of packages (str).
    """
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
    existing = set(existing)
    packages = set(list(packages))
    to_install = packages - existing
    already_present = packages - to_install
    to_install = list(to_install)
    for pack in already_present:
        print("'{}' is already present".format(pack))

    if to_install:
        if os.path.isfile(conf_file):
            lines = []
            # Lines of packages, with the comment once inline.
            for pack in to_install:
                if message:
                    try:
                        lines.append("{} \t# {}\n".format(pack, message))
                    except UnicodeDecodeError:
                        message = message.decode('utf8')
                        lines.append("{} \t# {}\n".format(pack, message))

                    message = None  # write it only once.
                else:
                    lines.append("{}\n".format(pack))
            with open(conf_file, "a") as f:
                f.writelines(lines)
                print("Added '{}' to {} package list...".format(" ".join(to_install), conf_file))
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
    fullfile = expanduser(join(CONF, afile))
    if os.path.isfile(fullfile):
        with open(fullfile, "rt") as f:
            lines = f.readlines()
        packages = filter_packages(lines)
    else:
        if create_cache:
            print("No cache for {}. Will initialize one.".format(afile))
            cache_init(afile, root_dir=root_dir)
        else:
            print("We don't find the package list at {}.".format(afile))
            return None

    return packages

def copy_file(curr_f, cached_f):
    shutil.copyfile(curr_f, cached_f)

def sync_packages(pmconf, root_dir=REQUIREMENTS_ROOT_DIR):
    """Install or delete packages.

    - pmconf: tuple of a package manager config: pmconf[0] is the pm,
      pmconf[1] a dict with 'file', 'install', 'pacman' etc.

    return: a return code (int).

    """
    conf = addict.Dict(pmconf[1])
    if not os.path.isfile(expanduser(join(CONF, conf.file))):
        print("We don't find the package list at {}.".format(conf.file))
        return 0

    # Get the previous state
    cached_f = expanduser(join(CONF, conf.file))
    cached_f_list = check_file_and_get_package_list(conf.file, create_cache=True, root_dir=root_dir)

    # Get the current package list.
    curr_list = []
    curr_f = expanduser(join(root_dir, conf.file))
    curr_list = check_file_and_get_package_list(curr_f)

    # Diff: which are new, which are to be deleted ?
    to_install, to_delete = get_diff(cached_f_list, curr_list)

    # Pretty output
    print("In " + colored("{}:".format(conf.file), "blue"))

    if not len(to_install) and not len(to_delete):
        print(colored("\t\u2714 nothing to do", "green"))
    else:
        if len(to_install):
            txt = "\tFound {} packages to install: {}".format(len(to_install), ", ".join(to_install))
            txt = colored(txt, "green")
        else:
            txt = "\tNothing to install"
        print(txt)
        if len(to_delete):
            txt = "\tFound {} packages to delete: {}".format(len(to_delete), to_delete)
            txt = colored(txt, "red")
        else:
            txt = "\tNothing to delete"
        print(txt)

    # Run the package managers.
    ret = run_package_manager(to_install, to_delete, pmconf)
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
        print("The {} package manager is unknown. Choice is one of: {}".format(pacman.lower(),
                                                                               ", ".join(REQUIREMENTS_FILES.keys())))
        exit(1)

    conf = conf.get('file')
    if not conf:
        print("There is no configuration file for this package manager. Abort.")
        return None

    return conf

def run_editor(root_dir, conf_file):
    conf = expanduser(os.path.join(root_dir, conf_file))
    cmd = " ".join([os.environ.get('EDITOR'), conf])
    ret = os.system(cmd)
    return ret


# Command line arguments is quickly done with clize.
@annotate(pm="p", message="m", dest="d", editor="e")
@kwoargs("pm", "message", "dest", "rm", "editor", "init")
def main(pm="", message="", dest="", rm=False, editor=False, init=False, *packages):
    """syp will check what's new in your config files, take the
    arguments into account, and it will install and remove packages
    accordingly. It uses a cache in ~/.syp/.

    pm: set the package manager, according to your settings. If not specified, it will work on all of them.

    message: comment to be written in the configuration file.

    dest: <not implemented>

    rm: remove the given packages. If no package is specified, call $EDITOR on the configuration file.

    editor: call your shell's $EDITOR to edit the configuration file associated to the given package manager, before the rest.

    init: write the default settings to ~/.syp/settings.py

    XXX: give a list of available pacman.

    Check your settings in ~/syp/settings.py. Create them with syp --init.
    """
    root_dir = REQUIREMENTS_ROOT_DIR
    req_files = REQUIREMENTS_FILES.items()

    if init:
        check_conf_dir("~/.syp/")
        if not os.path.isfile(cfg_file):
            copy_file("settings.py", cfg_file)
            print("Copied settings into ~/.syp.")
        else:
            print("warning: the file {} already exists. Do nothing.".format(CFG_FILE))

        exit(0)

    # Deal with a specific package manager
    if pm:
        # Sync only the conf file of the current package manager.
        req_files = [tup for tup in req_files if tup[0] == pm]
        print("Let's use {} to install packages {} !".format(pm, " ".join(packages)))
        conf_file = get_conf_file(pm)  # # TODO: to rm ?
        if not conf_file:
            exit(1)
        if editor:
            run_editor(root_dir, conf_file)

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

    # Do the job:
    check_conf_dir()
    ret_codes = []
    for req_file in req_files:
        ret_codes.append(sync_packages(req_file, root_dir=root_dir))

    exit(reduce(operator.or_, ret_codes, 0))

def run():
    exit(clize.run(main))

if __name__ == "__main__":
    exit(clize.run(main))
