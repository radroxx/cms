#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from uuid import uuid4

from tornado.web import HTTPError
from tornado_json import schema

from cms.db import User
from cms.redis import set_session
from .base import BaseAPIHandler, authenticated


class UserHandler(BaseAPIHandler):

    @authenticated
    @schema.validate(
        output_schema={
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "username": {"type": "string"},
                "email": {"type": "string"},
                "timezone": {"type": "string"},
                "preferred_languages": {"type": "string"},
            },
        },
    )
    def get(self, user_id):
        user = self.session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPError(404)

        data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email if user.email else "",
            "timezone": user.timezone if user.timezone else "",
            "preferred_languages": user.preferred_languages,
        }

        return data


class UserListHandler(BaseAPIHandler):

    @authenticated
    @schema.validate(
        input_schema={
            "type": "object",
            "properties": {
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "username": {"type": "string"},
                "password": {"type": "string"},
                "email": {"type": "string"},
                "timezone": {"type": "string"},
                "preferred_languages": {"type": "string"},
            },
            "required": ["username", "password", ]
        },
        output_schema={
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
            }
        },
    )
    def post(self):
        username = self.body.get("username", "")
        user = self.session.query(User).filter(User.username == username).first()
        if user is not None:
            raise HTTPError(409)

        user = User(
            username=username,
            first_name=self.body.get("first_name", ""),
            last_name=self.body.get("last_name", ""),
            password=self.body.get("password", ""),
            email=self.body.get("email", None),
            timezone=self.body.get("timezone", None),
            preferred_languages=self.body.get("preferred_languages", "[]"),
        )
        self.session.add(user)
        self.session.commit()

        return {"id": user.id}


class UserSessionsHandler(BaseAPIHandler):

    @authenticated
    @schema.validate(
        input_schema={
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "used_password": {"type": "string"},
            },
            "required": ["username", "used_password", ]
        },
        output_schema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
            }
        },
    )
    def post(self, user_id):
        user = self.session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPError(404)

        session_id = uuid4().hex
        login_info = {
            "username": user.username,
            "used_password": self.body["used_password"],
        }
        set_session(session_id, login_info)

        return {"session_id": session_id}
