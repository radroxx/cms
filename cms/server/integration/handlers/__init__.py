#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from .main import UserHandler, UserListHandler, UserSessionsHandler


HANDLERS = [
    (r"/users", UserListHandler),
    (r"/users/([0-9]+)", UserHandler),
    (r"/users/([0-9]+)/sessions", UserSessionsHandler),
]
