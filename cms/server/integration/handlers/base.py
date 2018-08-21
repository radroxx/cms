#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import functools

from tornado_json.exceptions import APIError
from tornado_json.requesthandlers import APIHandler

from cms import config
from cms.db import ScopedSession


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
        self.session = ScopedSession()
