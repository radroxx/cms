#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from tornado_json import schema
from tornado_json.exceptions import APIError

from cms.db import User
from cms.redis import set_session
from .base import BaseAPIHandler, authenticated
from ..logic.user import (
    create_user, create_participation,
    get_user_info, get_participation_info,
)


class UserHandler(BaseAPIHandler):

    @authenticated
    @schema.validate(
        output_schema={
            "type": "object",
            "properties": {
                "user_id": {"type": "integer"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "username": {"type": "string"},
                "email": {"type": "string"},
                "timezone": {"type": "string"},
                "preferred_languages": {"type": "string"},
                "contest": {
                    "type": "object",
                    "properties": {
                        "contest_id": {"type": "integer"},
                        "score": {"type": "number"},
                        "tasks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "task_id": {"type": "integer"},
                                    "score": {"type": "number"},
                                },
                            },
                        },
                    },
                },
            },
        },
    )
    def get(self, user_id):
        result = get_user_info(self.session, user_id)

        contest_id = self.get_argument('contest_id', None)
        if contest_id is None:
            return result

        result["contest"] = get_participation_info(
            self.session, user_id, contest_id)

        return result


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
                "contest_id": {"type": "integer"},
            },
            "required": ["username", "password", ]
        },
        output_schema={
            "type": "object",
            "properties": {
                "user_id": {"type": "integer"},
                "participation_id": {"type": "integer"},
            }
        },
    )
    def post(self):
        user_id = create_user(
            self.session,
            self.body.get("username", ""),
            self.body.get("first_name", ""),
            self.body.get("last_name", ""),
            self.body.get("password", ""),
            self.body.get("email", None),
            self.body.get("timezone", None),
            self.body.get("preferred_languages", "[]"),
        )
        result = {"user_id": user_id}

        contest_id = self.body.get("contest_id", None)
        if contest_id is not None:
            participation_id = create_participation(
                self.session, user_id, contest_id)
            result["participation_id"] = participation_id

        return result


class UserSessionsHandler(BaseAPIHandler):

    @authenticated
    @schema.validate(
        input_schema={
            "type": "object",
            "properties": {
                "contest_id": {
                    "anyOf": [
                        {"type": "integer"},
                        {"type": "null"},
                    ],
                },
            },
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
            raise APIError(404, "User not found.")

        login_info = {
            "user_id": user_id,
            "contest_id": self.body.get("contest_id", None),
        }
        session_id = set_session(login_info)

        return {"session_id": session_id}


class UserParticipationsHandler(BaseAPIHandler):

    @authenticated
    @schema.validate(
        input_schema={
            "type": "object",
            "properties": {
                "contest_id": {"type": "integer"},
            },
            "required": ["contest_id", ]
        },
        output_schema={
            "type": "object",
            "properties": {
                "participation_id": {"type": "integer"},
            }
        },
    )
    def post(self, user_id):
        participation_id = create_participation(
            self.session, user_id, self.body["contest_id"])

        return {"participation_id": participation_id}
