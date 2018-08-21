#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging

from cms import ConfigError, config
from cms.io import WebService

from .handlers import HANDLERS


logger = logging.getLogger(__name__)


class IntegrationWebServer(WebService):
    """Service that runs the web server serving the integration API.
    """
    def __init__(self, shard):
        parameters = {
            "debug": config.tornado_debug,
        }

        try:
            listen_address = config.integration_listen_address[shard]
            listen_port = config.integration_listen_port[shard]
        except IndexError:
            raise ConfigError(
                "Wrong shard number for %s, or missing address/port "
                "configuration. Please check integration_listen_address "
                "and integration_listen_port in cms.conf." % __name__)

        super(IntegrationWebServer, self).__init__(
            listen_port,
            HANDLERS,
            parameters,
            shard=shard,
            listen_address=listen_address
        )
