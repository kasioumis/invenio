# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2010, 2011, 2012, 2013. 2014, 2015, 2016 CERN.
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
BibSword general configuration variables.
"""

from invenio.bibformat_dblayer import get_tag_from_name
from invenio.urlutils import make_user_agent_string

# Define the maximum number of contributors to be displayed and submitted
CFG_BIBSWORD_MAXIMUM_NUMBER_OF_CONTRIBUTORS = 30

# Define a custom timeout for urllib2 requests
CFG_BIBSWORD_FORCE_DEFAULT_TIMEOUT = True
CFG_BIBSWORD_DEFAULT_TIMEOUT = 20.0

# The updated date format according to:
# * http://tools.ietf.org/html/rfc4287#section-3.3
# * https://dev.mysql.com/doc/refman/5.5/en/date-and-time-functions.html#function_date-format
# NOTE: Specify the local timezone in the "+xx:yy" format.
#       If unknown, must be "Z".
CFG_BIBSWORD_UPDATED_DATE_MYSQL_FORMAT = "%Y-%m-%dT%H:%i:%S"
CFG_BIBSWORD_LOCAL_TIMEZONE = "+01:00"

# The default atom entry mime-type for POST requests
CFG_BIBSWORD_ATOM_ENTRY_MIME_TYPE = "application/atom+xml;type=entry"

# Must be the same as in the client_servers/Makefile.am
CFG_BIBSWORD_CLIENT_SERVERS_PATH = "bibsword_client_servers"

CFG_BIBSWORD_USER_AGENT = make_user_agent_string("BibSword")

CFG_BIBSWORD_MARC_FIELDS = {
    'rn': get_tag_from_name('primary report number') or '037__a',
    'title': get_tag_from_name('title') or '245__a',
    'author_name': get_tag_from_name('first author name') or '100__a',
    'author_affiliation':
        get_tag_from_name('first author affiliation') or '100__u',
    'author_email': get_tag_from_name('first author email') or '859__f',
    'contributor_name':
        get_tag_from_name('additional author name') or '700__a',
    'contributor_affiliation':
        get_tag_from_name('additional author affiliation') or '700__u',
    # 'abstract': get_tag_from_name('main abstract') or '520__a',
    'abstract': '520__a',
    'additional_rn': get_tag_from_name('additional report number') or '088__a',
    # 'doi': get_tag_from_name('doi') or '909C4a',
    'doi': '909C4a',
    # 'journal_code': get_tag_from_name('journal code') or '909C4c',
    'journal_code': '909C4v',
    # 'journal_title': get_tag_from_name('journal title') or '909C4p',
    'journal_title': '909C4p',
    # 'journal_page': get_tag_from_name('journal page') or '909C4v',
    'journal_page': '909C4c',
    # 'journal_year': get_tag_from_name('journal year') or '909C4y',
    'journal_year': '909C4y',
    'comments': get_tag_from_name('comment') or '500__a',
    'internal_notes': get_tag_from_name('internal notes') or '595__a',
}

CFG_BIBSWORD_FILE_TYPES_MAPPING = {
    'application/atom+xml;type=entry': ['.xml'],
    'application/zip': ['.zip'],
    'application/xml': ['.wsdl', '.xpdl', '.rdf', '.xsl', '.xml', '.xsd'],
    'application/pdf': ['.pdf'],
    'application/postscript':
        ['.ai', '.ps', '.eps', '.epsi', '.epsf', '.eps2', '.eps3'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        ['.docx'],
    'text/xml': ['.xml'],
    'image/jpeg': ['.jpe', '.jpg', '.jpeg'],
    'image/jpg': ['.jpg'],
    'image/png': ['.png'],
    'image/gif': ['.gif'],
}
