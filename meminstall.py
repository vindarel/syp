#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import operator
import os
from os.path import join, expanduser

DEPS_ROOT_DIR = "~/dotfiles/requirements/"
REQUIREMENTS_FILES = {
    "APT": "apt-all.txt",
    "NPM": "npm-requirements.txt",
    "RUBY": "ruby/ruby-packages.txt",
}

CONF = "~/.meminstall/"

SYSTEM_PACMAN = "apt-get"

def cache_init(req_file):
    """Copy the package listings to the conf cache.
    """
    curr_apt = join(expanduser(DEPS_ROOT_DIR), req_file)
    cache_apt = join(expanduser(CONF), req_file)
    # Create new directories if needed.
    split = req_file.split("/")[0:-1]
    import ipdb; ipdb.set_trace()
    for i in xrange(len(split)):
        maybe_dir = join(expanduser(CONF), split[i:i+1][0])
        if not os.path.isdir(maybe_dir):
            os.makedirs(expanduser(maybe_dir))
    # At last, copy it.
    shutil.copyfile(curr_apt, cache_apt)

def get_packages(lines):
    """Get rid of comments. Return the packages list.
    """
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

def get_shell_cmd(req_file):
    """Form the shell command with the right package manager.
    It must be ready to append the packages list.
    """
    pacman = None
    if req_file == REQUIREMENTS_FILES["APT"]:
        pacman = "apt-get install -y"
    if req_file == REQUIREMENTS_FILES["NPM"]:
        pacman = "npm install -g"
    elif req_file == REQUIREMENTS_FILES["RUBY"]:
        pacman = "gem install"
    elif req_file == REQUIREMENTS_FILES["PIP"]:
        pacman = "pip install"
    else:
        print "Package manager not found. Abort."

    cmd = "sudo {}".format(pacman)
    return cmd

def run_package_manager(to_install, to_delete, req_file):
    """Run the right package manager. Install and delete packages.
    """
    if to_install or to_delete:
        go = raw_input("Install packages ? [Y/n]")
        if go in ["y", "yes", "o", ""]:
            cmd = get_shell_cmd(req_file)
            if not cmd:
                return 1
            cmd = " ".join([cmd] + to_install)
            os.system(cmd)

        else:
            return 1

    return 0

def sync_packages(req_file):

    def check_file_and_get_package_list(afile, create_cache=False):
        """From a given file, read its package list.
        Create the cache file if appropriate.
        """
        packages = []
        if os.path.isfile(afile):
            with open(afile, "rb") as f:
                lines = f.readlines()
            packages = get_packages(lines)
        else:
            if create_cache:
                print "No cache. Will initialize for {}.".format(req_file)
                cache_init(req_file)
            else:
                print "We don't find the package list at {}.".format(afile)

        return packages

    # Get the previous state
    cached_f = expanduser(join(CONF, req_file))
    cached_f_list = check_file_and_get_package_list(cached_f, create_cache=True)

    # Get the current package list.
    curr_list = []
    curr_f = expanduser(join(DEPS_ROOT_DIR, req_file))
    curr_list = check_file_and_get_package_list(curr_f)

    # Diff: which are new, which are to be deleted ?
    to_install, to_delete = get_diff(cached_f_list, curr_list)
    print "In {}:".format(req_file)
    print "\tFound {} packages to delete: {}".format(len(to_delete), to_delete)
    print "\tFound {} packages to install: {}".format(len(to_install), to_install)

    # Run the package managers.
    ret = run_package_manager(to_install, to_delete, req_file)
    if ret == 0:
        shutil.copyfile(curr_f, cached_f)

    return ret


def check_conf_dir(conf=CONF):
    """If config directory doesn't exist, create it.
    """
    if not os.path.exists(expanduser(conf)):
        os.makedirs(expanduser(conf))
        print "Config directory created at {}".format(conf)

def main():
    root_dir = REQUIREMENTS_ROOT_DIR
    create_venv_conf = False
    # Auto-recognition of a venv should come as an option,
    # not to interfere with normal command (install a global package).
    # if os.environ.get("VIRTUAL_ENV") is not None:
    #     create_venv_conf = True
    #     dir_name = os.path.realpath("./").split("/")[-1]
    #     root_dir = "./"
    #     if os.path.isfile("requirements.txt"):
    #         print "found a requirements file"
    #         REQUIREMENTS_FILES["PIP"] = "requirements.txt"
    #         REQUIREMENTS_FILES["APT"] = "abelujo/apt-requirements.txt"
    #         print REQUIREMENTS_FILES, root_dir
    #         exit(0)

    #     elif os.path.isfile(join(dir_name, "requirements.txt")):
    #         print "req in project file, like django."
    #         REQUIREMENTS_FILES["PIP"] = join(dir_name, "requirements.txt")
    #         print REQUIREMENTS_FILES, root_dir

    # else:
    if True:
        print "not in venv"
        print REQUIREMENTS_FILES, root_dir

    # exit(0)

    check_conf_dir(create_venv_conf=create_venv_conf)
    #TODO: pass root_dir to sync_packages, but not with map. partial application !
    ret_codes = []
    for val in REQUIREMENTS_FILES.values():
        ret_codes.append(sync_packages(val, root_dir=root_dir))

    return reduce(operator.or_, ret_codes)

if __name__ == "__main__":
    exit(main())
