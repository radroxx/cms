#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from tornado_json.exceptions import APIError

from cms.db import User, Contest, Participation, Task
from cms.grading import task_score


def get_user_or_404(session, username):
    user = session.query(User).filter(User.username == username).first()
    if user is None:
        raise APIError(404, "User not found.")

    return user


def create_user(session, username, first_name="", last_name="", password="",
                email=None, timezone=None, preferred_languages="[]"):
    user = session.query(User).filter(User.username == username).first()
    if user is not None:
        raise APIError(409, "User with such username already exist.")

    user = User(
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password,
        email=email,
        timezone=timezone,
        preferred_languages=preferred_languages,
    )
    session.add(user)
    session.commit()

    return user


def change_user(session, user, username, first_name="", last_name="", password="",
                email=None, timezone=None, preferred_languages="[]"):
    if user.username != username:
        new_user = session.query(User).filter(User.username == username).first()
        if new_user is not None:
            raise APIError(409, "User with such username already exist.")

    user.username = username
    user.first_name = first_name
    user.last_name = last_name
    user.password = password
    user.email = email
    user.timezone = timezone
    user.preferred_languages = preferred_languages
    session.add(user)
    session.commit()

    return user


def create_participation(session, user, contest_id):
    if not isinstance(user, User):
        user = get_user_or_404(session, user)

    contest = session.query(Contest).filter(Contest.id == contest_id).first()
    if contest is None:
        raise APIError(404, "Contest not found.")

    participation = session.query(Participation).filter(
        and_(Participation.user_id == user.id,
             Participation.contest_id == contest.id)).first()
    if participation is not None:
        raise APIError(409, "Participation with such username and contest_id "
                            "already exist.")

    participation = Participation(contest=contest, user=user)
    session.add(participation)
    session.commit()

    return participation


def get_user_info(session, user):
    if not isinstance(user, User):
        user = get_user_or_404(session, user)

    data = {
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "email": user.email if user.email else "",
        "timezone": user.timezone if user.timezone else "",
        "preferred_languages": user.preferred_languages,
    }

    return data


def get_participation_info(session, user, contest_id):
    if not isinstance(user, User):
        user = get_user_or_404(session, user)

    participation = session.query(Participation).filter(
        and_(Participation.contest_id == contest_id,
             Participation.user_id == user.id)).options(
        joinedload("submissions")).options(
        joinedload("submissions.token")).options(
        joinedload("submissions.results")).first()
    if participation is None:
        raise APIError(404, "Participation not found.")

    tasks = session.query(Task).filter(
        Task.contest_id == contest_id).all()

    g_score = 0.0
    tasks_data = []
    for task in tasks:
        t_score, _ = task_score(participation, task)
        t_score = round(t_score, task.score_precision)
        g_score += t_score
        tasks_data.append({"task_id": task.id, "score": t_score})

    data = {
        "contest_id": int(contest_id),
        "score": g_score,
        "tasks": tasks_data,
    }

    return data
