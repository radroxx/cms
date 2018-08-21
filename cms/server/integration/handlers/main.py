#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from uuid import uuid4

from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from tornado_json import schema
from tornado_json.exceptions import APIError

from cms.db import User, Contest, Participation, Task
from cms.grading import task_score
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
                "contest": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "score": {"type": "number"},
                        "tasks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
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
        user = self.session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise APIError(404, "User not found.")

        data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email if user.email else "",
            "timezone": user.timezone if user.timezone else "",
            "preferred_languages": user.preferred_languages,
        }

        contest_id = self.get_argument('contest_id', None)
        if contest_id is None:
            return data

        participation = self.session.query(Participation).filter(
            and_(Participation.contest_id == contest_id,
                 Participation.user_id == user_id)).options(
            joinedload('submissions')).options(
            joinedload('submissions.token')).options(
            joinedload('submissions.results')).first()
        if participation is None:
            raise APIError(404, "Participation not found.")

        tasks = self.session.query(Task).filter(
            Task.contest_id == contest_id).all()

        g_score = 0.0
        tasks_data = []
        for task in tasks:
            t_score, _ = task_score(participation, task)
            t_score = round(t_score, task.score_precision)
            g_score += t_score
            tasks_data.append({"id": task.id, "score": t_score})

        data["contest"] = {
            "id": int(contest_id),
            "score": g_score,
            "tasks": tasks_data,
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
            raise APIError(409, "User with such username already exist.")

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
                "contest_id": {
                    "anyOf": [
                        {"type": "integer"},
                        {"type": "null"},
                    ],
                },
            },
            "required": ["contest_id", ]
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

        session_id = uuid4().hex
        login_info = {
            "user_id": user_id,
            "contest_id": self.body.get("contest_id", None),
        }
        set_session(session_id, login_info)

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
        contest_id = self.body["contest_id"]
        contest = self.session.query(Contest).filter(Contest.id == contest_id).first()
        if contest is None:
            raise APIError(404, "Contest not found.")

        user = self.session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise APIError(404, "User not found.")

        participation = Participation(contest=contest, user=user)
        self.session.add(participation)
        self.session.commit()

        return {"participation_id": participation.id}
