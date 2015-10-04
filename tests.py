#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from unittest import main

import meminstall

class Test(TestCase):

    def setUp(self):
        pass

    def test_nominal(self):
        pass
        # ret = meminstall.main(["a_package"])

class TestUtils(TestCase):

    def setUp(self):
        pass

    def test_lines_filter_comments(self):
        lines = ["# comment", "package"]
        ret = meminstall.get_packages(lines)
        self.assertEqual(ret, ["package"])

        lines = ["package # comment inline"]
        self.assertEqual(["package"], meminstall.get_packages(lines))

    def test_get_diff(self):
        cached = ["rst"]
        conf = []
        self.assertEqual( ([], ["rst"]), meminstall.get_diff(cached, conf))

        conf = ["rst", "foo"]
        cached = ["foo"]
        # tuple (to install / to delete)
        self.assertEqual( (["rst"], []), meminstall.get_diff(cached, conf))

    def test_shell_cmd(self):
        meminstall.REQUIREMENTS_FILES =  {
            "APT": "apt-all.txt",
            "NPM": "npm-requirements.txt",
            "RUBY": "ruby/ruby-packages.txt",
            "PIP": "pip.txt",
        }
        self.assertEqual("sudo pip install", meminstall.get_shell_cmd("pip.txt"))


if __name__ == "__main__":
    main()

# parser.add_argument('-v', '--verbose', action='count', default=0)
# parser.add_argument('-q', '--quiet', action='count', default=0)

# logging_level = logging.WARN + 10*args.quiet - 10*args.verbose

# script -vv -> DEBUG
# script -v -> INFO
# script -> WARNING
# script -q -> ERROR
# script -qq -> CRITICAL
# script -qqq -> no logging at all
