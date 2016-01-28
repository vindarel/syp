#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from unittest import main
from unittest import mock

import syp

class Test(TestCase):
    """We mock the calls to methods that have IO.
    """

    def setUp(self):
        self.packages = ["rst", "two_pack"]
        self.syp = syp
        self.syp.check_file_and_get_package_list = mock.MagicMock(return_value=self.packages)
        self.syp.copy_file = mock.MagicMock()
        self.syp.run_package_manager = mock.MagicMock(return_value=0)
        self.syp.check_conf_dir = mock.MagicMock()
        self.syp.get_conf_file = mock.MagicMock() #TODO: side_effect

    def test_nominal(self):
        ret = syp.main(["a_package"])
        assert self.syp.check_file_and_get_package_list.call_count == \
            len(self.syp.REQUIREMENTS_FILES) * 2
        self.assertEqual(0, ret)

class TestUtils(TestCase):

    def setUp(self):
        pass

    def test_lines_filter_comments(self):
        lines = ["# comment", "package"]
        ret = syp.filter_packages(lines)
        self.assertEqual(ret, ["package"])

        lines = ["package # comment inline"]
        self.assertEqual(["package"], syp.filter_packages(lines))

    def test_get_diff(self):
        cached = ["rst"]
        conf = []
        self.assertEqual( ([], ["rst"]), syp.get_diff(cached, conf))

        conf = ["rst", "foo"]
        cached = ["foo"]
        # tuple (to install / to delete)
        self.assertEqual( (["rst"], []), syp.get_diff(cached, conf))

    def test_shell_cmd(self):
        syp.REQUIREMENTS_FILES =  {
            "apt": "apt.txt",
            "npm": "npm.txt",
            "ruby": "ruby.txt",
            "pip": "pip.txt",
        }
        self.assertEqual("sudo pip install", syp.get_shell_cmd("pip.txt"))


if __name__ == "__main__":
    main()
