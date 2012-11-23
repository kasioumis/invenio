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
BibSword Web Interface.
"""

from invenio.access_control_engine import(
    acc_authorize_action
)
import invenio.bibsword_client as sword_client
from invenio.config import(
    CFG_SITE_LANG,
    CFG_SITE_URL
)
from invenio.messages import(
    gettext_set_language
)
from invenio.webinterface_handler import(
    wash_urlargd,
    WebInterfaceDirectory
)
from invenio.webpage import(
    page
)
from invenio.webuser import(
    getUid,
    page_not_authorized
)


__lastupdated__ = """$Date$"""


class WebInterfaceSwordClient(WebInterfaceDirectory):
    """Web interface for the BibSword client."""

    _exports = [
        "",
        "servers",
        "server_options",
        "submissions",
        "submission_options",
        "submit",
        "submit_step_1",
        "submit_step_2",
        "submit_step_3",
        "submit_step_4",
    ]

    def submissions(self, req, form):
        """Web interface for the existing submissions."""
        # Check if the user has rights to manage the Sword client
        auth_code, auth_message = acc_authorize_action(
            req,
            "run_sword_client"
        )
        if auth_code != 0:
            return page_not_authorized(
                req=req,
                referer="/sword_client/",
                text=auth_message,
                navtrail=""
            )

        argd = wash_urlargd(form, {
            "ln": (str, CFG_SITE_LANG),
        })

        # Get the user ID
        uid = getUid(req)

        # Set language for i18n text auto generation
        ln = argd["ln"]
        _ = gettext_set_language(ln)

        body = sword_client.perform_request_submissions(
            ln
        )

        navtrail = """
&gt; <a class="navtrail" href="%(CFG_SITE_URL)s/sword_client">%(label)s</a>
""" % {
            'CFG_SITE_URL': CFG_SITE_URL,
            'label': _("Sword Client"),
        }

        return page(
            title=_("Submissions"),
            body=body,
            navtrail=navtrail,
            lastupdated=__lastupdated__,
            req=req,
            language=ln
        )

    def submission_options(self, req, form):
        """Web interface for the options on the submissions."""
        # Check if the user has rights to manage the Sword client
        auth_code, auth_message = acc_authorize_action(
            req,
            "run_sword_client"
        )
        if auth_code != 0:
            return page_not_authorized(
                req=req,
                referer="/sword_client",
                text=auth_message,
                navtrail=""
            )

        argd = wash_urlargd(form, {
            "option": (str, ""),
            "action": (str, "submit"),
            "server_id": (int, 0),
            "status_url": (str, ""),
            "ln": (str, CFG_SITE_LANG),
        })

        if argd["option"] in ("update",):
            option = argd["option"]
        else:
            option = ""

        if argd["action"] in ("submit",):
            action = argd["action"]
        else:
            action = ""

        server_id = argd["server_id"]
        status_url = argd["status_url"]
        ln = argd["ln"]

        (error, result) = sword_client.perform_request_submission_options(
            option,
            action,
            server_id,
            status_url,
            ln
        )

        if error:
            req.set_content_type("text/plain; charset=utf-8")
            req.set_status("400")
            req.send_http_header()
            req.write("Error: {0}".format(error))
            return

        return result

    def servers(self, req, form):
        """Web interface for the available servers."""
        # Check if the user has rights to manage the Sword client
        auth_code, auth_message = acc_authorize_action(
            req,
            "manage_sword_client"
        )
        if auth_code != 0:
            return page_not_authorized(
                req=req,
                referer="/sword_client/",
                text=auth_message,
                navtrail=""
            )

        argd = wash_urlargd(form, {
            "ln": (str, CFG_SITE_LANG),
        })

        # Get the user ID
        uid = getUid(req)

        # Set language for i18n text auto generation
        ln = argd["ln"]
        _ = gettext_set_language(ln)

        body = sword_client.perform_request_servers(
            ln
        )

        navtrail = """
&gt; <a class="navtrail" href="%(CFG_SITE_URL)s/sword_client">%(label)s</a>
""" % {
            'CFG_SITE_URL': CFG_SITE_URL,
            'label': _("Sword Client"),
        }

        return page(
            title=_("Servers"),
            body=body,
            navtrail=navtrail,
            lastupdated=__lastupdated__,
            req=req,
            language=ln
        )

    def server_options(self, req, form):
        """Web interface for the options on the available servers."""
        # Check if the user has rights to manage the Sword client
        auth_code, auth_message = acc_authorize_action(
            req,
            "manage_sword_client"
        )
        if auth_code != 0:
            return page_not_authorized(
                req=req,
                referer="/sword_client",
                text=auth_message,
                navtrail=""
            )

        argd = wash_urlargd(form, {
            "option": (str, ""),
            "action": (str, "submit"),
            "server_id": (int, 0),
            "sword_client_server_name": (str, ""),
            "sword_client_server_engine": (str, ""),
            "sword_client_server_username": (str, ""),
            "sword_client_server_password": (str, ""),
            "sword_client_server_email": (str, ""),
            "sword_client_server_update_frequency": (str, ""),
            "ln": (str, CFG_SITE_LANG),
        })

        if argd["option"] in ("add", "update", "modify", "delete"):
            option = argd["option"]
        else:
            option = ""

        if argd["action"] in ("prepare", "submit"):
            action = argd["action"]
        else:
            action = ""

        server_id = argd["server_id"]

        server = (
            argd["sword_client_server_name"],
            argd["sword_client_server_engine"],
            argd["sword_client_server_username"],
            argd["sword_client_server_password"],
            argd["sword_client_server_email"],
            argd["sword_client_server_update_frequency"],
        )

        ln = argd["ln"]

        (error, result) = sword_client.perform_request_server_options(
            option,
            action,
            server_id,
            server,
            ln
        )

        if error:
            req.set_content_type("text/plain; charset=utf-8")
            req.set_status("400")
            req.send_http_header()
            req.write("Error: {0}".format(error))
            return

        return result

    def submit(self, req, form):
        """Submit a record using SWORD."""
        # Check if the user has rights to manage the Sword client
        auth_code, auth_message = acc_authorize_action(
            req,
            "run_sword_client"
        )
        if auth_code != 0:
            return page_not_authorized(
                req=req,
                referer="/sword_client",
                text=auth_message,
                navtrail=""
            )

        argd = wash_urlargd(form, {
            "record_id": (int, 0),
            "server_id": (int, 0),
            "ln": (str, CFG_SITE_LANG),
        })

        # Get the user ID
        uid = getUid(req)

        # Set language for i18n text auto generation
        ln = argd["ln"]
        _ = gettext_set_language(ln)

        record_id = argd["record_id"]
        server_id = argd["server_id"]

        body = sword_client.perform_submit(
            uid,
            record_id,
            server_id,
            ln
        )

        navtrail = """
&gt; <a class="navtrail" href="%(CFG_SITE_URL)s/sword_client">%(label)s</a>
""" % {
            'CFG_SITE_URL': CFG_SITE_URL,
            'label': _("Sword Client"),
        }

        return page(
            title=_("Submit"),
            body=body,
            navtrail=navtrail,
            lastupdated=__lastupdated__,
            req=req,
            language=ln
        )

    def submit_step_1(self, req, form):
        """Process step 1 in the submission workflow."""
        # Check if the user has adequate rights to run the bibsword client
        # TODO: in a more advanced model, also check if the give user has
        #       rights to the current submission based on the user id and the
        #       submission id. It would get even more complicated if we
        #       introduced people that can approve specific submissions etc.
        auth_code, auth_message = acc_authorize_action(
            req,
            "run_sword_client"
        )
        if auth_code != 0:
            return page_not_authorized(
                req=req,
                referer="/sword_client",
                text=auth_message,
                navtrail=""
            )

        argd = wash_urlargd(form, {
            'sid': (str, ''),
            'server_id': (int, 0),
            'ln': (str, CFG_SITE_LANG),
        })

        sid = argd['sid']
        server_id = argd['server_id']
        ln = argd['ln']

        return sword_client.perform_submit_step_1(
            sid,
            server_id,
            ln
        )

    def submit_step_2(self, req, form):
        """Process step 2 in the submission workflow."""
        # Check if the user has adequate rights to run the bibsword client
        # TODO: in a more advanced model, also check if the give user has
        #       rights to the current submission based on the user id and the
        #       submission id. It would get even more complicated if we
        #       introduced people that can approve specific submissions etc.
        auth_code, auth_message = acc_authorize_action(
            req,
            "run_sword_client"
        )
        if auth_code != 0:
            return page_not_authorized(
                req=req,
                referer="/sword_client",
                text=auth_message,
                navtrail=""
            )

        argd = wash_urlargd(form, {
            'sid': (str, ""),
            'collection_url': (str, ""),
            'ln': (str, CFG_SITE_LANG),
        })

        sid = argd['sid']
        collection_url = argd['collection_url']
        ln = argd['ln']

        return sword_client.perform_submit_step_2(
            sid,
            collection_url,
            ln
        )

    def submit_step_3(self, req, form):
        """Process step 3 in the submission workflow."""
        # Check if the user has adequate rights to run the bibsword client
        # TODO: in a more advanced model, also check if the give user has
        #       rights to the current submission based on the user id and the
        #       submission id. It would get even more complicated if we
        #       introduced people that can approve specific submissions etc.
        auth_code, auth_message = acc_authorize_action(
            req,
            "run_sword_client"
        )
        if auth_code != 0:
            return page_not_authorized(
                req=req,
                referer="/sword_client",
                text=auth_message,
                navtrail=""
            )

        argd = wash_urlargd(form, {
            'sid': (str, ""),
            'mandatory_category_url': (str, ""),
            'optional_categories_urls': (list, []),
            'ln': (str, CFG_SITE_LANG),
        })

        sid = argd['sid']
        ln = argd['ln']
        mandatory_category_url = argd['mandatory_category_url']
        optional_categories_urls = argd['optional_categories_urls']

        return sword_client.perform_submit_step_3(
            sid,
            mandatory_category_url,
            optional_categories_urls,
            ln
        )

    def submit_step_4(self, req, form):
        """Process step 4 in the submission workflow."""
        # Check if the user has adequate rights to run the bibsword client
        # TODO: in a more advanced model, also check if the give user has
        #       rights to the current submission based on the user id and the
        #       submission id. It would get even more complicated if we
        #       introduced people that can approve specific submissions etc.
        auth_code, auth_message = acc_authorize_action(
            req,
            "run_sword_client"
        )
        if auth_code != 0:
            return page_not_authorized(
                req=req,
                referer="/sword_client",
                text=auth_message,
                navtrail=""
            )

        argd = wash_urlargd(form, {
            "sid": (str, ""),
            "rn": (str, ""),
            "additional_rn": (list, []),
            "title": (str, ""),
            "author_fullname": (str, ""),
            "author_email": (str, ""),
            "author_affiliation": (str, ""),
            "abstract": (str, ""),
            "contributor_fullname": (list, []),
            "contributor_email": (list, []),
            "contributor_affiliation": (list, []),
            "files": (list, []),
            "ln": (str, CFG_SITE_LANG),
        })

        sid = argd["sid"]
        rn = argd["rn"]
        additional_rn = argd["additional_rn"]
        title = argd["title"]
        author_fullname = argd["author_fullname"]
        author_email = argd["author_email"]
        author_affiliation = argd["author_affiliation"]
        abstract = argd["abstract"]
        contributor_fullname = argd["contributor_fullname"]
        contributor_email = argd["contributor_email"]
        contributor_affiliation = argd["contributor_affiliation"]
        files_indexes = argd["files"]
        ln = argd["ln"]

        return sword_client.perform_submit_step_4(
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
        )

    index = submissions
