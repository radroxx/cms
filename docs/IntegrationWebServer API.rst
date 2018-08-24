IntegrationWebServer API description
************************************

Required headers
================

``x-integration-api-key`` - API secret key used for authorization.

Get user info
=============

URL: ``/get_user``

Method: ``GET``

Query parameters:

*   Required:

    * ``username`` - Username of the user to retrieve info.

*   Not required:

    * ``contest_id`` - Specify ID of contest if you want to get score info for the user.

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

URL: ``/create_user``

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

Notes:

* ``contest_id`` - Specify ID of contest if you want to create new participation in place.

Create new participation
========================

URL: ``/create_participation``

Method: ``POST``

JSON schema:

.. sourcecode:: python

    input_schema={
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "contest_id": {"type": "integer"},
        },
        "required": ["username", "contest_id", ]
    }

    output_schema={
        "type": "object",
        "properties": {
            "participation_id": {"type": "integer"},
        }
    }

Create new session for user authentication
==========================================

URL: ``/create_session``

Method: ``POST``

JSON schema:

.. sourcecode:: python

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
    }

    output_schema={
        "type": "object",
        "properties": {
            "session_id": {"type": "string"},
        }
    }

Notes:

* ``contest_id`` - Specify ID of contest if you want to create a contest-specific session.
