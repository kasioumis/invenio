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
BibSWORD Client Library.
"""

import cPickle
import json
import os
import random
import re

from invenio.bibdocfile import BibRecDocs
from invenio.bibsword_config import(
    CFG_BIBSWORD_CLIENT_SERVERS_PATH,
    CFG_BIBSWORD_LOCAL_TIMEZONE,
    CFG_BIBSWORD_MARC_FIELDS,
    CFG_BIBSWORD_MAXIMUM_NUMBER_OF_CONTRIBUTORS,
    CFG_BIBSWORD_UPDATED_DATE_MYSQL_FORMAT
)
import invenio.bibsword_client_dblayer as sword_client_db
from invenio.bibsword_client_templates import TemplateSwordClient
from invenio.config import CFG_PYLIBDIR
from invenio.errorlib import raise_exception
from invenio.messages import gettext_set_language
from invenio.pluginutils import PluginContainer
from invenio.search_engine import(
    get_modification_date,
    get_record,
    record_exists
)

sword_client_template = TemplateSwordClient()

RANDOM_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

RANDOM_RANGE = range(32)

_CLIENT_SERVERS = PluginContainer(
    os.path.join(
        CFG_PYLIBDIR,
        'invenio',
        CFG_BIBSWORD_CLIENT_SERVERS_PATH,
        '*.py'
    )
)


class BibSwordSubmission(object):
    """The BibSwordSubmission class."""

    def __init__(
        self,
        recid,
        uid,
        sid=None
    ):
        """
        The constructor. Assign the given
        or a unique temporary submission id.
        """

        self._set_recid_and_record(recid)
        self._set_sid(sid)
        self._set_uid(uid)

    def _set_uid(self, uid):
        self._uid = uid

    def get_uid(self):
        return self._uid

    def get_sid(self):
        return self._sid

    def _set_sid(self, sid=None):
        if sid is None:
            self._sid = self._get_random_id()
        else:
            self._sid = sid
        return self._sid

    def _get_random_id(self, size_range=RANDOM_RANGE, chars=RANDOM_CHARS):
        return ''.join(random.choice(chars) for i in size_range)

    def _set_recid_and_record(self, recid):
        self._recid = recid
        self._record = get_record(recid)

    def get_recid(self):
        return self._recid

    def _get_marc_field_parts(self, field):
        tag = field[0:3].lower()
        ind1 = field[3].lower().replace('_', ' ')
        ind2 = field[4].lower().replace('_', ' ')
        subfield = field[5].lower()

        return (tag, ind1, ind2, subfield)

    def get_record_title(self, force=False):

        if '_title' not in self.__dict__.keys() or force:

            self._title = ""

            (tag, ind1, ind2, subfield) = self._get_marc_field_parts(
                CFG_BIBSWORD_MARC_FIELDS['title']
            )

            for record_title in self._record.get(tag, []):
                if _decapitalize(record_title[1:3]) == (ind1, ind2):
                    for (code, value) in record_title[0]:
                        if code.lower() == subfield:
                            self._title = value
                            break
                            # Only get the first occurrence
                            break

        return self._title

    def set_record_title(self, title):
        # TODO: Should we unescape here?
        self._title = title

    def get_record_abstract(self, force=False):

        if '_abstract' not in self.__dict__.keys() or force:

            self._abstract = ""

            (tag, ind1, ind2, subfield) = self._get_marc_field_parts(
                CFG_BIBSWORD_MARC_FIELDS['abstract']
            )

            for record_abstract in self._record.get(tag, []):
                if _decapitalize(record_abstract[1:3]) == (ind1, ind2):
                    for (code, value) in record_abstract[0]:
                        if code.lower() == subfield:
                            self._abstract = value
                            break
                            # Only get the first occurrence
                            break

        return self._abstract

    def set_record_abstract(self, abstract):
        self._abstract = abstract

    def get_record_author(self, force=False):

        if '_author' not in self.__dict__.keys() or force:

            author_name = ""
            author_email = ""
            author_affiliation = ""

            (
                tag_name,
                ind1_name,
                ind2_name,
                subfield_name
            ) = self._get_marc_field_parts(
                CFG_BIBSWORD_MARC_FIELDS['author_name']
            )

            (
                tag_email,
                ind1_email,
                ind2_email,
                subfield_email
            ) = self._get_marc_field_parts(
                CFG_BIBSWORD_MARC_FIELDS['author_email']
            )

            (
                tag_aff,
                ind1_aff,
                ind2_aff,
                subfield_aff
            ) = self._get_marc_field_parts(
                CFG_BIBSWORD_MARC_FIELDS['author_affiliation']
            )

            for record_author_name in self._record.get(tag_name, []):
                if _decapitalize(record_author_name[1:3]) == (
                    ind1_name, ind2_name
                ):
                    for (code, value) in record_author_name[0]:
                        if code.lower() == subfield_name:
                            author_name = value
                            break
                    if tag_name == tag_email and (ind1_name, ind2_name) == (
                        ind1_email, ind2_email
                    ):
                        for (code, value) in record_author_name[0]:
                            if code.lower() == subfield_email:
                                author_email = value
                                break
                    if tag_name == tag_aff and (ind1_name, ind2_name) == (
                        ind1_aff, ind2_aff
                    ):
                        for (code, value) in record_author_name[0]:
                            if code.lower() == subfield_aff:
                                author_affiliation = value
                                break
                    # Only get the first occurrence
                    break

            if tag_name != tag_email or (ind1_name, ind2_name) != (
                ind1_email, ind2_email
            ):
                for record_author_email in self._record.get(tag_email, []):
                    if _decapitalize(record_author_email[1:3]) == (
                        ind1_email, ind2_email
                    ):
                        for (code, value) in record_author_email[0]:
                            if code.lower() == subfield_email:
                                author_email = value
                                break
                                # Only get the first occurrence
                                break

            if tag_name != tag_aff or (ind1_name, ind2_name) != (
                ind1_aff, ind2_aff
            ):
                for record_author_affiliation in self._record.get(tag_aff, []):
                    if _decapitalize(record_author_affiliation[1:3]) == (
                        ind1_aff, ind2_aff
                    ):
                        for (code, value) in record_author_affiliation[0]:
                            if code.lower() == subfield_aff:
                                author_affiliation = value
                                break
                                # Only get the first occurrence
                                break

            self._author = (author_name, author_email, author_affiliation)

        return self._author

    def set_record_author(
        self,
        (author_name, author_email, author_affiliation)
    ):
        self._author = (author_name, author_email, author_affiliation)

    def _equalize_lists(self, *args):

        max_len = max([len(arg) for arg in args])

        for arg in args:
            diff = max_len - len(arg)
            if diff > 0:
                arg.extend([None] * diff)

    def get_record_contributors(self, force=False):

        if '_contributors' not in self.__dict__.keys() or force:

            self._contributors = []

            contributors_names = []
            contributors_emails = []
            contributors_affiliations = []

            (
                tag_name,
                ind1_name,
                ind2_name,
                subfield_name
            ) = self._get_marc_field_parts(
                CFG_BIBSWORD_MARC_FIELDS['contributor_name']
            )

            (
                tag_aff,
                ind1_aff,
                ind2_aff,
                subfield_aff
            ) = self._get_marc_field_parts(
                CFG_BIBSWORD_MARC_FIELDS['contributor_affiliation']
            )

            for record_contributor_name in self._record.get(tag_name, []):
                contributor_name = None
                contributor_email = None
                contributor_affiliation = None
                if _decapitalize(record_contributor_name[1:3]) == (
                    ind1_name, ind2_name
                ):
                    for (code, value) in record_contributor_name[0]:
                        if code.lower() == subfield_name:
                            contributor_name = value
                            break
                    contributors_names.append(contributor_name)
                    if tag_name == tag_aff and (ind1_name, ind2_name) == (
                        ind1_aff, ind2_aff
                    ):
                        for (code, value) in record_contributor_name[0]:
                            if code.lower() == subfield_aff:
                                contributor_affiliation = value
                                break
                        contributors_affiliations.append(
                            contributor_affiliation
                        )

                if tag_name != tag_aff or (ind1_name, ind2_name) != (
                    ind1_aff, ind2_aff
                ):
                    for record_contributor_affiliation in self._record.get(
                        tag_aff, []
                    ):
                        if _decapitalize(
                            record_contributor_affiliation[1:3]
                        ) == (ind1_aff, ind2_aff):
                            for (
                                code,
                                value
                            ) in record_contributor_affiliation[0]:
                                if code.lower() == subfield_aff:
                                    contributor_affiliation = value
                                    break
                            contributors_affiliations.append(
                                contributor_affiliation
                            )

                self._equalize_lists(
                    contributors_names,
                    contributors_emails,
                    contributors_affiliations
                )
                self._contributors = zip(
                    contributors_names,
                    contributors_emails,
                    contributors_affiliations
                )

        return self._contributors

    def set_record_contributors(
        self,
        (contributors_names, contributors_emails, contributors_affiliations)
    ):
        self._contributors = zip(
            contributors_names,
            contributors_emails,
            contributors_affiliations
        )

    def get_record_report_number(self, force=False):

        if '_rn' not in self.__dict__.keys() or force:

            self._rn = ""

            (tag, ind1, ind2, subfield) = self._get_marc_field_parts(
                CFG_BIBSWORD_MARC_FIELDS['rn']
            )

            for record_rn in self._record.get(tag, []):
                if _decapitalize(record_rn[1:3]) == (ind1, ind2):
                    for (code, value) in record_rn[0]:
                        if code.lower() == subfield:
                            self._rn = value
                            break
                            # Only get the first occurrence
                            break

        return self._rn

    def set_record_report_number(self, rn):
        self._rn = rn

    def get_record_additional_report_numbers(self, force=False):

        if '_additional_rn' not in self.__dict__.keys() or force:

            self._additional_rn = []

            (tag, ind1, ind2, subfield) = self._get_marc_field_parts(
                CFG_BIBSWORD_MARC_FIELDS['additional_rn']
            )

            for record_additional_rn in self._record.get(tag, []):
                if _decapitalize(record_additional_rn[1:3]) == (ind1, ind2):
                    for (code, value) in record_additional_rn[0]:
                        if code.lower() == subfield:
                            self._additional_rn.append(value)
                            break

            self._additional_rn = tuple(self._additional_rn)

        return self._additional_rn

    def set_record_additional_report_numbers(self, additional_rn):
        self._additional_rn = tuple(additional_rn)

    def get_record_doi(self, force=False):

        if '_doi' not in self.__dict__.keys() or force:

            self._doi = ""

            (tag, ind1, ind2, subfield) = self._get_marc_field_parts(
                CFG_BIBSWORD_MARC_FIELDS['doi']
            )

            for record_doi in self._record.get(tag, []):
                if _decapitalize(record_doi[1:3]) == (ind1, ind2):
                    for (code, value) in record_doi[0]:
                        if code.lower() == subfield:
                            self._doi = value
                            break
                            # Only get the first occurrence
                            break

        return self._doi

    def set_record_doi(self, doi):
        self._doi = doi

    def get_record_comments(self, force=False):

        if '_comments' not in self.__dict__.keys() or force:

            self._comments = []

            (tag, ind1, ind2, subfield) = self._get_marc_field_parts(
                CFG_BIBSWORD_MARC_FIELDS['comments']
            )

            for record_comments in self._record.get(tag, []):
                if _decapitalize(record_comments[1:3]) == (ind1, ind2):
                    for (code, value) in record_comments[0]:
                        if code.lower() == subfield:
                            self._comments.append(value)
                            break

            self._comments = tuple(self._comments)

        return self._comments

    def set_record_comments(self, comments):
        self._comments = tuple(comments)

    def get_record_internal_notes(self, force=False):

        if '_internal_notes' not in self.__dict__.keys() or force:

            self._internal_notes = []

            (tag, ind1, ind2, subfield) = self._get_marc_field_parts(
                CFG_BIBSWORD_MARC_FIELDS['internal_notes']
            )

            for record_internal_notes in self._record.get(tag, []):
                if _decapitalize(record_internal_notes[1:3]) == (ind1, ind2):
                    for (code, value) in record_internal_notes[0]:
                        if code.lower() == subfield:
                            self._internal_notes.append(value)
                            break

            self._internal_notes = tuple(self._internal_notes)

        return self._internal_notes

    def set_record_internal_notes(self, internal_notes):
        self._internal_notes = tuple(internal_notes)

    def get_record_journal_info(self, force=False):

        if '_journal_info' not in self.__dict__.keys() or force:

            journal_code = ""
            journal_title = ""
            journal_page = ""
            journal_year = ""

            (
                tag_code,
                ind1_code,
                ind2_code,
                subfield_code
            ) = self._get_marc_field_parts(
                CFG_BIBSWORD_MARC_FIELDS['journal_code']
            )

            (
                tag_title,
                ind1_title,
                ind2_title,
                subfield_title
            ) = self._get_marc_field_parts(
                CFG_BIBSWORD_MARC_FIELDS['journal_title']
            )

            (
                tag_page,
                ind1_page,
                ind2_page,
                subfield_page
            ) = self._get_marc_field_parts(
                CFG_BIBSWORD_MARC_FIELDS['journal_page']
            )

            (
                tag_year,
                ind1_year,
                ind2_year,
                subfield_year
            ) = self._get_marc_field_parts(
                CFG_BIBSWORD_MARC_FIELDS['journal_year']
            )

            for record_journal_code in self._record.get(tag_code, []):
                if _decapitalize(record_journal_code[1:3]) == (
                    ind1_code, ind2_code
                ):
                    for (code, value) in record_journal_code[0]:
                        if code.lower() == subfield_code:
                            journal_code = value
                            break
                    if tag_code == tag_title and (ind1_code, ind2_code) == (
                        ind1_title, ind2_title
                    ):
                        for (code, value) in record_journal_code[0]:
                            if code.lower() == subfield_title:
                                journal_title = value
                                break
                    if tag_code == tag_page and (ind1_code, ind2_code) == (
                        ind1_page, ind2_page
                    ):
                        for (code, value) in record_journal_code[0]:
                            if code.lower() == subfield_page:
                                journal_page = value
                                break
                    if tag_code == tag_year and (ind1_code, ind2_code) == (
                        ind1_year, ind2_year
                    ):
                        for (code, value) in record_journal_code[0]:
                            if code.lower() == subfield_year:
                                journal_year = value
                                break
                    # Only get the first occurrence
                    break

            if tag_code != tag_title or (ind1_code, ind2_code) != (
                ind1_title, ind2_title
            ):
                for record_journal_title in self._record.get(tag_title, []):
                    if _decapitalize(record_journal_title[1:3]) == (
                        ind1_title, ind2_title
                    ):
                        for (code, value) in record_journal_title[0]:
                            if code.lower() == subfield_title:
                                journal_title = value
                                break
                                # Only get the first occurrence
                                break

            if tag_code != tag_page or (ind1_code, ind2_code) != (
                ind1_page, ind2_page
            ):
                for record_journal_page in self._record.get(tag_page, []):
                    if _decapitalize(record_journal_page[1:3]) == (
                        ind1_page, ind2_page
                    ):
                        for (code, value) in record_journal_page[0]:
                            if code.lower() == subfield_page:
                                journal_page = value
                                break
                                # Only get the first occurrence
                                break

            if tag_code != tag_year or (ind1_code, ind2_code) != (
                ind1_year, ind2_year
            ):
                for record_journal_year in self._record.get(tag_year, []):
                    if _decapitalize(record_journal_year[1:3]) == (
                        ind1_year, ind2_year
                    ):
                        for (code, value) in record_journal_year[0]:
                            if code.lower() == subfield_year:
                                journal_year = value
                                break
                                # Only get the first occurrence
                                break

            self._journal_info = (
                journal_code,
                journal_title,
                journal_page,
                journal_year
            )

        return self._journal_info

    def set_record_journal_info(
        self,
        (journal_code, journal_title, journal_page, journal_year)
    ):
        self._journal_info = (
            journal_code,
            journal_title,
            journal_page,
            journal_year
        )

    def get_record_modification_date(self, force=False):
        if '_modification_date' not in self.__dict__.keys() or force:
            self._modification_date = get_modification_date(
                self.get_recid(),
                CFG_BIBSWORD_UPDATED_DATE_MYSQL_FORMAT +
                CFG_BIBSWORD_LOCAL_TIMEZONE
            )
        return self._modification_date

    def set_record_modification_date(self, modification_date):
        self._modification_date = modification_date

    def get_accepted_file_types(self):
        if '_accepted_file_types' not in self.__dict__.keys():
            if '_collection_url' not in self.__dict__.keys():
                self._collection_url = self.get_collection_url()
            self._accepted_file_types = self._server.get_accepted_file_types(
                self._collection_url
            )
        return self._accepted_file_types

    def get_maximum_file_size(self):
        """
        In bytes.
        """
        if '_maximum_file_size' not in self.__dict__.keys():
            self._maximum_file_size = self._server.get_maximum_file_size()
        return self._maximum_file_size

    def get_record_files(self):

        if '_files' not in self.__dict__.keys():

            # Fetch all the record's files and cross-check the list
            # against the accepted file types of the chosen collection
            # and the maximum file size

            accepted_file_types = self.get_accepted_file_types()
            maximum_file_size = self.get_maximum_file_size()

            self._files = {}
            counter = 0

            brd = BibRecDocs(self._recid)
            bdfs = brd.list_latest_files()
            for bdf in bdfs:
                extension = bdf.get_superformat()
                checksum = bdf.get_checksum()
                path = bdf.get_full_path()
                url = bdf.get_url()
                name = bdf.get_full_name()
                size = bdf.get_size()
                mime = bdf.mime

                if (extension in accepted_file_types) and (
                    size <= maximum_file_size
                ):
                    counter += 1
                    self._files[counter] = {
                        'name': name,
                        'path': path,
                        'url': url,
                        'checksum': checksum,
                        'size': size,
                        'mime': mime,
                    }

        return self._files

    def get_files_indexes(self):
        if '_files_indexes' not in self.__dict__.keys():
            self._files_indexes = ()
        return self._files_indexes

    def set_files_indexes(self, files_indexes):
        self._files_indexes = tuple(map(int, files_indexes))

    def get_server_id(self):
        if '_server_id' not in self.__dict__.keys():
            self._server_id = None
        return self._server_id

    def set_server_id(self, server_id):
        self._server_id = server_id

    def get_server(self):
        if '_server' not in self.__dict__.keys():
            self._server = None
        return self._server

    def set_server(self, server):
        self._server = server

    def get_available_collections(self):
        if '_available_collections' not in self.__dict__.keys():
            if '_server' not in self.__dict__.keys():
                self._server = self.get_server()
            self._available_collections = self._server.get_collections()
        return self._available_collections

    def get_collection_url(self):
        if '_collection_url' not in self.__dict__.keys():
            self._collection_url = None
        return self._collection_url

    def set_collection_url(self, collection_url):
        self._collection_url = collection_url

    def get_available_categories(self):
        if '_available_categories' not in self.__dict__.keys():
            if '_collection_url' not in self.__dict__.keys():
                self._collection_url = self.get_collection_url()
            self._available_categories = self._server.get_categories(
                self._collection_url
            )
        return self._available_categories

    def set_mandatory_category_url(self, mandatory_category_url):
        self._mandatory_category_url = mandatory_category_url

    def get_mandatory_category_url(self):
        if '_mandatory_category_url' not in self.__dict__.keys():
            self._mandatory_category_url = None
        return self._mandatory_category_url

    def set_optional_categories_urls(self, optional_categories_urls):
        self._optional_categories_urls = tuple(optional_categories_urls)

    def get_optional_categories_urls(self):
        if '_optional_categories_urls' not in self.__dict__.keys():
            self._optional_categories_urls = ()
        return self._optional_categories_urls

    def submit(self):

        # Prepare the URL
        url = self.get_collection_url()

        # Prepare the metadata

        # Prepare the mandatory and optional categories
        available_categories = self.get_available_categories()
        mandatory_category_url = self.get_mandatory_category_url()
        optional_categories_urls = self.get_optional_categories_urls()
        mandatory_category = {
            "term": mandatory_category_url,
            "scheme": available_categories[
                "mandatory"
            ][
                mandatory_category_url
            ][
                "scheme"
            ],
            "label": available_categories[
                "mandatory"
            ][
                mandatory_category_url
            ][
                "label"
            ],
        }
        optional_categories = []
        for optional_category_url in optional_categories_urls:
            optional_categories.append(
                {
                    "term": optional_category_url,
                    "scheme": available_categories[
                        "optional"
                    ][
                        optional_category_url
                    ][
                        "scheme"
                    ],
                    "label": available_categories[
                        "optional"
                    ][
                        optional_category_url
                    ][
                        "label"
                    ],
                }
            )
        optional_categories = tuple(optional_categories)

        # Get all the metadata together
        metadata = {
            "abstract": self.get_record_abstract(),
            "additional_rn": self.get_record_additional_report_numbers(),
            "author": self.get_record_author(),
            "comments": self.get_record_comments(),
            "contributors": self.get_record_contributors(),
            "doi": self.get_record_doi(),
            "internal_notes": self.get_record_internal_notes(),
            "journal_info": self.get_record_journal_info(),
            "rn": self.get_record_report_number(),
            "title": self.get_record_title(),
            "modification_date": self.get_record_modification_date(),
            "recid": self.get_recid(),
            "mandatory_category": mandatory_category,
            "optional_categories": optional_categories,
        }

        # Prepare the media
        media = {}
        files = self.get_record_files()
        files_indexes = self.get_files_indexes()
        for file_index in files_indexes:
            media[file_index] = files[file_index]

        # Perform the submission and save the result
        self._result = self._server.submit(
            metadata,
            media,
            url
        )

        # Return the result
        return self._result

    def get_result(self):
        if '_result' not in self.__dict__.keys():
            self._result = None
        return self._result


def perform_submit(
        uid,
        record_id,
        server_id,
        ln
):
    """
    """

    if record_id and record_exists(record_id):

        # At this point we have a valid recid, go ahead and create the
        # submission object.
        submission = BibSwordSubmission(
            record_id,
            uid
        )

        # Gather useful information about the submission.
        title = submission.get_record_title()
        author = submission.get_record_author()[0]
        report_number = submission.get_record_report_number()

        # Get the submission ID.
        sid = submission.get_sid()

        # Store the submission.
        stored_submission_successfully_p = _store_temp_submission(
            sid,
            submission
        )

        # Inform the user and administrators in case of problems and exit.
        if not stored_submission_successfully_p:
            msg = ("BibSword: Unable to store the submission in the DB " +
                   "(sid={0}, uid={1}, record_id={2}, server_id={3}).").format(
                sid,
                uid,
                record_id,
                server_id
            )
            raise_exception(
                msg=msg,
                alert_admin=True
            )
            _ = gettext_set_language(ln)
            out = _("An error has occured. " +
                    "The administrators have been informed.")
            return out

        # Get the list of available servers.
        servers = sword_client_db.get_servers()
        # Only keep the server ID and name.
        if servers:
            servers = [server[:2] for server in servers]

        # If the server_id has already been chosen,
        # then move to the next step automatically.
        step = 0
        if server_id:
            step = 1

        # Create the basic starting interface for this submission.
        out = sword_client_template.tmpl_submit(
            sid,
            record_id,
            title,
            author,
            report_number,
            step,
            servers,
            server_id,
            ln
        )

        return out

    else:
        # This means that no record_id was given, inform the user that a
        # record_id is necessary for the submission to start.
        _ = gettext_set_language(ln)
        out = _("Unable to submit invalid record. " +
                "Please submit a valid record and try again.")
        return out


def perform_submit_step_1(
    sid,
    server_id,
    ln
):
    """
    """

    _ = gettext_set_language(ln)

    submission = _retrieve_temp_submission(sid)
    if submission is None:
        msg = ("BibSword: Unable to retrieve the submission from the DB " +
               "(sid={0}, server_id={1}).").format(
            sid,
            server_id
        )
        raise_exception(
            msg=msg,
            alert_admin=True
        )
        _ = gettext_set_language(ln)
        out = _("An error has occured. " +
                "The administrators have been informed.")
        return out

    record_id = submission.get_recid()
    is_submission_archived = sword_client_db.is_submission_archived(
        record_id,
        server_id
    )
    if is_submission_archived:
        out = _("This record has already been submitted to this server." +
                "<br />Please start again and select a different server.")
        return out

    server_settings = sword_client_db.get_servers(
        server_id=server_id,
        with_dict=True
    )
    if not server_settings:
        msg = ("BibSword: Unable to find the server settings in the DB " +
               "(sid={0}, server_id={1}).").format(
            sid,
            server_id
        )
        raise_exception(
            msg=msg,
            alert_admin=True
        )
        _ = gettext_set_language(ln)
        out = _("An error has occured. " +
                "The administrators have been informed.")
        return out

    server_settings = server_settings[0]
    server_object = _initialize_server(server_settings)
    if not server_object:
        msg = ("BibSword: Unable to initialize the server " +
               "(sid={0}, server_id={1}).").format(
            sid,
            server_id
        )
        raise_exception(
            msg=msg,
            alert_admin=True
        )
        _ = gettext_set_language(ln)
        out = _("An error has occured. " +
                "The administrators have been informed.")
        return out

    # Update the server's service document if needed.
    if server_object.needs_to_be_updated():
        server_object.update()

    submission.set_server_id(server_id)
    submission.set_server(server_object)

    # Get the available collections
    available_collections = submission.get_available_collections()

    # Prepare the collections for the HTML select element
    collections = sorted(
        [
            (
                available_collection,
                available_collections[available_collection]["title"]
            ) for available_collection in available_collections
        ],
        key=lambda available_collection: available_collection[1]
    )

    # Update the stored submission.
    updated_submission_successfully_p = _update_temp_submission(
        sid,
        submission
    )
    if not updated_submission_successfully_p:
        msg = ("BibSword: Unable to update the submission in the DB " +
               "(sid={0}, server_id={1}).").format(
            sid,
            server_id
        )
        raise_exception(
            msg=msg,
            alert_admin=True
        )
        _ = gettext_set_language(ln)
        out = _("An error has occured. " +
                "The administrators have been informed.")
        return out

    out = sword_client_template.submit_step_2_details(
        collections,
        ln
    )

    return out


def perform_submit_step_2(
    sid,
    collection_url,
    ln
):
    """
    """

    _ = gettext_set_language(ln)

    submission = _retrieve_temp_submission(sid)
    if submission is None:
        msg = ("BibSword: Unable to retrieve the submission from the DB " +
               "(sid={0}).").format(
            sid
        )
        raise_exception(
            msg=msg,
            alert_admin=True
        )
        _ = gettext_set_language(ln)
        out = _("An error has occured. " +
                "The administrators have been informed.")
        return out

    submission.set_collection_url(collection_url)

    # Get the available categories
    available_categories = submission.get_available_categories()

    # Prepare the categories for the HTML select element
    mandatory_categories = sorted(
        [
            (
                available_mandatory_category,
                available_categories[
                    "mandatory"
                ][
                    available_mandatory_category
                ][
                    "label"
                ]
            ) for available_mandatory_category in available_categories[
                "mandatory"
            ]
        ],
        key=lambda available_mandatory_category: available_mandatory_category[
            1
        ]
    )
    optional_categories = sorted(
        [
            (
                available_optional_category,
                available_categories[
                    "optional"
                ][
                    available_optional_category
                ][
                    "label"
                ]
            ) for available_optional_category in available_categories[
                "optional"
            ]
        ],
        key=lambda available_optional_category: available_optional_category[
            1
        ]
    )

    # Update the stored submission.
    updated_submission_successfully_p = _update_temp_submission(
        sid,
        submission
    )
    if not updated_submission_successfully_p:
        msg = ("BibSword: Unable to update the submission in the DB " +
               "(sid={0}).").format(
            sid
        )
        raise_exception(
            msg=msg,
            alert_admin=True
        )
        _ = gettext_set_language(ln)
        out = _("An error has occured. " +
                "The administrators have been informed.")
        return out

    out = sword_client_template.submit_step_3_details(
        mandatory_categories,
        optional_categories,
        ln
    )

    return out


def perform_submit_step_3(
    sid,
    mandatory_category_url,
    optional_categories_urls,
    ln
):
    """
    """

    _ = gettext_set_language(ln)

    submission = _retrieve_temp_submission(sid)
    if submission is None:
        msg = ("BibSword: Unable to retrieve the submission from the DB " +
               "(sid={0}).").format(
            sid
        )
        raise_exception(
            msg=msg,
            alert_admin=True
        )
        _ = gettext_set_language(ln)
        out = _("An error has occured. " +
                "The administrators have been informed.")
        return out

    submission.set_mandatory_category_url(mandatory_category_url)
    if optional_categories_urls:
        submission.set_optional_categories_urls(optional_categories_urls)

    metadata = {
        'title': submission.get_record_title(),
        'abstract': submission.get_record_abstract(),
        'author': submission.get_record_author(),
        'contributors': submission.get_record_contributors(),
        'rn': submission.get_record_report_number(),
        'additional_rn': submission.get_record_additional_report_numbers(),
        'doi': submission.get_record_doi(),
        'comments': submission.get_record_comments(),
        'internal_notes': submission.get_record_internal_notes(),
        'journal_info': submission.get_record_journal_info(),
    }

    files = submission.get_record_files()

    # Update the stored submission.
    updated_submission_successfully_p = _update_temp_submission(
        sid,
        submission
    )
    if not updated_submission_successfully_p:
        msg = ("BibSword: Unable to update the submission in the DB " +
               "(sid={0}).").format(
            sid
        )
        raise_exception(
            msg=msg,
            alert_admin=True
        )
        _ = gettext_set_language(ln)
        out = _("An error has occured. " +
                "The administrators have been informed.")
        return out

    out = sword_client_template.submit_step_4_details(
        metadata,
        files,
        CFG_BIBSWORD_MAXIMUM_NUMBER_OF_CONTRIBUTORS,
        ln
    )

    return out


def perform_submit_step_4(
    sid,
    (
        rn,
        additional_rn,
        title,
        author_fullname,
        author_email,
        author_affiliation,
        abstract,
        contributor_fullname,
        contributor_email,
        contributor_affiliation,
        files_indexes
    ),
    ln
):
    """
    """

    _ = gettext_set_language(ln)

    submission = _retrieve_temp_submission(sid)
    if submission is None:
        msg = ("BibSword: Unable to retrieve the submission from the DB " +
               "(sid={0}).").format(
            sid
        )
        raise_exception(
            msg=msg,
            alert_admin=True
        )
        _ = gettext_set_language(ln)
        out = _("An error has occured. " +
                "The administrators have been informed.")
        return out

    # Set the updated metadata
    submission.set_record_title(title)
    submission.set_record_abstract(abstract)
    submission.set_record_author(
        (author_fullname, author_email, author_affiliation)
    )
    submission.set_record_contributors(
        (contributor_fullname, contributor_email, contributor_affiliation)
    )
    submission.set_record_report_number(rn)
    submission.set_record_additional_report_numbers(additional_rn)
    # submission.set_record_doi(doi)
    # submission.set_record_comments(comments)
    # submission.set_record_internal_notes(internal_notes)
    # submission.set_record_journal_info(
    #     (journal_code, journal_title, journal_page, journal_year)
    # )

    # Set the chosen files indexes
    submission.set_files_indexes(files_indexes)

    # Perform the submission
    result = submission.submit()

    if result is None or not result or result.get('error', False):
        # Update the stored submission
        updated_submission_successfully_p = _update_temp_submission(
            sid,
            submission
        )

        if not updated_submission_successfully_p:
            msg = ("BibSword: Unable to update the submission in the DB " +
                   "(sid={0}).").format(
                sid
            )
            raise_exception(
                msg=msg,
                alert_admin=True
            )
            _ = gettext_set_language(ln)
            out = _("An error has occured. " +
                    "The administrators have been informed.")
            return out

        # TODO: Should we give the user detailed feedback on the error
        #       in the result (if it exsists?), instead of just notifying
        #        the admins?
        msg = ("BibSword: The submission failed " +
               "(sid={0}, result={1}).").format(
            sid,
            str(result)
        )
        raise_exception(
            msg=msg,
            alert_admin=True
        )

        _ = gettext_set_language(ln)
        if result.get("error", False):
            out = _("The submission could not be completed successfully " +
                    "and the following error has been reported:" +
                    "<br /><em>{0}</em><br />" +
                    "The administrators have been informed.").format(
                        result.get("msg", _("Uknown error."))
                        )
        else:
            out = _("An error has occured. " +
                    "The administrators have been informed.")
        return out

    else:
        # Archive the submission
        archived_submission_successfully_p = _archive_submission(submission)
        if not archived_submission_successfully_p:
            msg = ("BibSword: Unable to archive the submission in the DB " +
                   "(sid={0}).").format(
                sid
            )
            raise_exception(
                msg=msg,
                alert_admin=True
            )
            _ = gettext_set_language(ln)
            out = _("An error has occured. " +
                    "The administrators have been informed.")
            return out

        # Delete the previously temporary submission
        deleted_submission_successfully_p = _delete_temp_submission(sid)
        if not deleted_submission_successfully_p:
            msg = ("BibSword: Unable to delete the submission in the DB " +
                   "(sid={0}).").format(
                sid
            )
            raise_exception(
                msg=msg,
                alert_admin=True
            )
            _ = gettext_set_language(ln)
            out = _("An error has occured. " +
                    "The administrators have been informed.")
            return out

    out = sword_client_template.submit_step_final_details(ln)

    return out


def _archive_submission(sobject):
    """
    Archives the current submission.
    """

    user_id = sobject.get_uid()
    record_id = sobject.get_recid()
    server_id = sobject.get_server_id()
    result = sobject.get_result()
    alternate_url = result['msg']['alternate']
    edit_url = result['msg']['edit']
    return sword_client_db.archive_submission(
        user_id,
        record_id,
        server_id,
        alternate_url,
        edit_url
    )


def _store_temp_submission(sid, sobject):
    """
    Uses cPickle to dump the current submission and stores it.
    """

    sobject_blob = cPickle.dumps(sobject)
    return sword_client_db.store_temp_submission(sid, sobject_blob)


def _retrieve_temp_submission(sid):
    """
    Retrieves the current submission and uses cPickle to load it.
    """

    # call DB function to retrieve the blob
    sobject_blob = sword_client_db.retrieve_temp_submission(sid)
    sobject = cPickle.loads(sobject_blob)
    return sobject


def _update_temp_submission(sid, sobject):
    """
    Uses cPickle to dump the current submission and updates it.
    """

    sobject_blob = cPickle.dumps(sobject)
    return sword_client_db.update_temp_submission(sid, sobject_blob)


def _delete_temp_submission(sid):
    """
    Deletes the given submission.
    """

    return sword_client_db.delete_temp_submission(sid)


def _decapitalize(field_parts):
    return tuple([part.lower() for part in field_parts])


def perform_request_submissions(
    ln
):
    """
    Returns the HTML for the Sword client submissions.
    """

    submissions = sword_client_db.get_submissions()

    html = sword_client_template.tmpl_submissions(
        submissions,
        ln
    )

    return html


def perform_request_submission_options(
    option,
    action,
    server_id,
    status_url,
    ln
):
    """
    Perform an action on a given submission based on the selected option
    and return the results.
    """

    _ = gettext_set_language(ln)

    (error, result) = (None, None)

    if not option:
        error = _("Missing option")

    elif not action:
        error = _("Missing action")

    else:

        if option == "update":

            if not server_id:
                error = _("Missing server ID")

            if not status_url:
                error = _("Missing status URL")

            else:
                if action == "submit":
                    server_settings = sword_client_db.get_servers(
                        server_id=server_id,
                        with_dict=True
                    )
                    if not server_settings:
                        error = _("The server could not be found")
                    else:
                        server_settings = server_settings[0]
                        server_object = _initialize_server(server_settings)
                        if not server_object:
                            error = _("The server could not be initialized")
                        else:
                            result = server_object.status(status_url)
                            if result["error"]:
                                error = _(result["msg"])
                            else:
                                result = {
                                    "status": (
                                        result["msg"]["error"] is None
                                    ) and (
                                        "{0}".format(result["msg"]["status"])
                                    ) or (
                                        "{0} ({1})".format(
                                            result["msg"]["status"],
                                            result["msg"]["error"]
                                        )
                                    ),
                                    "last_updated": _("Just now"),
                                }
                                result = json.dumps(result)
                else:
                    error = _("Wrong action")

        else:
            error = _("Wrong option")

    return (error, result)


def perform_request_servers(
    ln
):
    """
    Returns the HTML for the Sword client servers.
    """

    servers = sword_client_db.get_servers()

    html = sword_client_template.tmpl_servers(
        servers,
        ln
    )

    return html


def perform_request_server_options(
    option,
    action,
    server_id,
    server,
    ln
):
    """
    Perform an action on a given server based on the selected option
    and return the results.
    """

    _ = gettext_set_language(ln)

    (error, result) = (None, None)

    if not option:
        error = _("Missing option")

    elif not action:
        error = _("Missing action")

    else:

        if option == "add":
            if action == "prepare":
                server = None
                available_engines = _CLIENT_SERVERS.keys()
                if "__init__" in available_engines:
                    available_engines.remove("__init__")
                result = sword_client_template.tmpl_add_or_modify_server(
                    server,
                    available_engines,
                    ln
                )
            elif action == "submit":
                if "" in server:
                    error = _("Insufficient server information")
                else:
                    if not _validate_server(server):
                        error = _("Wrong server information")
                    else:
                        server_id = sword_client_db.add_server(*server)
                        if server_id:
                            (
                                name,
                                engine,
                                username,
                                password,
                                email,
                                update_frequency
                            ) = server
                            result = \
                                sword_client_template._tmpl_server_table_row(
                                    (
                                        server_id,
                                        name,
                                        engine,
                                        username,
                                        password,
                                        email,
                                        None,
                                        update_frequency,
                                        None,
                                    ),
                                    ln
                                )
                        else:
                            error = _("The server could not be added")
            else:
                error = _("Wrong action")

        elif option == "update":

            if not server_id:
                error = _("Missing server ID")

            else:
                if action == "submit":
                    server_settings = sword_client_db.get_servers(
                        server_id=server_id,
                        with_dict=True
                    )
                    if not server_settings:
                        error = _("The server could not be found")
                    else:
                        server_settings = server_settings[0]
                        server_object = _initialize_server(server_settings)
                        if not server_object:
                            error = _("The server could not be initialized")
                        else:
                            result = server_object.update()
                            if not result:
                                error = _("The server could not be updated")
                            else:
                                result = _("Just now")
                else:
                    error = _("Wrong action")

        elif option == "modify":
            if not server_id:
                error = _("Missing server ID")

            else:
                if action == "prepare":
                    server = sword_client_db.get_servers(
                        server_id=server_id
                    )
                    if not server:
                        error = _("The server could not be found")
                    else:
                        server = server[0]
                        available_engines = _CLIENT_SERVERS.keys()
                        if "__init__" in available_engines:
                            available_engines.remove("__init__")
                        result = \
                            sword_client_template.tmpl_add_or_modify_server(
                                server,
                                available_engines,
                                ln
                            )
                elif action == "submit":
                    if "" in server:
                        error = _("Insufficient server information")
                    else:
                        if not _validate_server(server):
                            error = _("Wrong server information")
                        else:
                            result = sword_client_db.modify_server(
                                server_id,
                                *server
                            )
                            if result:
                                (
                                    name,
                                    engine,
                                    username,
                                    dummy,
                                    email,
                                    update_frequency
                                ) = server
                                result = {
                                    "name": name,
                                    "engine": engine,
                                    "username": username,
                                    "email": email,
                                    "update_frequency": TemplateSwordClient
                                    ._humanize_frequency(update_frequency, ln),
                                }
                                result = json.dumps(result)
                            else:
                                error = _("The server could not be modified")
                else:
                    error = _("Wrong action")

        elif option == "delete":
            if not server_id:
                error = _("Missing server ID")

            else:
                if action == "submit":
                    result = sword_client_db.delete_servers(
                        server_id=server_id
                    )
                    if not result:
                        error = _("The server could not be deleted")
                else:
                    error = _("Wrong action")

        else:
            error = _("Wrong option")

    return (error, result)


def _initialize_server(server_settings):
    """
    Initializes and returns the server based on the given settings.
    """

    server_engine = server_settings.pop('engine')
    if server_engine is not None:
        server_object = _CLIENT_SERVERS.get(server_engine)(server_settings)
        return server_object
    return None


def _validate_server(server_settings):
    """
    Returs True if the server settings are valid or False if otherwise.
    """

    (server_name,
     server_engine,
     server_username,
     server_password,
     server_email,
     server_update_frequency) = server_settings

    available_engines = _CLIENT_SERVERS.keys()
    if "__init__" in available_engines:
        available_engines.remove("__init__")
    if server_engine not in available_engines:
        return False

    if not re.match(
        r"^([0-9]+[wdhms]{1}){1,5}$",
        server_update_frequency
    ):
        return False

    return True
