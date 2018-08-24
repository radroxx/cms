#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from .main import (
    GetUserHandler,
    CreateUserHandler,
    CreateUserSessionHandler,
    CreateUserParticipationHandler,
)


HANDLERS = [
    (r"/get_user", GetUserHandler),
    (r"/create_user", CreateUserHandler),
    (r"/create_session", CreateUserSessionHandler),
    (r"/create_participation", CreateUserParticipationHandler),
]
