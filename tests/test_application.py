# -*- coding: utf-8 -*-
# Pitivi video editor
# Copyright (c) 2014, Alex Băluț <alexandru.balut@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA 02110-1301, USA.
"""Tests for the application module."""
# pylint: disable=missing-docstring,protected-access,no-self-use
from unittest import mock

from pitivi import application
from pitivi import configure
from tests import common


class TestPitivi(common.TestCase):

    def call_version_info_received(self, version_info):
        app = application.Pitivi()
        giofile = mock.Mock()
        giofile.load_contents_finish.return_value = (True, version_info)
        app._version_info_received_cb(giofile, result=None, user_data=None)
        return app

    def test_version_info(self):
        app = application.Pitivi()
        self.assertTrue(app.isLatest())

        app = self.call_version_info_received("invalid")
        self.assertTrue(app.isLatest())

        app = self.call_version_info_received(
            "%s=CURRENT" % configure.VERSION)
        self.assertTrue(app.isLatest())
        self.assertEqual(configure.VERSION, app.getLatest())

        app = self.call_version_info_received(
            "%s=current\n0=supported" % configure.VERSION)
        self.assertTrue(app.isLatest())
        self.assertEqual(configure.VERSION, app.getLatest())

        app = self.call_version_info_received("999.0=CURRENT")
        self.assertFalse(app.isLatest())
        self.assertEqual("999.0", app.getLatest())

        app = self.call_version_info_received(
            "999.0=CURRENT\n%s=SUPPORTED" % configure.VERSION)
        self.assertFalse(app.isLatest())
        self.assertEqual("999.0", app.getLatest())

        app = self.call_version_info_received("0.91=current")
        self.assertTrue(app.isLatest())
        self.assertEqual("0.91", app.getLatest())

        app = self.call_version_info_received("9999.00000000=current")
        self.assertFalse(app.isLatest())
        self.assertEqual("9999.00000000", app.getLatest())

    def test_inhibition(self):
        app = application.Pitivi()

        # Check simple_inhibit.
        with mock.patch.object(app, "inhibit") as inhibit_mock:
            inhibit_mock.return_value = 1
            app.simple_inhibit("reason1", "flags1")
            inhibit_mock.return_value = 2
            app.simple_inhibit("reason2", "flags2")
            self.assertEqual(inhibit_mock.call_count, 2)

            inhibit_mock.reset_mock()
            app.simple_inhibit("reason1", "flags1.1")
            self.assertFalse(inhibit_mock.called)

        # Check simple_uninhibit.
        with mock.patch.object(app, "uninhibit") as uninhibit_mock:
            uninhibit_mock.reset_mock()
            app.simple_uninhibit("reason1")
            uninhibit_mock.assert_called_once_with(1)

            uninhibit_mock.reset_mock()
            app.simple_uninhibit("reason1")
            self.assertFalse(uninhibit_mock.called)

            uninhibit_mock.reset_mock()
            app.simple_uninhibit("reason2")
            uninhibit_mock.assert_called_once_with(2)

            uninhibit_mock.reset_mock()
            app.simple_uninhibit("reason2")
            self.assertFalse(uninhibit_mock.called)

            app.simple_uninhibit("reason3")
            self.assertFalse(uninhibit_mock.called)

        # Check again simple_inhibit.
        with mock.patch.object(app, "inhibit") as inhibit_mock:
            app.simple_inhibit("reason1", "flags1")
            self.assertTrue(inhibit_mock.called)
