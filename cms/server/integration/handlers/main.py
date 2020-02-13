#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from tornado_json import schema

from cms.redis import set_session
from .base import BaseAPIHandler, authenticated
from ..logic.user import (
    create_user,
    change_user,
    create_participation,
    get_user_info,
    get_participation_info,
)


class GetUserHandler(BaseAPIHandler):

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
                "preferred_languages": {"type": "array","items":{"type":"string"}},
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
    def get(self):
        username = self.get_required_argument("username")
        user = self.get_user_or_404(username)

        result = get_user_info(self.session, user)

        contest_id = self.get_argument("contest_id", None)
        if contest_id is None:
            return result

        result["contest"] = get_participation_info(
            self.session, user, contest_id)

        return result


class CreateUserHandler(BaseAPIHandler):

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
                "preferred_languages": {"type": "array","items":{"type":"string"}},
                "contest_id": {"type": "integer"},
                "hash_method": {"enum": ["bcrypt", "plaintext"]},
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
        user = create_user(
            self.session,
            self.body.get("username", ""),
            self.body.get("first_name", ""),
            self.body.get("last_name", ""),
            self.body.get("password", ""),
            self.body.get("email", None),
            self.body.get("timezone", None),
            self.body.get("preferred_languages", []),
            self.body.get("hash_method", "bcrypt"),
        )
        result = {"user_id": user.id}

        contest_id = self.body.get("contest_id", None)
        if contest_id is not None:
            participation = create_participation(
                self.session, user, contest_id)
            result["participation_id"] = participation.id
            self.application.service.proxy_service.reinitialize()

        return result


class ChangeUserHandler(BaseAPIHandler):

    @authenticated
    @schema.validate(
        input_schema={
            "type": "object",
            "properties": {
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "username": {"type": "string"},
                "new_username": {"type": "string"},
                "password": {"type": "string"},
                "email": {"type": "string"},
                "timezone": {"type": "string"},
                "preferred_languages": {"type": "array","items":{"type":"string"}},
                "hash_method": {"enum": ["bcrypt", "plaintext"]},
            },
            "required": ["username", ]
        },
        output_schema={
            "type": "object",
            "properties": {
                "user_id": {"type": "integer"},
            }
        },
    )
    def patch(self):
        user = self.get_user_or_404(self.body["username"])

        user = change_user(
            self.session,
            user,
            self.body.get("new_username", user.username),
            self.body.get("first_name", user.first_name),
            self.body.get("last_name", user.last_name),
            self.body.get("password", user.password),
            self.body.get("email", user.email),
            self.body.get("timezone", user.timezone),
            self.body.get("preferred_languages", user.preferred_languages),
            self.body.get("hash_method", "bcrypt"),
        )
        result = {"user_id": user.id}
        self.application.service.proxy_service.reinitialize()

        return result


class CreateUserSessionHandler(BaseAPIHandler):

    @authenticated
    @schema.validate(
        input_schema={
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "contest_id": {
                    "anyOf": [
                        {"type": "integer"},
                        {"type": "null"},
                    ],
                },
            },
            "required": ["username", ]
        },
        output_schema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
            }
        },
    )
    def post(self):
        user = self.get_user_or_404(self.body["username"])

        login_info = {
            "user_id": user.id,
            "contest_id": self.body.get("contest_id", None),
        }
        session_id = set_session(login_info)

        return {"session_id": session_id}


class CreateUserParticipationHandler(BaseAPIHandler):

    @authenticated
    @schema.validate(
        input_schema={
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "contest_id": {"type": "integer"},
            },
            "required": ["username", "contest_id", ]
        },
        output_schema={
            "type": "object",
            "properties": {
                "participation_id": {"type": "integer"},
            }
        },
    )
    def post(self):
        participation = create_participation(
            self.session, self.body["username"], self.body["contest_id"])
        self.application.service.proxy_service.reinitialize()

        return {"participation_id": participation.id}
