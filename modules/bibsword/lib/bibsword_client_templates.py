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
BibSWORD Client Templates.
"""

from cgi import escape
from datetime import datetime
import re
from invenio.config import(
    CFG_SITE_RECORD,
    CFG_SITE_URL
)
from invenio.messages import gettext_set_language


class TemplateSwordClient(object):
    """
    Templates for the Sword client.
    """

    @staticmethod
    def _tmpl_submission_table_row(
        submission,
        ln
    ):
        """
        Returns the HTML code for a server table row.
        """
        (user,
         record_id,
         server_id,
         server_name,
         submitted,
         status,
         last_updated,
         status_url
         ) = submission

        table_row = """
                    <tr id="submission_id_{0}_{1}">
        """.format(record_id, server_id)

        table_row += """
                        <td class="sword_client_submission_user">
                            {0}
                        </td>
        """.format(user)

        table_row += """
                        <td class="sword_client_submission_record">
                            <a href="{0}/{1}/{2}">#{2}</a>
                        </td>
        """.format(CFG_SITE_URL, CFG_SITE_RECORD, record_id)

        table_row += """
                        <td class="sword_client_submission_server">
                            {0}
                        </td>
        """.format(server_name)

        table_row += """
                        <td class="sword_client_submission_submitted">
                            {0}
                        </td>
        """.format(
            TemplateSwordClient._humanize_datetime(
                submitted,
                ln
            )
        )

        table_row += """
                        <td class="sword_client_submission_status">
                            {0}
                        </td>
        """.format(status)

        table_row += """
                        <td class="sword_client_submission_last_updated">
                            {0}
                        </td>
        """.format(
            TemplateSwordClient._humanize_datetime(
                last_updated,
                ln
            )
        )

        # ↺ --> &#8634;
        html_options = """
                            <a class="bibsword_anchor font_size_150percent" data-option="update" data-action="submit" data-server_id="{0}" data-status_url="{1}" data-ln="{2}" href="javascript:void(0)">&#8634;</a>
        """

        table_row += """
                        <td class="sword_client_submission_option text_align_center">
                            {0}
                        </td>
        """.format(html_options.format(server_id, status_url, ln))

        table_row += """
                    </tr>
        """

        return table_row

    def tmpl_submissions(
        self,
        submissions,
        ln
    ):
        """
        Returns the submissions table with all information and options.
        """

        _ = gettext_set_language(ln)

        html = """
            <script>

            $(document).ready(function(){{

                $("table.bibsword_table td.sword_client_submission_option").on("click", "a:not('.temporarily_disabled')", function(){{

                    var sword_client_submission_option_element = $(this);
                    var sword_client_submission_option_data = sword_client_submission_option_element.data();
                    var sword_client_submission_option_data_option = sword_client_submission_option_data["option"];

                    $.ajax({{

                        url: "/sword_client/submission_options",

                        data: sword_client_submission_option_data,

                        beforeSend: function(){{
                            if ( sword_client_submission_option_data_option == "update" ) {{
                                sword_client_submission_option_element.parent().children("a:not('.temporarily_disabled')").addClass("temporarily_disabled");
                            }}
                        }},

                        success: function(data){{

                            if ( sword_client_submission_option_data_option == "update" ) {{
                                data = JSON.parse(data);
                                sword_client_submission_option_element.parent().siblings("td.sword_client_submission_status").html(data["status"]);
                                sword_client_submission_option_element.parent().siblings("td.sword_client_submission_last_updated").html(data["last_updated"]);
                            }}

                        }},

                        error: function(jqXHR) {{
                            alert("{error_message}");
                        }},

                        complete: function(){{
                            if ( sword_client_submission_option_data_option == "update" ) {{
                                sword_client_submission_option_element.parent().children("a.temporarily_disabled").removeClass("temporarily_disabled");
                            }}
                        }},

                    }});

                }});

            }});

            </script>

            <table class="bibsword_table">
                <thead>
                    <tr>
                        <th>
                            {user_header_label}
                        </th>
                        <th>
                            {record_header_label}
                        </th>
                        <th>
                            {server_header_label}
                        </th>
                        <th>
                            {submitted_header_label}
                        </th>
                        <th>
                            {status_header_label}
                        </th>
                        <th>
                            {updated_header_label}
                        </th>
                        <th>
                            {options_header_label}
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {tbody}
                </tbody>
                <tfoot>
                </tfoot>
            </table>
        """

        html_tbody = ""

        for submission in submissions:
            html_tbody += TemplateSwordClient._tmpl_submission_table_row(
                submission,
                ln
            )

        return html.format(
            error_message=_("An error has occured. " +
                            "The administrators have been informed."),
            user_header_label=_("User"),
            record_header_label=_("Record"),
            server_header_label=_("Server"),
            submitted_header_label=_("Submitted"),
            status_header_label=_("Status"),
            updated_header_label=_("Last updated"),
            options_header_label=_("Options"),
            tbody=html_tbody
        )

    @staticmethod
    def _tmpl_server_table_row(
        server,
        ln
    ):
        """
        Returns the HTML code for a server table row.
        """
        (server_id,
         name,
         engine,
         username,
         dummy,
         email,
         dummy,
         update_frequency,
         last_updated) = server

        table_row = """
                    <tr id="server_id_{0}">
        """.format(server_id)

        table_row += """
                        <td class="sword_client_server_name">
                            {0}
                        </td>
        """.format(name)

        table_row += """
                        <td class="sword_client_server_engine">
                            {0}
                        </td>
        """.format(engine)

        table_row += """
                        <td class="sword_client_server_username">
                            {0}
                        </td>
        """.format(username)

        table_row += """
                        <td class="sword_client_server_email">
                            {0}
                        </td>
        """.format(email)

        table_row += """
                        <td class="sword_client_server_update_frequency">
                            {0}
                        </td>
        """.format(
            TemplateSwordClient._humanize_frequency(
                update_frequency,
                ln
            )
        )

        table_row += """
                        <td class="sword_client_server_last_updated">
                            {0}
                        </td>
        """.format(
            TemplateSwordClient._humanize_datetime(
                last_updated,
                ln
            )
        )

        # ↺ --> &#8634;
        # ✎ --> &#9998;
        # ✗ --> &#10007;
        html_options = """
                            <a class="bibsword_anchor font_size_150percent" data-option="update" data-action="submit" data-server_id="{0}" data-ln="{1}" href="javascript:void(0)">&#8634;</a>
                            &nbsp;
                            <a class="bibsword_anchor font_size_150percent" data-option="modify" data-action="prepare" data-server_id="{0}" data-ln="{1}" href="javascript:void(0)">&#9998;</a>
                            &nbsp;
                            <a class="bibsword_anchor font_size_150percent" data-option="delete" data-action="submit" data-server_id="{0}" data-ln="{1}" href="javascript:void(0)">&#10007;</a>
        """

        table_row += """
                        <td class="sword_client_server_option">
                            {0}
                        </td>
        """.format(html_options.format(server_id, ln))

        table_row += """
                    </tr>
        """

        return table_row

    def tmpl_servers(
        self,
        servers,
        ln
    ):
        """
        Returns the servers table with all information and available options.
        """

        _ = gettext_set_language(ln)

        # ⊕ --> &oplus;
        html = """
            <script>

            $(document).ready(function(){{

                $(".bibsword_table, .sword_client_server_add").on("click", "a:not('.temporarily_disabled')", function(){{

                    var sword_client_server_option_element = $(this);
                    var sword_client_server_option_data = sword_client_server_option_element.data();
                    var sword_client_server_option_data_option = sword_client_server_option_data["option"];

                    if ( sword_client_server_option_data_option == "delete" ) {{
                        if ( confirm("{confirm_delete_label}") == false) {{
                            return;
                        }}
                    }}

                    $.ajax({{

                        url: "/sword_client/server_options",

                        data: sword_client_server_option_data,

                        beforeSend: function(){{
                            if ( sword_client_server_option_data_option == "delete" || sword_client_server_option_data_option == "update" ) {{
                                sword_client_server_option_element.parent().children("a:not('.temporarily_disabled')").addClass("temporarily_disabled");
                            }}
                        }},

                        success: function(data){{

                            if ( sword_client_server_option_data_option == "add" || sword_client_server_option_data_option == "modify" ) {{
                                $("body").append(data);
                            }}

                            if ( sword_client_server_option_data_option == "delete" ) {{
                                sword_client_server_option_element.parent().parent().hide(300).remove();
                            }}

                            if ( sword_client_server_option_data_option == "update" ) {{
                                sword_client_server_option_element.parent().siblings("td.sword_client_server_last_updated").text(data);
                            }}

                        }},

                        error: function(jqXHR) {{
                            alert("{error_message}");
                        }},

                        complete: function(){{
                            if ( sword_client_server_option_data_option == "delete" || sword_client_server_option_data_option == "update" ) {{
                                sword_client_server_option_element.parent().children("a.temporarily_disabled").removeClass("temporarily_disabled");
                            }}
                        }},

                    }});

                }});

            }});

            </script>

            <div class="margin_10px sword_client_server_add">
                <a class="bibsword_anchor" data-option="add" data-action="prepare" data-ln="{ln}" href="javascript:void(0)">
                    <span class="font_size_150percent">&oplus;</span>&nbsp;{add_label}
                </a>
            </div>

            <table class="bibsword_table">
                <thead>
                    <tr>
                        <th>
                            {name_header_label}
                        </th>
                        <th>
                            {engine_header_label}
                        </th>
                        <th>
                            {username_header_label}
                        </th>
                        <th>
                            {email_header_label}
                        </th>
                        <th>
                            {frequency_header_label}
                        </th>
                        <th>
                            {last_updated_header_label}
                        </th>
                        <th>
                            {options_header_label}
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {tbody}
                </tbody>
                <tfoot>
                </tfoot>
            </table>
        """

        html_tbody = ""

        for server in servers:
            html_tbody += TemplateSwordClient._tmpl_server_table_row(
                server,
                ln
            )

        return html.format(
            confirm_delete_label=_(
                "Are you sure you want to delete this server?"
            ),
            add_label=_("Add server"),
            error_message=_("An error has occured. " +
                            "The administrators have been informed."),
            name_header_label=_("Name"),
            engine_header_label=_("Engine"),
            username_header_label=_("Username"),
            email_header_label=_("E-mail"),
            frequency_header_label=_("Update frequency"),
            last_updated_header_label=_("Last updated"),
            options_header_label=_("Options"),
            tbody=html_tbody,
            ln=ln
        )

    def tmpl_add_or_modify_server(
        self,
        server,
        available_engines,
        ln
    ):
        """
        Returns the servers table with all information and available options.
        """

        _ = gettext_set_language(ln)

        if server:
            (server_id,
             name,
             engine,
             username,
             password,
             email,
             dummy,
             update_frequency,
             dummy) = server
            label = _("Modify server")
            content = """
                <input type="hidden" name="option" value="modify">
                <input type="hidden" name="action" value="submit">
                <input type="hidden" name="server_id" value="{0!s}">
            """.format(server_id)
            controls = ""
        else:
            (server_id,
             name,
             engine,
             username,
             password,
             email,
             dummy,
             update_frequency,
             dummy) = ("",)*9
            label = _("Add server")
            content = """
                <input type="hidden" name="option" value="add">
                <input type="hidden" name="action" value="submit">
            """
            controls = ""

        html_input = """
            <div>
                <div>
                    <label class="bibsword_modal_content_field_title">
                        {title}:
                    </label>
                    <br />
                    <div class="bibsword_modal_content_field_subtitle">
                        {subtitle}
                    </div>
                </div>
                <div class="display_inline">
                    <input type="{input_type}" name="{name}" value="{value}" size="{size}" placeholder="{placeholder}" />
                </div>
            </div>
        """

        html_select_option = """
                        <option value="{value}"{selected}>{label}</option>
        """

        html_select = """
            <div>
                <div>
                    <label class="bibsword_modal_content_field_title">
                        {title}:
                    </label>
                    <br />
                    <div class="bibsword_modal_content_field_subtitle">
                        {subtitle}
                    </div>
                </div>
                <div class="display_inline">
                    <select name={name}>
                        {options}
                    </select>
                </div>
            </div>
        """

        content += html_input.format(
            title=_("Server name"),
            subtitle=_("A custom name for the server that you can then choose to submit to."),
            input_type="text",
            name="sword_client_server_name",
            value=escape(name, True),
            size="50%",
            placeholder="example.com SWORD server"
        )

        content += html_select.format(
            title=_("Server engine"),
            subtitle=_("The server engine to connect to."),
            name="sword_client_server_engine",
            options="".join(
                [html_select_option.format(
                    value=escape(available_engine, True),
                    selected=" selected" if available_engine == engine else "",
                    label=escape(available_engine, True)
                ) for available_engine in available_engines]
            )
        )

        content += html_input.format(
            title=_("Username"),
            subtitle=_("The username used to connect to the server."),
            input_type="text",
            name="sword_client_server_username",
            value=escape(username, True),
            size="50%",
            placeholder="johndoe"
        )

        content += html_input.format(
            title=_("Password"),
            subtitle=_("The password used to connect to the server."),
            input_type="password",
            name="sword_client_server_password",
            value=password,
            size="50%",
            placeholder="pa55w0rd"
        )

        content += html_input.format(
            title=_("E-mail"),
            subtitle=_("The e-mail of the user that connects to the server."),
            input_type="text",
            name="sword_client_server_email",
            value=escape(email, True),
            size="50%",
            placeholder="johndoe@example.com"
        )

        content += html_input.format(
            title=_("Update frequency"),
            subtitle=_("How often should the server be checked for updates?" +
                       " The update frequency must be expressed in units of" +
                       " weeks (w), days (d), hours(h), minutes (m) and" +
                       " seconds (s) as a single string with no spaces." +
                       " For example, \"1w3d\" means \"Every 1 week and 3" +
                       " days\" and \"6h30m10s\" means \"Every 6 hours," +
                       " 30 minutes and 10 seconds\"."),
            input_type="text",
            name="sword_client_server_update_frequency",
            value=escape(update_frequency, True),
            size="50%",
            placeholder="1w3d"
        )

        controls += """
            <button class="sword_client_server_control" name="cancel" type="button">{label}</button>
        """.format(
            label=_("Cancel")
        )

        controls += """
            &nbsp;
        """

        controls += """
            <button class="sword_client_server_control" name="submit" type="button">{label}</button>
        """.format(
            label=_("Submit")
        )

        html = """
            <script>

            $(document).ready(function(){{

                $("button.sword_client_server_control[name='cancel']").on("click", function(){{

                    var sword_client_server_option_element = $(this);
                    if ( sword_client_server_option_element.hasClass("temporarily_disabled") ) {{
                        return;
                    }}
                    sword_client_server_option_element.parents("div.bibsword_modal_outer").remove();

                }});

                $("button.sword_client_server_control[name='submit']").on("click", function(){{

                    var sword_client_server_option_element = $(this);
                    if ( sword_client_server_option_element.hasClass("temporarily_disabled") ) {{
                        return;
                    }}
                    var sword_client_server_option_data_element = $("form[name='sword_client_server_form']");
                    var sword_client_server_option_data = sword_client_server_option_data_element.serialize();
                    var sword_client_server_option_data_option = sword_client_server_option_data_element.children("input[name='option']").val();
                    var sword_client_server_option_data_server_id = sword_client_server_option_data_element.children("input[name='server_id']").val();

                    $.ajax({{

                        url: "/sword_client/server_options",

                        data: sword_client_server_option_data,

                        beforeSend: function(){{
                            sword_client_server_option_element.parent().children("button:not('.temporarily_disabled')").addClass("temporarily_disabled");
                        }},

                        success: function(data){{

                            if ( sword_client_server_option_data_option == "add" ) {{
                                $(data).hide().appendTo("table.bibsword_table tbody").fadeIn(300);
                            }}

                            if ( sword_client_server_option_data_option == "modify" ) {{
                                var sword_client_server = $("#server_id_" + sword_client_server_option_data_server_id);
                                data = JSON.parse(data);
                                sword_client_server.children("td.sword_client_server_name").text(data["name"]);
                                sword_client_server.children("td.sword_client_server_engine").text(data["engine"]);
                                sword_client_server.children("td.sword_client_server_username").text(data["username"]);
                                sword_client_server.children("td.sword_client_server_email").text(data["email"]);
                                sword_client_server.children("td.sword_client_server_update_frequency").text(data["update_frequency"]);
                            }}

                        }},

                        error: function(jqXHR) {{
                            alert("{error_message}");
                        }},

                        complete: function(){{
                            sword_client_server_option_element.parent().children("button.temporarily_disabled").removeClass("temporarily_disabled");
                            sword_client_server_option_element.parents("div.bibsword_modal_outer").remove();
                        }},

                    }});

                }});

            }});

            </script>

            <div class="bibsword_modal_outer">
                <div class="bibsword_modal_inner">
                    <div class="bibsword_modal_label">
                        {label}
                    </div>
                    <div class="bibsword_modal_content">
                        <form name="sword_client_server_form">
                            {content}
                        <form>
                    </div>
                    <div class="bibsword_modal_controls">
                        {controls}
                    </div>
                </div>
            </div>
        """.format(
            label=label,
            content=content,
            controls=controls,
            error_message=_("An error has occured. " +
                            "The administrators have been informed.")
        )

        return html

    @staticmethod
    def _humanize_frequency(
        raw_frequency,
        ln
    ):
        """
        Converts this: "3w4d5h6m7s"
        to this: "Every 3 weeks, 4 days, 5 hours, 6 minutes, 7 seconds"
        """

        _ = gettext_set_language(ln)

        frequency_translation = {
            "w": _("week(s)"),
            "d": _("day(s)"),
            "h": _("hour(s)"),
            "m": _("minute(s)"),
            "s": _("second(s)"),
        }

        humanized_frequency = _("Every")
        humanized_frequency += " "

        frequency_parts = re.findall(
            "([0-9]+)([wdhms]{1})",
            raw_frequency
        )

        frequency_parts = map(
            lambda p: "{0} {1}".format(p[0], frequency_translation[p[1]]),
            frequency_parts
        )

        humanized_frequency += ", ".join(frequency_parts)

        return humanized_frequency

    @staticmethod
    def _humanize_datetime(
        raw_datetime,
        ln
    ):
        """
        Converts this: "2015-02-17 10:10:10"
        to this: "2 week(s), 5 day(s) ago"
        """

        _ = gettext_set_language(ln)

        if not raw_datetime:
            return _("Never")

        passed_datetime = datetime.now() - raw_datetime

        passed_datetime_days = passed_datetime.days

        humanized_datetime_parts = []

        if passed_datetime_days:
            passed_datetime_weeks = passed_datetime_days / 7
            if passed_datetime_weeks:
                humanized_datetime_parts.append(
                    "{0!s} {1}".format(passed_datetime_weeks, _("week(s)"))
                )
            passed_datetime_days = passed_datetime_days % 7
            humanized_datetime_parts.append(
                "{0!s} {1}".format(passed_datetime_days, _("day(s)"))
            )

        else:
            passed_datetime_seconds = passed_datetime.seconds
            passed_datetime_minutes = passed_datetime_seconds / 60
            passed_datetime_hours = passed_datetime_minutes / 60
            if passed_datetime_hours:
                humanized_datetime_parts.append(
                    "{0!s} {1}".format(passed_datetime_hours, _("hour(s)"))
                )
            passed_datetime_minutes = passed_datetime_minutes % 60
            if passed_datetime_minutes:
                humanized_datetime_parts.append(
                    "{0!s} {1}".format(passed_datetime_minutes, _("minute(s)"))
                )
            passed_datetime_seconds = passed_datetime_seconds % 60
            if passed_datetime_seconds:
                humanized_datetime_parts.append(
                    "{0!s} {1}".format(passed_datetime_seconds, _("second(s)"))
                )

        humanized_datetime = ", ".join(humanized_datetime_parts)
        humanized_datetime += " "
        humanized_datetime += _("ago")

        return humanized_datetime

    @staticmethod
    def _submit_prepare_select_tag(
        select_id,
        select_name,
        options,
        default_option=None,
        multiple=False
    ):
        """Prepare the HTML select tag."""
        out = """
        <select id="%s"%s%s>
        """ % (
            select_id,
            select_name and ' name="%s"' % (select_name,) or '',
            multiple and ' multiple="multiple"' or ''
        )

        for option in options:
            option_value = option[0]
            option_text = option[1]
            out += """
            <option value="%s"%s>%s</option>
            """ % (
                escape(str(option_value), True),
                default_option is not None and (
                    option_value == default_option and " selected" or ""
                ) or "",
                escape(str(option_text), True)
            )

        out += """
        </select>
        """

        return out

    def tmpl_submit(
        self,
        sid,
        recid,
        title,
        author,
        report_number,
        step,
        servers,
        server_id,
        ln
    ):
        """
        The main submission interface.

        Through a series of steps, the user is guided through the submission.
        """

        _ = gettext_set_language(ln)

        out = """
<div class="bibsword_submit_container">

    <div class="bibsword_submit_header">
    %(header)s
    </div>

    <div id="bibsword_submit_step_1_title" class="bibsword_submit_step_title">
    %(step_1_title)s
    </div>

    <div id="bibsword_submit_step_1_details" class="bibsword_submit_step_details">
    %(step_1_details)s
    </div>

    <div id="bibsword_submit_step_2_title" class="bibsword_submit_step_title" style="display: none;">
    %(step_2_title)s
    </div>

    <div id="bibsword_submit_step_2_details" class="bibsword_submit_step_details" style="display: none;">
    %(step_2_details)s
    </div>

    <div id="bibsword_submit_step_3_title" class="bibsword_submit_step_title" style="display: none;">
    %(step_3_title)s
    </div>

    <div id="bibsword_submit_step_3_details" class="bibsword_submit_step_details" style="display: none;">
    %(step_3_details)s
    </div>

    <div id="bibsword_submit_step_4_title" class="bibsword_submit_step_title" style="display: none;">
    %(step_4_title)s
    </div>

    <div id="bibsword_submit_step_4_details" class="bibsword_submit_step_details" style="display: none;">
    %(step_4_details)s
    </div>

    <div id="bibsword_submit_step_final_title" class="bibsword_submit_step_title" style="display: none;">
    %(step_final_title)s
    </div>

    <div id="bibsword_submit_step_final_details" class="bibsword_submit_step_details" style="display: none;">
    %(step_final_details)s
    </div>

</div>

<script type="text/javascript" src="%(CFG_SITE_URL)s/js/jquery-ui.min.js"></script>

<script>
// Actions to take following the confirmation of step 1: the selection of the server
$(".bibsword_submit_container").on("click", "#%(step_1_server_confirm_id)s", function () {

    $.ajax({

        url: "/sword_client/submit_step_1",

        data: {
            "sid": "%(sid)s",
            "server_id": $("#%(step_1_server_select_id)s").val(),
            "ln": "%(ln)s"
        },

        beforeSend: function(){
            // Set the new text and color of the current step title (inactive)
            $("#bibsword_submit_step_1_title").html(" %(step_1_title_done_text)s " + $("#%(step_1_server_select_id)s option:selected").html());
            $("#bibsword_submit_step_1_title").css("color", "%(title_done_color)s");
            $("<img>").attr({"style" : "vertical-align:middle", "src" : "%(title_done_image)s"}).prependTo("#bibsword_submit_step_1_title");
            $("#bibsword_submit_step_1_details").hide(%(animation_speed)s, function dummy() {
                $("#bibsword_submit_step_2_title").show(%(animation_speed)s, function dummy() {
                    $("#bibsword_submit_step_2_details").show(%(animation_speed)s);
                });
            });
        },

        success: function(data){
            // Calculate the step 2 details content
            $("#bibsword_submit_step_2_details").html(data);
        },

        error: function(jqXHR) {
            alert("%(error_message)s");
        },

    });

});

// Actions to take following the confirmation of step 2: the selection of the collection
$(".bibsword_submit_container").on("click", "#%(step_2_collection_confirm_id)s", function () {

    $.ajax({

        url: "/sword_client/submit_step_2",

        data: {
            "sid": "%(sid)s",
            "collection_url": $("#%(step_2_collection_select_id)s").val(),
            "ln": "%(ln)s"
        },

        beforeSend: function(){
            // Set the new text and color of the current step title (inactive)
            $("#bibsword_submit_step_2_title").html(" %(step_2_title_done_text)s " + $("#%(step_2_collection_select_id)s option:selected").html());
            $("#bibsword_submit_step_2_title").css("color", "%(title_done_color)s");
            $("<img>").attr({"style" : "vertical-align:middle", "src" : "%(title_done_image)s"}).prependTo("#bibsword_submit_step_2_title");
            $("#bibsword_submit_step_2_details").hide(%(animation_speed)s, function dummy() {
                $("#bibsword_submit_step_3_title").show(%(animation_speed)s, function dummy() {
                    $("#bibsword_submit_step_3_details").show(%(animation_speed)s);
                });
            });
        },

        success: function(data){
            // Calculate the step 3 details content
            $("#bibsword_submit_step_3_details").html(data);
        },

        error: function(jqXHR) {
            alert("%(error_message)s");
        },

    });

});

// Actions to take during step 3: addition of optional categories
var optional_categories_urls = [];
//TODO: What should this number be?
var maximum_number_of_optional_categories = 4;
$("#bibsword_submit_step_3_details").on("click", "#%(step_3_optional_categories_add_id)s", function () {

    // Is the adding optional categories enabled?
    var disabled_status = $("#%(step_3_optional_categories_add_id)s").attr("disabled");
    if ( disabled_status == "disabled" ) {
        return;
    }

    // Get the index of the currently selected option
    var current_index = $("#%(step_3_optional_categories_select_id)s option:selected").index();
    var current_index_plus_one = current_index + 1;

    // Let's make sure there was a valid option to select in the first place
    if ( current_index >= 0 ) {

        // Get the option's value and text
        var current_option = $("#%(step_3_optional_categories_select_id)s").val();
        var current_label  = $("#%(step_3_optional_categories_select_id)s option:selected").text();

        // Push the option's value to the optional_categories_urls
        optional_categories_urls.push(current_option);

        // Create and append the optional category
        var current_added_item = '<li class="bibsword_submit_step_details_legend_item">';
        current_added_item    += '<span value="' + current_option + '">' + current_label + '</span>';
        current_added_item    += "&nbsp;";
        current_added_item    += '<img src="%(step_3_optional_categories_remove_image)s"/>';
        current_added_item    += "</li>";
        $("#%(step_3_optional_categories_legend_id)s").append(current_added_item);

        // Remove the added optional category from the select element
        // and automatically select the next option in the list.
        ////$("#%(step_3_optional_categories_select_id)s option:selected").remove();
        $("#%(step_3_optional_categories_select_id)s option:selected").attr("disabled", "disabled");
        $("#%(step_3_optional_categories_select_id)s option:eq(" + current_index_plus_one + ")").attr("selected", "selected");

        if ( maximum_number_of_optional_categories > 0 && optional_categories_urls.length >= maximum_number_of_optional_categories ) {
            $("#%(step_3_optional_categories_add_id)s").attr("disabled", "disabled");
            $("#%(step_3_optional_categories_add_id)s strong").html("maximum already reached");
        }

    }

});

// Actions to take during step 3: removal of optional categories
$("#bibsword_submit_step_3_details").on("click", "#%(step_3_optional_categories_legend_id)s img", function () {

    // Get the option's value and text
    var current_option = $(this).siblings("span").attr("value");
    var current_label  = $(this).siblings("span").text();

    // Check if the option exists in the optional_categories_urls
    var current_option_index = optional_categories_urls.indexOf(current_option)
    if ( current_option_index != -1 ) {

        // Remove the option's value from the optional_categories_urls
        optional_categories_urls.splice(current_option_index, 1)

        // Remove the optional category from the list of added optional categories
        // Use .remove() or .detach() ?
        $(this).parent().remove();

        // Add this optional category in the optional categories select again
        $("#%(step_3_optional_categories_select_id)s option[value='" + current_option + "']").attr("disabled", false);

        if ( maximum_number_of_optional_categories > 0 && optional_categories_urls.length < maximum_number_of_optional_categories ) {
            $("#%(step_3_optional_categories_add_id)s").attr("disabled", false);
            $("#%(step_3_optional_categories_add_id)s strong").html("&#10010;");
        }

    }

});

// Actions to take following the confirmation of step 3: the selection of the categories
$(".bibsword_submit_container").on("click", "#%(step_3_categories_confirm_id)s", function () {

    $.ajax({

        url: "/sword_client/submit_step_3",

        data: $.param({
            "sid": "%(sid)s",
            "mandatory_category_url": $("#%(step_3_mandatory_category_select_id)s").val(),
            "optional_categories_urls": optional_categories_urls,
            "ln": "%(ln)s"
        }, true),

        beforeSend: function(){
            // Set the new text and color of the step 3 title (inactive)
            if ( optional_categories_urls.length > 0 ) {
                $("#bibsword_submit_step_3_title").html(" %(step_3_title_done_text_part_1)s " + $("#%(step_3_mandatory_category_select_id)s option:selected").html() + " (+" + optional_categories_urls.length.toString() + " %(step_3_title_done_text_part_2)s)");
            }
            else {
                $("#bibsword_submit_step_3_title").html(" %(step_3_title_done_text_part_1)s " + $("#%(step_3_mandatory_category_select_id)s option:selected").html());
            }
            $("#bibsword_submit_step_3_title").css("color", "%(title_done_color)s");
            $("<img>").attr({"style" : "vertical-align:middle", "src" : "%(title_done_image)s"}).prependTo("#bibsword_submit_step_3_title");
            $("#bibsword_submit_step_3_details").hide(%(animation_speed)s, function dummy() {
                $("#bibsword_submit_step_4_title").show(%(animation_speed)s, function dummy() {
                    $("#bibsword_submit_step_4_details").show(%(animation_speed)s);
                });
            });
        },

        success: function(data){
            // Calculate the step 4 details content
            $("#bibsword_submit_step_4_details").html(data);
        },

        complete: function(data){
            // Make some of the submission fields sortable
            $("#bibsword_submit_step_4_additional_rn_sortable").sortable({
                placeholder: "highlight"
            });
            $("#bibsword_submit_step_4_contributors_sortable").sortable({
                placeholder: "highlight"
            });
        },

        error: function(jqXHR) {
            alert("%(error_message)s");
        },

    });

});

// Actions to take during step 4: inserting and removing additional report numbers
$("#bibsword_submit_step_4_details").on("click", ".%(step_4_additional_rn_insert_class)s", function () {
    var data = '%(step_4_additional_rn_insert_data)s';
    $("#bibsword_submit_step_4_additional_rn_sortable").append(data);
});
$("#bibsword_submit_step_4_details").on("click", ".%(step_4_additional_rn_remove_class)s", function () {
    $(this).parent().parent().hide(%(animation_speed)s, function dummy() {
        $(this).remove();
    });
});

// Actions to take during step 4: inserting and removing contributors
$("#bibsword_submit_step_4_details").on("click", ".%(step_4_contributors_insert_class)s", function () {
    var data = '%(step_4_contributors_insert_data)s';
    $("#bibsword_submit_step_4_contributors_sortable").append(data);
});
$("#bibsword_submit_step_4_details").on("click", ".%(step_4_contributors_remove_class)s", function () {
    $(this).parent().parent().hide(%(animation_speed)s, function dummy() {
        $(this).remove();
    });
});

// Actions to take following the confirmation of step 4: the submission
$(".bibsword_submit_container").on("click", "#%(step_4_submission_confirm_id)s", function () {

    $.ajax({

        url: "/sword_client/submit_step_4",

        data: $.param({
            "sid": "%(sid)s",
            "rn": $("#%(step_4_submission_data_id)s input[name='rn']").val(),
            "additional_rn": $("#%(step_4_submission_data_id)s input[name='additional_rn']").serializeArray().map(function(element){return element.value;}),
            "title": $("#%(step_4_submission_data_id)s input[name='title']").val(),
            "author_fullname": $("#%(step_4_submission_data_id)s input[name='author_fullname']").val(),
            "author_email": $("#%(step_4_submission_data_id)s input[name='author_email']").val(),
            "author_affiliation": $("#%(step_4_submission_data_id)s input[name='author_affiliation']").val(),
            "abstract": $("#%(step_4_submission_data_id)s textarea[name='abstract']").val(),
            "contributor_fullname": $("#%(step_4_submission_data_id)s input[name='contributor_fullname']").serializeArray().map(function(element){return element.value;}),
            "contributor_email": $("#%(step_4_submission_data_id)s input[name='contributor_email']").serializeArray().map(function(element){return element.value;}),
            "contributor_affiliation": $("#%(step_4_submission_data_id)s input[name='contributor_affiliation']").serializeArray().map(function(element){return element.value;}),
            "files": $("#%(step_4_submission_data_id)s input[name='files']").serializeArray().map(function(element){return element.value;}),
            "ln": "%(ln)s"
        }, true),

        beforeSend: function(){
            // Set the new text and color of the step 4 title (inactive)
            $("#bibsword_submit_step_4_title").html(" %(step_4_title_done_text)s");
            $("#bibsword_submit_step_4_title").css("color", "%(title_done_color)s");
            $("<img>").attr({"style" : "vertical-align:middle", "src" : "%(title_done_image)s"}).prependTo("#bibsword_submit_step_4_title");

            // Hide the current step details and show the next title and details
            $("#bibsword_submit_step_4_details").hide(%(animation_speed)s, function dummy() {
                $("#bibsword_submit_step_final_title").show(%(animation_speed)s, function dummy() {
                    $("#bibsword_submit_step_final_details").show(%(animation_speed)s);
                    });
                });
        },

        success: function(data){
            // Set the new text and color of the final step title (inactive)
            $("#bibsword_submit_step_final_title").html(" %(step_final_title_done_text)s");
            $("#bibsword_submit_step_final_title").css("color", "%(title_done_color)s");
            $("<img>").attr({"style" : "vertical-align:middle", "src" : "%(title_done_image)s"}).prependTo("#bibsword_submit_step_final_title");

            // Calculate the final step details content
            $("#bibsword_submit_step_final_details").html(data);
        },

        error: function(jqXHR) {
            alert("%(error_message)s");
        },

    });

});

// We might want to jump to a specific step directly
if ( "%(step)s" == "1" ) {
    $("#%(step_1_server_confirm_id)s").trigger("click");
};

</script>

        """ % {
            "header": self._submit_header(
                recid,
                title,
                author,
                report_number,
                ln
            ),

            "step_1_title": _("Where would you like to submit?"),
            "step_1_details": self.submit_step_1_details(
                servers,
                server_id,
                ln
            ),
            "step_1_title_done_text": _("Selected server:"),
            "step_1_server_select_id": "bibsword_submit_step_1_select",
            "step_1_server_confirm_id": "bibsword_submit_step_1_confirm",

            "step_2_title": _("What collection would you like to submit to?"),
            "step_2_details": self._submit_loading(ln),
            "step_2_title_done_text": _("Selected collection:"),
            "step_2_collection_select_id": "bibsword_submit_step_2_select",
            "step_2_collection_confirm_id": "bibsword_submit_step_2_confirm",

            "step_3_title": _("What category would you like to submit to?"),
            "step_3_details": self._submit_loading(ln),
            "step_3_optional_categories_add_id":
                "bibsword_submit_step_3_optional_categories_add",
            "step_3_optional_categories_select_id":
                "bibsword_submit_step_3_optional_categories_select",
            "step_3_optional_categories_legend_id":
                "bibsword_submit_step_3_optional_categories_legend",
            "step_3_optional_categories_remove_image":
                "%s/%s" % (CFG_SITE_URL, "img/cross_red.gif"),
            "step_3_title_done_text_part_1": _("Selected category:"),
            "step_3_title_done_text_part_2": _("additional categories"),
            "step_3_mandatory_category_select_id":
                "bibsword_submit_step_3_mandatory_category_select",
            "step_3_categories_confirm_id":
                "bibsword_submit_step_3_collection_confirm",

            "step_4_additional_rn_insert_class":
                "bibsword_submit_step_4_additional_rn_insert",
            "step_4_additional_rn_insert_data":
                "".join(TemplateSwordClient._submit_step_4_additional_rn_input_block(
                    name='additional_rn',
                    value='',
                    size='25',
                    placeholder=_('Report number...'),
                    sortable_label=_("&#8691;"),
                    remove_class='bibsword_submit_step_4_additional_rn_remove negative',
                    remove_label=_("&#10008;")
                ).splitlines()),
            "step_4_additional_rn_remove_class":
                "bibsword_submit_step_4_additional_rn_remove",
            "step_4_contributors_insert_class":
                "bibsword_submit_step_4_contributors_insert",
            "step_4_contributors_insert_data":
                "".join(TemplateSwordClient._submit_step_4_contributors_input_block(
                    fullname=(
                        _('Fullname:'),
                        'contributor_fullname',
                        '',
                        '25',
                        _('Fullname...'),
                    ),
                    email=(
                        _('E-mail:'),
                        'contributor_email',
                        '',
                        '35',
                        _('E-mail...'),
                    ),
                    affiliation=(
                        _('Affiliation:'),
                        'contributor_affiliation',
                        '',
                        '35',
                        _('Affiliation...'),
                    ),
                    sortable_label=_("&#8691;"),
                    remove_class='bibsword_submit_step_4_contributors_remove negative',
                    remove_label=_("&#10008;")
                ).splitlines()),
            "step_4_contributors_remove_class":
                "bibsword_submit_step_4_contributors_remove",
            "step_4_title":
                _("Please review and, if needed," +
                  " correct the following information:"),
            "step_4_details": self._submit_loading(ln),
            "step_4_title_done_text": _(
                "All the information has been prepared for submission"
            ),
            "step_4_submission_data_id": "bibsword_submit_step_4_submission_data",
            "step_4_submission_confirm_id": "bibsword_submit_step_4_submission_confirm",

            "step_final_title": _(
                "Please wait while your submission is being processed..."
            ),
            "step_final_details": self._submit_loading(ln),
            "step_final_title_done_text": _(
                "Your submission has been processed"
            ),

            "title_done_color": "#999999",
            "title_done_image": "%s/%s" % (CFG_SITE_URL, "img/aid_check.png"),
            "animation_speed": 300,
            "error_message": _("An error has occured. " +
                               "The administrators have been informed."),

            "CFG_SITE_URL": CFG_SITE_URL,
            "sid": sid,
            "step": step,
            "ln": ln,
        }

        return out

    def _submit_header(
        self,
        record_id,
        title,
        author,
        report_number,
        ln
    ):
        """
        """

        _ = gettext_set_language(ln)

        out = """
        {submitting} <strong><a target="_blank" href="{CFG_SITE_URL}/{CFG_SITE_RECORD}/{record_id}">{title}</a></strong> ({report_number}) {by} <strong>{author}</strong>
        """.format(
            submitting=_("You are submitting:"),
            CFG_SITE_URL=CFG_SITE_URL,
            CFG_SITE_RECORD=CFG_SITE_RECORD,
            record_id=record_id,
            title=escape(title, True),
            report_number=escape(report_number, True),
            by=_("by"),
            author=escape(author, True)
        )

        return out

    def _submit_loading(self, ln):
        """
        NOTE_2015
        """

        _ = gettext_set_language(ln)

        out = """
        <img style="vertical-align:middle" src="%s/%s" /> &nbsp; %s
        """ % (CFG_SITE_URL, "img/loading.gif", _("Loading..."))
        return out

    def submit_step_1_details(
        self,
        servers,
        server_id,
        ln
    ):
        """
        """

        _ = gettext_set_language(ln)

        confirmation = """
        <button id="%s">%s</button>
        """ % (
            "bibsword_submit_step_1_confirm",
            _("Confirm and continue")
        )

        out = """
        <div class="bibsword_submit_step_details_field">
            <div class="bibsword_submit_step_details_label">
                <label>%(label)s</label>
            </div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                %(selection)s
            </div>
        </div>
        <div class="bibsword_submit_step_details_field">
            <div class="bibsword_submit_step_details_input display_inline_block">
                %(confirmation)s
            </div>
        </div>
        """ % {
            'label': _("Server:"),
            'selection': TemplateSwordClient._submit_prepare_select_tag(
                "bibsword_submit_step_1_select",
                "server_id",
                servers,
                default_option=server_id
            ),
            'confirmation': confirmation,
        }

        return out

    def submit_step_2_details(
        self,
        collections,
        ln
    ):
        """
        NOTE_2015
        """

        _ = gettext_set_language(ln)

        confirmation = """
        <button id="%s">%s</button>
        """ % (
            "bibsword_submit_step_2_confirm",
            _("Confirm and continue")
        )

        out = """
        <div class="bibsword_submit_step_details_field">
            <div class="bibsword_submit_step_details_label">
                <label>%(label)s</label>
            </div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                %(selection)s
            </div>
        </div>
        <div class="bibsword_submit_step_details_field">
            <div class="bibsword_submit_step_details_input display_inline_block">
                %(confirmation)s
            </div>
        </div>
        """ % {
            "label": _("Collection:"),
            "selection": TemplateSwordClient._submit_prepare_select_tag(
                "bibsword_submit_step_2_select",
                "collection_url",
                collections
            ),
            "confirmation": confirmation
        }

        return out

    def submit_step_3_details(
        self,
        mandatory_categories,
        optional_categories,
        ln
    ):
        """
        """

        _ = gettext_set_language(ln)

        confirmation = """
        <button id="%s">%s</button>
        """ % (
            "bibsword_submit_step_3_collection_confirm",
            _("Confirm and continue")
        )

        # TODO: Different SWORD servers will have different concepts
        # of categories (mandatory, optional, etc). Write a function
        # that accomodates all cases.
        if not mandatory_categories:
            mandatory_categories = optional_categories
            optional_categories = None

        out = """
        <div class="bibsword_submit_step_details_field">
            <div class="bibsword_submit_step_details_label">
                <label>%(label)s</label>
            </div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                %(primary_category_selection)s
            </div>
        </div>
        """ % {
            'label': _("Category:"),
            'primary_category_selection':
                TemplateSwordClient._submit_prepare_select_tag(
                    "bibsword_submit_step_3_mandatory_category_select",
                    "mandatory_category_url",
                    mandatory_categories
                ),
        }

        if optional_categories:

            addition = """
            <button id="%s">%s</button>
            """ % (
                "bibsword_submit_step_3_optional_categories_add",
                "<strong>" + _("&#10010;") + "</strong>"
            )

            out += """
            <div class="bibsword_submit_step_details_field">
                <div class="bibsword_submit_step_details_label">
                    <label>%(label)s</label>
                </div>
                <div class="bibsword_submit_step_details_input display_inline_block">
                    %(additional_category_selection)s
                    %(addition)s
                </div>
                <div class="bibsword_submit_step_details_legend">
                    <ul id="%(additional_category_legend_id)s">
                    </ul>
                </div>
            </div>
            """ % {
                "label": _("Additional optional categories:"),
                "additional_category_selection":
                    TemplateSwordClient._submit_prepare_select_tag(
                        "bibsword_submit_step_3_optional_categories_select",
                        None,
                        optional_categories
                    ),
                "addition": addition,
                "additional_category_legend_id":
                    "bibsword_submit_step_3_optional_categories_legend",
            }

        out += """
        <div class="bibsword_submit_step_details_field">
            <div class="bibsword_submit_step_details_input display_inline_block">
                %(confirmation)s
            </div>
        </div>
        """ % {
            "confirmation": confirmation,
        }

        return out

    @staticmethod
    def _submit_step_4_additional_rn_input_block(
        name,
        value,
        size,
        placeholder,
        sortable_label,
        remove_class,
        remove_label
    ):
        """
        """

        out = """
        <div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                <span class="sortable">%(sortable_label)s</span>
                <input type="text" name="%(name)s" value="%(value)s" size="%(size)s" placeholder="%(placeholder)s" />
                <button class="%(remove_class)s"><strong>%(remove_label)s</strong></button>
            </div>
        </div>
        """ % {
            'name': name,
            'value': value,
            'size': size,
            'placeholder': placeholder,
            'sortable_label': sortable_label,
            'remove_class': remove_class,
            'remove_label': remove_label,
        }

        return out

    @staticmethod
    def _submit_step_4_contributors_input_block(
        fullname,
        email,
        affiliation,
        sortable_label,
        remove_class,
        remove_label
    ):
        """
        """

        out = """
        <div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                <span class="sortable">%(sortable_label)s</span>
            </div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                <div>
                    <label>%(label_fullname)s</label>
                </div>
                <div>
                    <input type="text" name="%(name_fullname)s" value="%(value_fullname)s" size="%(size_fullname)s" placeholder="%(placeholder_fullname)s" />
                </div>
            </div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                <div>
                    <label>%(label_email)s</label>
                </div>
                <div>
                    <input type="text" name="%(name_email)s" value="%(value_email)s" size="%(size_email)s" placeholder="%(placeholder_email)s" />
                </div>
            </div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                <div>
                    <label>%(label_affiliation)s</label>
                </div>
                <div>
                    <input type="text" name="%(name_affiliation)s" value="%(value_affiliation)s" size="%(size_affiliation)s" placeholder="%(placeholder_affiliation)s" />
                </div>
            </div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                <button class="%(remove_class)s"><strong>%(remove_label)s</strong></button>
            </div>
        </div>
        """ % {
            'label_fullname': fullname[0],
            'name_fullname': fullname[1],
            'value_fullname': fullname[2],
            'size_fullname': fullname[3],
            'placeholder_fullname': fullname[4],

            'label_email': email[0],
            'name_email': email[1],
            'value_email': email[2],
            'size_email': email[3],
            'placeholder_email': email[4],

            'label_affiliation': affiliation[0],
            'name_affiliation': affiliation[1],
            'value_affiliation': affiliation[2],
            'size_affiliation': affiliation[3],
            'placeholder_affiliation': affiliation[4],

            'sortable_label': sortable_label,
            'remove_class': remove_class,
            'remove_label': remove_label,
        }

        return out

    def submit_step_4_details(
        self,
        metadata,
        files,
        maximum_number_of_contributors,
        ln
    ):
        """
        """

        _ = gettext_set_language(ln)

        #######################################################################
        # Confirmation button
        #######################################################################
        confirmation_text = """
        <div class="bibsword_submit_step_details_field">
            <div class="bibsword_submit_step_details_input display_inline_block">
                <button id="%(id)s">%(value)s</button>
            </div>
        </div>
        """ % {
            'id': "bibsword_submit_step_4_submission_confirm",
            'value': _("Confirm and submit"),
        }

        #######################################################################
        # Title
        #######################################################################
        title_text = """
        <div class="bibsword_submit_step_details_field">
            <div class="bibsword_submit_step_details_label">
                <label>%(label)s</label>
            </div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                <input class="mandatory" type="text" name="%(name)s" value="%(value)s" size="%(size)s" placeholder="%(placeholder)s" />
            </div>
        </div>
        """ % {
            'label': _('Title:'),
            'placeholder': _('Title...'),
            'value': metadata['title'] and escape(metadata['title'], True) or '',
            'size': '100',
            'name': 'title',
        }

        #######################################################################
        # Author
        #######################################################################
        author_text = """
        <div class="bibsword_submit_step_details_field">
            <div class="bibsword_submit_step_details_label">
                <label>%(label)s</label>
            </div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                <div>
                    <label>%(label_fullname)s</label>
                </div>
                <div>
                    <input class="mandatory" type="text" name="%(name_fullname)s" value="%(value_fullname)s" size="%(size_fullname)s" placeholder="%(placeholder_fullname)s" />
                </div>
            </div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                <div>
                    <label>%(label_email)s</label>
                </div>
                <div>
                    <input class="mandatory" type="text" name="%(name_email)s" value="%(value_email)s" size="%(size_email)s" placeholder="%(placeholder_email)s" />
                </div>
            </div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                <div>
                    <label>%(label_affiliation)s</label>
                </div>
                <div>
                    <input type="text" name="%(name_affiliation)s" value="%(value_affiliation)s" size="%(size_affiliation)s" placeholder="%(placeholder_affiliation)s" />
                </div>
            </div>
        </div>
        """ % {
            'label': _('Author:'),
            'label_fullname': _('Fullname:'),
            'placeholder_fullname': _('Fullname...'),
            'value_fullname': metadata['author'][0] and escape(metadata['author'][0], True) or '',
            'size_fullname': '25',
            'name_fullname': 'author_fullname',
            'label_email': _('E-mail:'),
            'placeholder_email': _('E-mail...'),
            'value_email': metadata['author'][1] and escape(metadata['author'][1], True) or '',
            'size_email': '35',
            'name_email': 'author_email',
            'label_affiliation': _('Affiliation:'),
            'placeholder_affiliation': _('Affiliation...'),
            'value_affiliation': metadata['author'][2] and escape(metadata['author'][2], True) or '',
            'size_affiliation': '35',
            'name_affiliation': 'author_affiliation',
        }

        #######################################################################
        # Contributors
        #######################################################################
        contributors_text = """
        <div class="bibsword_submit_step_details_field">
            <div class="bibsword_submit_step_details_label">
                <label>%(label)s</label>
            </div>
        """ % {
            'label': _('Contributors:'),
        }

        if len(metadata['contributors']) > maximum_number_of_contributors:
            contributors_text += """
            <div class="bibsword_submit_step_details_label">
                <span class="warning">%(text)s</span>
            </div>
            """ % {
                'text': _('Displaying only the first {0}').format(maximum_number_of_contributors),
            }

        contributors_text += """
        <div id="bibsword_submit_step_4_contributors_sortable">
        """

        for contributor in metadata['contributors'][:maximum_number_of_contributors]:

            contributors_text += TemplateSwordClient._submit_step_4_contributors_input_block(
                fullname=(
                    _('Fullname:'),
                    'contributor_fullname',
                    contributor[0] and escape(contributor[0], True) or '',
                    '25',
                    _('Fullname...'),
                ),
                email=(
                    _('E-mail:'),
                    'contributor_email',
                    contributor[1] and escape(contributor[1], True) or '',
                    '35',
                    _('E-mail...'),
                ),
                affiliation=(
                    _('Affiliation:'),
                    'contributor_affiliation',
                    contributor[2] and escape(contributor[2], True) or '',
                    '35',
                    _('Affiliation...'),
                ),
                sortable_label=_("&#8691;"),
                remove_class='bibsword_submit_step_4_contributors_remove negative',
                remove_label=_("&#10008;")
            )

        contributors_text += """
        </div>
        """

        contributors_text += """
        <div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                <button class="%(insert_class)s"><strong>%(insert_label)s</strong></button>
                <label>%(label)s</label>
            </div>
        </div>
        """ % {
            'insert_class': 'bibsword_submit_step_4_contributors_insert positive',
            'insert_label': _("&#10010;"),
            'label': _("Insert another one..."),
        }

        contributors_text += """
        </div>
        """

        #######################################################################
        # Abstract
        #######################################################################
        abstract_text = """
        <div class="bibsword_submit_step_details_field">
            <div class="bibsword_submit_step_details_label">
                <label>%(label)s</label>
            </div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                <textarea class="mandatory" name="%(name)s" rows="%(rows)s" cols="%(cols)s">%(value)s</textarea>
            </div>
        </div>
        """ % {
            'label': _('Abstract:'),
            'value': metadata['abstract'] and escape(metadata['abstract'], True) or '',
            'rows': '10',
            'cols': '120',
            'name': 'abstract',
        }

        #######################################################################
        # Report number
        #######################################################################
        rn_text = """
        <div class="bibsword_submit_step_details_field">
            <div class="bibsword_submit_step_details_label">
                <label>%(label)s</label>
            </div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                <input type="text" name="%(name)s" value="%(value)s" size="%(size)s" placeholder="%(placeholder)s" />
            </div>
        </div>
        """ % {
            'label': _('Report number:'),
            'placeholder': _('Report number...'),
            'value': metadata['rn'] and escape(metadata['rn'], True) or '',
            'size': '25',
            'name': 'rn',
        }

        #######################################################################
        # Additional report numbers
        #######################################################################
        additional_rn_text = """
        <div class="bibsword_submit_step_details_field">
            <div class="bibsword_submit_step_details_label">
                <label>%(label)s</label>
            </div>
        """ % {
            'label': _('Additional report numbers:'),
        }

        additional_rn_text += """
        <div id="bibsword_submit_step_4_additional_rn_sortable">
        """

        for additional_rn in metadata['additional_rn']:

            additional_rn_text += TemplateSwordClient._submit_step_4_additional_rn_input_block(
                name='additional_rn',
                value=additional_rn and escape(additional_rn, True) or '',
                size='25',
                placeholder=_('Report number...'),
                sortable_label=_("&#8691;"),
                remove_class='bibsword_submit_step_4_additional_rn_remove negative',
                remove_label=_("&#10008;")
            )

        additional_rn_text += """
        </div>
        """

        additional_rn_text += """
        <div>
            <div class="bibsword_submit_step_details_input display_inline_block">
                <button class="%(insert_class)s"><strong>%(insert_label)s</strong></button>
                <label>%(label)s</label>
            </div>
        </div>
        """ % {
            'insert_class': 'bibsword_submit_step_4_additional_rn_insert positive',
            'insert_label': _("&#10010;"),
            'label': _("Insert another one..."),
        }

        additional_rn_text += """
        </div>
        """

        #######################################################################
        # DOI
        #######################################################################
        # if metadata['doi']:

        #     doi_text = """
        #     <input type="hidden" name="%(name)s" value="%(value)s" />
        #     """ % {
        #         'name': 'doi',
        #         'value': escape(metadata['doi'], True),
        #     }

        # else:
        #     doi_text = ''

        #######################################################################
        # Journal information (code, title, page, year)
        #######################################################################
        # journal_info_text = ''

        # for journal_info in zip(('code', 'title', 'page', 'year'), metadata['journal_info']):

        #     if journal_info[1]:
        #         journal_info_text += """
        #         <input type="hidden" name="%(name)s" value="%(value)s" />
        #         """ % {
        #             'name': journal_info[0],
        #             'value': escape(journal_info[1], True),
        #         }

        #######################################################################
        # Files
        #######################################################################
        if files:
            files_text = """
            <div class="bibsword_submit_step_details_field">
                <div class="bibsword_submit_step_details_label">
                    <label>%(label)s</label>
                </div>
            """ % {
                'label': _('Files'),
            }

            for file_key in files.iterkeys():

                files_text += """
                <div class="bibsword_submit_step_details_input">
                    <input type="checkbox" name="%(name)s" value="%(value)s" checked="checked" style="vertical-align: middle;" />
                    <a href="%(url)s" target="_blank">%(label)s</a>
                </div>
                """ % {
                    'name': 'files',
                    'value': str(file_key),
                    'url': escape(files[file_key]['url'], True),
                    'label': escape(files[file_key]['name'], True),
                }

            files_text += """
            </div>
            """

        else:
            files_text = ""

        #######################################################################
        # Complete final text. Reorder if necessary.
        #######################################################################
        text_open = """
        <div id=%(id)s>
        """ % {
            "id": "bibsword_submit_step_4_submission_data",
        }

        text_body = (
            rn_text +
            additional_rn_text +
            title_text +
            author_text +
            abstract_text +
            contributors_text +
            files_text +
            confirmation_text
        )

        text_close = """
        </div>
        """

        return text_open + text_body + text_close

    def submit_step_final_details(
        self,
        ln
    ):
        """
        Return the HTML for the final step details.
        """

        _ = gettext_set_language(ln)

        out = _("The submission has been completed successfully.<br />" +
                "You may check the status of all your submissions " +
                "<a href='/sword_client/?ln={0}'>here</a>.").format(ln)

        return out
