#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import functools

from tornado.web import MissingArgumentError
from tornado_json.exceptions import APIError
from tornado_json.requesthandlers import APIHandler

from cms import config
from cms.db import ScopedSession
from ..logic.user import get_user_or_404


def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        api_key = self.request.headers.get(BaseAPIHandler.API_KEY_HEADER, None)
        if api_key != config.integration_api_key:
            raise APIError(403, "Invalid API key.")
        return method(self, *args, **kwargs)
    return wrapper


class BaseAPIHandler(APIHandler):

    API_KEY_HEADER = "x-integration-api-key"

    def __init__(self, *args, **kwargs):
        super(BaseAPIHandler, self).__init__(*args, **kwargs)
        self.session = None

    def prepare(self):
        super(BaseAPIHandler, self).prepare()

        if self.request.body == "":
            self.request.body = "{}"

        self.session = ScopedSession()

    def get_required_argument(self, name):
        try:
            return self.get_argument(name)
        except MissingArgumentError:
            raise APIError(400, "Query argument \"{}\" required.".format(name))

    def get_user_or_404(self, username):
        return get_user_or_404(self.session, username)
