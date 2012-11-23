# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2010, 2011, 2012, 2013, 2014, 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
BibSword Client DBLayer.
"""

import time
from invenio.dateutils import convert_datestruct_to_datetext
from invenio.dbquery import run_sql


# CREATE TABLE `swrCLIENTTEMPSUBMISSION` (
#   `id` varchar(128) NOT NULL,
#   `object` longblob NOT NULL,
#   `last_updated` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
#   PRIMARY KEY (`id`)
# )


def store_temp_submission(
    sid,
    sobject_blob
):
    """
    Store the temporary submission.
    """

    query = """
    INSERT INTO swrCLIENTTEMPSUBMISSION
                (id, object, last_updated)
    VALUES      (%s, %s, %s)
    """

    now = convert_datestruct_to_datetext(time.localtime())
    params = (sid, sobject_blob, now)

    try:
        res = run_sql(query, params)
    except Exception:
        return False
    else:
        return True


def retrieve_temp_submission(
    sid
):
    """
    Retrieve the temporary submission.
    """

    query = """
    SELECT  object
    FROM    swrCLIENTTEMPSUBMISSION
    WHERE   id=%s
    """

    params = (sid,)

    res = run_sql(query, params)

    if res:
        return res[0][0]
    else:
        return None


def update_temp_submission(
    sid,
    sobject_blob
):
    """
    Update the temporary submission.
    """

    query = """
    UPDATE  swrCLIENTTEMPSUBMISSION
    SET     object=%s,
            last_updated=%s
    WHERE   id=%s
    """

    now = convert_datestruct_to_datetext(time.localtime())
    params = (sobject_blob, now, sid)

    res = run_sql(query, params)

    return res


def delete_temp_submission(
    sid
):
    """
    Delete the temporary submission.
    """

    query = """
    DELETE FROM swrCLIENTTEMPSUBMISSION
    WHERE       id=%s
    """

    params = (sid,)

    res = run_sql(query, params)

    return res


# CREATE TABLE `swrCLIENTSUBMISSION` (
#   `id_user` int(15) unsigned NOT NULL,
#   `id_record` mediumint(8) unsigned NOT NULL,
#   `id_server` int(11) unsigned NOT NULL,
#   `url_alternate` varchar(256) NOT NULL DEFAULT '',
#   `url_edit` varchar(256) NOT NULL DEFAULT '',
#   `status` varchar(256) NOT NULL DEFAULT '',
#   `submitted` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
#   `last_updated` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
#   PRIMARY KEY (`id_record`,`id_server`)
# )


def archive_submission(
    user_id,
    record_id,
    server_id,
    alternate_url,
    edit_url
):
    """
    Archive the given submission.
    """

    query = """
    INSERT INTO swrCLIENTSUBMISSION
                (
                    id_user,
                    id_record,
                    id_server,
                    url_alternate,
                    url_edit,
                    submitted
                )
    VALUES      (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
    """

    now = convert_datestruct_to_datetext(time.localtime())
    params = (
        user_id,
        record_id,
        server_id,
        alternate_url,
        edit_url,
        now
    )

    try:
        res = run_sql(query, params)
    except Exception:
        return False
    else:
        return True


def is_submission_archived(
    record_id,
    server_id,
):
    """
    If the given record has already been archived to the given server
    return True, otherwise return False.
    """

    query = """
    SELECT  COUNT(id_record)
    FROM    swrCLIENTSUBMISSION
    WHERE   id_record=%s
        AND id_server=%s
    """

    params = (
        record_id,
        server_id,
    )

    res = run_sql(query, params)

    return bool(res[0][0])


def get_submissions(
    with_dict=False
):
    """
    Get the Sword client submissions.
    """

    query = """
    SELECT      user.nickname,
                swrCLIENTSUBMISSION.id_record,
                swrCLIENTSUBMISSION.id_server,
                swrCLIENTSERVER.name,
                swrCLIENTSUBMISSION.submitted,
                swrCLIENTSUBMISSION.status,
                swrCLIENTSUBMISSION.last_updated,
                swrCLIENTSUBMISSION.url_alternate
    FROM        swrCLIENTSUBMISSION
    JOIN        swrCLIENTSERVER
            ON  swrCLIENTSUBMISSION.id_server = swrCLIENTSERVER.id
    JOIN        user
            ON  swrCLIENTSUBMISSION.id_user = user.id
    ORDER BY    swrCLIENTSUBMISSION.submitted DESC
    """

    params = None

    result = run_sql(query, params, with_dict=with_dict)

    return result


# CREATE TABLE `swrCLIENTSERVER` (
#  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
#  `name` varchar(64) NOT NULL,
#  `engine` varchar(64) NOT NULL,
#  `username` varchar(64) NOT NULL,
#  `password` varchar(64) NOT NULL,
#  `email` varchar(64) NOT NULL,
#  `service_document_parsed` longblob,
#  `update_frequency` varchar(16) NOT NULL,
#  `last_updated` timestamp DEFAULT 0,
#  PRIMARY KEY (`id`)
# )


def get_servers(
    server_id=None,
    with_dict=False
):
    """
    Get the Sword client servers.

    Given a server_id, get that server only.
    """

    query = """
    SELECT  id AS server_id,
            name,
            engine,
            username,
            password,
            email,
            service_document_parsed,
            update_frequency,
            last_updated
    FROM    swrCLIENTSERVER
    """

    if server_id is not None:
        query += """
        WHERE   id=%s
        """
        params = (server_id,)
    else:
        params = None

    result = run_sql(query, params, with_dict=with_dict)

    return result


def delete_servers(
    server_id=None
):
    """
    Delete the Sword client servers.

    Given a server_id, delete that server only.
    """

    query = """
    DELETE
    FROM    swrCLIENTSERVER
    """

    if server_id is not None:
        query += """
        WHERE   id=%s
        """
        params = (server_id,)
    else:
        params = None

    result = run_sql(query, params)

    return result


def modify_server(
    server_id,
    server_name,
    server_engine,
    server_username,
    server_password,
    server_email,
    server_update_frequency
):
    """
    Modify the Sword client server.

    Given a server_id.
    """

    query = """
    UPDATE  swrCLIENTSERVER
    SET     name=%s,
            engine=%s,
            username=%s,
            password=%s,
            email=%s,
            update_frequency=%s
    WHERE   id=%s
    """

    params = (
        server_name,
        server_engine,
        server_username,
        server_password,
        server_email,
        server_update_frequency,
        server_id,
    )

    result = run_sql(query, params)

    return result


def add_server(
    server_name,
    server_engine,
    server_username,
    server_password,
    server_email,
    server_update_frequency
):
    """
    Add a Sword client server based on the given information.
    """

    query = """
    INSERT INTO swrCLIENTSERVER
                (name,
                 engine,
                 username,
                 password,
                 email,
                 update_frequency)
    VALUES      (%s,
                 %s,
                 %s,
                 %s,
                 %s,
                 %s)
    """

    params = (
        server_name,
        server_engine,
        server_username,
        server_password,
        server_email,
        server_update_frequency,
    )

    try:
        result = run_sql(query, params)
    except:
        result = None

    return result
