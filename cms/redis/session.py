#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import logging

from redis import (
    Redis,
    ResponseError as RedisResponseError,
    ConnectionError as RedisConnectionError
)

from cms import config

logger = logging.getLogger(__name__)
cms_redis = Redis().from_url(config.redis)


def redis_decorator(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (RedisResponseError, RedisConnectionError) as e:
            logger.error(e)
    return wrapped


@redis_decorator
def get_session(key):
    value = cms_redis.get(key)
    if value is not None:
        value = json.loads(value)
    return value


@redis_decorator
def set_session(key, value, expired=config.session_duration):
    if value is not None:
        value = json.dumps(value)
    cms_redis.set(key, value, ex=expired)


@redis_decorator
def delete_session(key):
    cms_redis.delete(key)
