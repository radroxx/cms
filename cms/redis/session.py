#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json
import logging

from redis import (
    Redis,
    ResponseError as RedisResponseError,
    ConnectionError as RedisConnectionError
)

from cms import config
from cmscommon.crypto import get_hex_random_key


logger = logging.getLogger(__name__)
cms_redis = Redis().from_url(config.redis)


def redis_decorator(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (RedisResponseError, RedisConnectionError) as e:
            logger.exception(e)
    return wrapped


@redis_decorator
def get_session(session_id):
    value = cms_redis.get(session_id)
    if value is not None:
        value = json.loads(value)
    return value


@redis_decorator
def set_session(value, session_id=None, expired=config.session_duration):
    if session_id is None:
        session_id = get_hex_random_key()
    if value is not None:
        value = json.dumps(value)
    cms_redis.set(session_id, value, ex=expired)
    return session_id


@redis_decorator
def delete_session(session_id):
    cms_redis.delete(session_id)
    return True
