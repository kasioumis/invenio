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
Base class for the SWORD client servers.
"""

import urllib2
from socket import getdefaulttimeout, setdefaulttimeout
from mimetypes import guess_all_extensions
from tempfile import NamedTemporaryFile
from datetime import datetime, timedelta
import re

from invenio.config import CFG_TMPDIR
from invenio.dbquery import(
    run_sql,
    serialize_via_marshal,
    deserialize_via_marshal
)
from invenio.dateutils import(
    convert_datestruct_to_datetext
)

from invenio.bibsword_config import \
    CFG_BIBSWORD_USER_AGENT, \
    CFG_BIBSWORD_FILE_TYPES_MAPPING, \
    CFG_BIBSWORD_DEFAULT_TIMEOUT, \
    CFG_BIBSWORD_FORCE_DEFAULT_TIMEOUT, \
    CFG_BIBSWORD_ATOM_ENTRY_MIME_TYPE


class SwordClientServer(object):
    """
    Base class for the SWORD client servers.
    Missing funcionality needs to be extended by specific implementations.
    """

    def __init__(self, settings):
        """
        Initialize the object by setting the instance variables,
        decompressing the parsed service document and
        preparing the auth handler.
        """

        # We expect to have the following instance variables:
        # self.server_id (int)
        # self.name (str)
        # self.username (str)
        # self.password (str)
        # self.email (str)
        # self.service_document_parsed (blob)
        # self.update_frequency (str)
        # self.last_updated (str/timestamp)
        # self.realm (str)
        # self.uri (str)
        # self.service_document_url (str)

        for (name, value) in settings.iteritems():
            setattr(self, name, value)

        self._prepare_auth_handler()

        if self.service_document_parsed:
            self.service_document_parsed = deserialize_via_marshal(
                self.service_document_parsed
            )
        else:
            self.update()

    def _prepare_auth_handler(self):
        """
        """

        # create a password manager
        self._password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()

        # Add the username and password
        self._password_mgr.add_password(self.realm,
                                        self.uri,
                                        self.username,
                                        self.password)

    def _url_opener(self):
        """
        """

        # Create a basic authentication handler
        _auth_handler = urllib2.HTTPBasicAuthHandler(self._password_mgr)

        # Return a URL opener (OpenerDirector instance)
        return urllib2.build_opener(_auth_handler)

    @staticmethod
    def _get_extension_for_file_type(file_type):

        extensions = guess_all_extensions(file_type)

        if not extensions:
            def _guess_extension_for_ambiguous_file_type(ambiguous_file_type):
                return ambiguous_file_type.split('/')[-1]
            extensions = CFG_BIBSWORD_FILE_TYPES_MAPPING.get(
                file_type,
                _guess_extension_for_ambiguous_file_type(file_type))

        return extensions

    def submit(self, metadata, media, url):
        """
        """

        # Perform the media deposit
        media_response = self._deposit_media(
            metadata,
            media,
            url
        )

        # Perform the metadata submission
        metadata_response = self._ingest_metadata(
            metadata,
            media_response,
            url
        )

        # Prepare and return the final response
        response = self._prepare_response(
            media_response,
            metadata_response
        )

        return response

    def _deposit_media(self, metadata, media, url):
        """
        """

        # Hold the response for each file in the response dictionary
        response = {}

        prepared_media = self._prepare_media(media)

        for (file_index, file_info) in prepared_media.iteritems():
            headers = self._prepare_media_headers(file_info, metadata)
            try:
                file_object = open(file_info['path'], "r")
                file_contents = file_object.read()
                file_object.close()
            except Exception, e:
                response[file_index] = {
                    'error': True,
                    'msg': str(e),
                    'name': file_info['name'],
                    'mime': file_info['mime'],
                }
            else:
                req = urllib2.Request(url, file_contents, headers)
                try:
                    if CFG_BIBSWORD_FORCE_DEFAULT_TIMEOUT:
                        default_timeout = getdefaulttimeout()
                        setdefaulttimeout(CFG_BIBSWORD_DEFAULT_TIMEOUT)
                    res = self._url_opener().open(req)
                    if CFG_BIBSWORD_FORCE_DEFAULT_TIMEOUT:
                        setdefaulttimeout(default_timeout)
                except urllib2.HTTPError, e:
                    response[file_index] = {
                        'error': True,
                        'msg': self._prepare_media_response_error(e),
                        'name': file_info['name'],
                        'mime': file_info['mime'],
                    }
                except Exception, e:
                    response[file_index] = {
                        'error': True,
                        'msg': str(e),
                        'name': file_info['name'],
                        'mime': file_info['mime'],
                    }
                else:
                    response[file_index] = {
                        'error': False,
                        'msg': self._prepare_media_response(res),
                        'name': file_info['name'],
                        'mime': file_info['mime'],
                    }

        return response

    def _prepare_media(self, media):
        """
        """

        # NOTE: Implement me for each server!

        return media

    def _prepare_media_headers(self, file_info, dummy):
        """
        """

        # NOTE: Implement me for each server!

        headers = {}

        headers['Content-Type'] = file_info['mime']
        headers['Content-Length'] = file_info['size']
        headers['User-Agent'] = CFG_BIBSWORD_USER_AGENT

        return headers

    def _prepare_media_response(self, response):
        """
        """

        # NOTE: Implement me for each server!

        return response.read()

    def _prepare_media_response_error(self, error):
        """
        """

        # NOTE: Implement me for each server!

        return error

    def _ingest_metadata(self, metadata, media_response, url):
        """
        """

        response = {}

        if media_response:
            for file_response in media_response.itervalues():
                if file_response['error']:
                    response['error'] = True
                    response['msg'] = (
                        "There has been at least one error with " +
                        "the files chosen for media deposit."
                    )
                    return response
        else:
            response['error'] = True
            response['msg'] = (
                "No files were chosen for media deposit. " +
                "At least one file has to be chosen."
            )
            return response

        prepared_metadata = self._prepare_metadata(metadata, media_response)

        headers = self._prepare_metadata_headers(metadata)

        req = urllib2.Request(url, prepared_metadata, headers)
        try:
            if CFG_BIBSWORD_FORCE_DEFAULT_TIMEOUT:
                default_timeout = getdefaulttimeout()
                setdefaulttimeout(CFG_BIBSWORD_DEFAULT_TIMEOUT)
            res = self._url_opener().open(req)
            if CFG_BIBSWORD_FORCE_DEFAULT_TIMEOUT:
                setdefaulttimeout(default_timeout)
        except urllib2.HTTPError, e:
            response['error'] = True
            response['msg'] = self._prepare_metadata_response_error(e)
        except Exception, e:
            response['error'] = True
            response['msg'] = str(e)
        else:
            response['error'] = False
            response['msg'] = self._prepare_metadata_response(res)

        return response

    def _prepare_metadata(self, metadata, dummy):
        """
        """

        # NOTE: Implement me for each server!

        return metadata

    def _prepare_metadata_headers(self, dummy):
        """
        """

        # NOTE: Implement me for each server!

        headers = {}

        headers['Content-Type'] = CFG_BIBSWORD_ATOM_ENTRY_MIME_TYPE
        headers['User-Agent'] = CFG_BIBSWORD_USER_AGENT

        return headers

    def _prepare_metadata_response(self, response):
        """
        """

        # NOTE: Implement me for each server!

        return response.read()

    def _prepare_metadata_response_error(self, error):
        """
        """

        # NOTE: Implement me for each server!

        return error

    def _prepare_response(self, media_response, metadata_response):
        """
        """

        # NOTE: Implement me for each server!

        return None

    def status(self, url):
        """
        """

        response = {}

        headers = self._prepare_status_headers()

        req = urllib2.Request(url, headers=headers)

        try:
            if CFG_BIBSWORD_FORCE_DEFAULT_TIMEOUT:
                default_timeout = getdefaulttimeout()
                setdefaulttimeout(CFG_BIBSWORD_DEFAULT_TIMEOUT)
            # TODO: No need for authentication at this point,
            #       maybe use the standard url_opener?
            res = self._url_opener().open(req)
            if CFG_BIBSWORD_FORCE_DEFAULT_TIMEOUT:
                setdefaulttimeout(default_timeout)
        except urllib2.HTTPError, e:
            response['error'] = True
            response['msg'] = str(e)
        except Exception, e:
            response['error'] = True
            response['msg'] = str(e)
        else:
            response['error'] = False
            response['msg'] = self._prepare_status_response(res)
            self._store_submission_status(
                url,
                response['msg']['error'] is None and "{0}".format(
                    response['msg']['status']
                ) or "{0} ({1})".format(
                    response['msg']['status'],
                    response['msg']['error']
                )
            )

        return response

    def _prepare_status_headers(self):
        """
        """

        # NOTE: Implement me for each server!

        headers = {}

        headers['User-Agent'] = CFG_BIBSWORD_USER_AGENT

        return headers

    def _prepare_status_response(self, response):
        """
        """

        # NOTE: Implement me for each server!

        return response.read()

    def _store_submission_status(self, url, status):
        """
        Stores the submission status in the database.
        """

        query = """
        UPDATE  swrCLIENTSUBMISSION
        SET     status=%s,
                last_updated=%s
        WHERE   id_server=%s
        AND     url_alternate=%s
        """

        params = (
            status,
            convert_datestruct_to_datetext(datetime.now()),
            self.server_id,
            url,
        )

        result = run_sql(query, params)

        return result

    @staticmethod
    def _convert_frequency_to_timedelta(raw_frequency):
        """
        Converts this: "5w4d3h2m1s"
        to this: datetime.timedelta(39, 10921)
        """

        frequency_translation = {
            "w": "weeks",
            "d": "days",
            "h": "hours",
            "m": "minutes",
            "s": "seconds",
        }

        frequency_parts = re.findall(
            "([0-9]+)([wdhms]{1})",
            raw_frequency
        )

        frequency_parts = map(
            lambda p: (frequency_translation[p[1]], int(p[0])),
            frequency_parts
        )

        frequency_timedelta_parts = dict(frequency_parts)

        frequency_timedelta = timedelta(**frequency_timedelta_parts)

        return frequency_timedelta

    def needs_to_be_updated(self):
        """
        Check if the service document is out of date,
        i.e. if the "last_updated" date is more than
        "update_frequency" time in the past.
        """

        frequency_timedelta = \
            SwordClientServer._convert_frequency_to_timedelta(
                self.update_frequency
            )

        if ((self.last_updated + frequency_timedelta) < datetime.now()):
            return True

        return False

    def update(self):
        """
        Fetches the latest service document, parses it and
        saves it in the database.
        """

        service_document_raw = self._fetch_service_document()

        if service_document_raw:
            service_document_parsed = self._parse_service_document(
                service_document_raw
            )

            if service_document_parsed:
                self.service_document_parsed = service_document_parsed
                return self._store_service_document()

        return False

    def _fetch_service_document(self):
        """
        Returns the raw service document of the server.
        """

        req = urllib2.Request(self.service_document_url)
        try:
            res = self._url_opener().open(req)
        except urllib2.HTTPError:
            return None
        service_document_raw = res.read()
        res.close()

        return service_document_raw

    def _store_service_document(self):
        """
        Stores the compressed parsed service document in the database.
        """

        query = """
        UPDATE  swrCLIENTSERVER
        SET     service_document_parsed=%s,
                last_updated=%s
        WHERE   id=%s
        """

        params = (
            serialize_via_marshal(self.service_document_parsed),
            convert_datestruct_to_datetext(datetime.now()),
            self.server_id
        )

        result = run_sql(query, params)

        return result
