IntegrationWebServer API description
************************************

Get user info
=============

URL: ``/users/<user_id>``

Method: ``GET``

Query parameters:

* ``contest_id`` - Specify ID of contest to get score info for the user. [Not required]

JSON schema:

.. sourcecode:: python

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
    }

Create new user
===============

URL: ``/users``

Method: ``POST``

JSON schema:

.. sourcecode:: python

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
    }

    output_schema={
        "type": "object",
        "properties": {
            "user_id": {"type": "integer"},
            "participation_id": {"type": "integer"},
        }
    }

Create new participation
========================

URL: ``/users/<user_id>/participations``

Method: ``POST``

JSON schema:

.. sourcecode:: python

    input_schema={
        "type": "object",
        "properties": {
            "contest_id": {"type": "integer"},
        },
        "required": ["contest_id", ]
    }

    output_schema={
        "type": "object",
        "properties": {
            "participation_id": {"type": "integer"},
        }
    }

Create new session for user authentication
==========================================

URL: ``/users/<user_id>/sessions``

Method: ``POST``

JSON schema:

.. sourcecode:: python

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
    }

    output_schema={
        "type": "object",
        "properties": {
            "session_id": {"type": "string"},
        }
    }
