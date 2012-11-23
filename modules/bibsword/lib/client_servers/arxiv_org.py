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
arXiv.org SWORD server.
"""

from cgi import escape
from lxml import etree

from invenio.bibsword_client_server import SwordClientServer

__revision__ = "$Id$"

_LOCAL_SETTINGS = {
    'realm': 'SWORD at arXiv',
    'uri': 'https://arxiv.org/sword-app/',
    'service_document_url': 'https://arxiv.org/sword-app/servicedocument',
}

CFG_ARXIV_ORG_VERBOSE = True
CFG_ARXIV_ORG_DRY_RUN = True


class ArxivOrg(SwordClientServer):
    """
    The arXiv.org SWORD server.
    """

    def __init__(self, settings):
        """
        Adds the arXiv.org-specific settings before running
        SwordClientServer's constructor.
        """

        settings.update(_LOCAL_SETTINGS)
        SwordClientServer.__init__(self, settings)

    def _parse_service_document(
        self,
        service_document_raw
    ):
        """
        Parses the raw service document (XML) into a python dictionary.
        """

        service_document_parsed = {}

        try:
            service_document_etree = etree.XML(service_document_raw)
        except etree.XMLSyntaxError:
            return service_document_parsed

        # Get the version
        version = service_document_etree.itertext(
            tag="{http://purl.org/net/sword/}version"
        ).next().strip()
        service_document_parsed["version"] = version

        # Get the maximum upload size
        maximum_file_size_in_kilobytes = service_document_etree.itertext(
            tag="{http://purl.org/net/sword/}maxUploadSize"
        ).next().strip()
        maximum_file_size_in_bytes = int(maximum_file_size_in_kilobytes)*1024
        service_document_parsed["maxUploadSize"] = maximum_file_size_in_bytes

        # Get the verbose
        verbose = service_document_etree.itertext(
            tag="{http://purl.org/net/sword/}verbose"
        ).next().strip()
        service_document_parsed["verbose"] = verbose

        # Get the noOp
        noOp = service_document_etree.itertext(
            tag="{http://purl.org/net/sword/}noOp"
        ).next().strip()
        service_document_parsed["noOp"] = noOp

        # Get the collections
        service_document_parsed["collections"] = {}
        collections = service_document_etree.iterdescendants(
            tag='{http://www.w3.org/2007/app}collection'
        )
        for collection in collections:
            collection_url = collection.get('href')
            service_document_parsed["collections"][collection_url] = {}

            # Get the collection title
            collection_title = collection.itertext(
                tag='{http://www.w3.org/2005/Atom}title'
            ).next().strip()
            service_document_parsed[
                "collections"
            ][
                collection_url
            ][
                "title"
            ] = collection_title

            # Get the collection accepted file types
            service_document_parsed[
                "collections"
            ][
                collection_url
            ][
                "accepts"
            ] = []
            collection_accepts = collection.iterdescendants(
                tag='{http://www.w3.org/2007/app}accept'
            )
            for collection_accept in collection_accepts:
                collection_accept_extensions = \
                    SwordClientServer._get_extension_for_file_type(
                        collection_accept.text.strip()
                    )
                service_document_parsed[
                    "collections"
                ][
                    collection_url
                ][
                    "accepts"
                ].extend(collection_accept_extensions)

            service_document_parsed[
                "collections"
            ][
                collection_url
            ][
                "accepts"
            ] = tuple(
                set(
                    service_document_parsed[
                        "collections"
                    ][
                        collection_url
                    ][
                        "accepts"
                    ]
                )
            )

            # Get the collection policy
            collection_policy = collection.itertext(
                tag="{http://purl.org/net/sword/}collectionPolicy"
            ).next().strip()
            service_document_parsed[
                "collections"
            ][
                collection_url
            ][
                "policy"
            ] = collection_policy

            # Get the collection abstract
            collection_abstract = collection.itertext(
                tag="{http://purl.org/dc/terms/}abstract"
            ).next().strip()
            service_document_parsed[
                "collections"
            ][
                collection_url
            ][
                "abstract"
            ] = collection_abstract

            # Get the collection mediation
            collection_mediation = collection.itertext(
                tag="{http://purl.org/net/sword/}mediation"
            ).next().strip()
            service_document_parsed[
                "collections"
            ][
                collection_url
            ][
                "mediation"
            ] = collection_mediation

            # Get the collection treatment
            collection_treatment = collection.itertext(
                tag="{http://purl.org/net/sword/}treatment"
            ).next().strip()
            service_document_parsed[
                "collections"
            ][
                collection_url
            ][
                "treatment"
            ] = collection_treatment

            # Get the collection categories
            service_document_parsed[
                "collections"
            ][
                collection_url
            ][
                "categories"
            ] = {}
            collection_categories = collection.iterdescendants(
                tag='{http://www.w3.org/2005/Atom}category'
            )
            for collection_category in collection_categories:
                collection_category_term = collection_category.get(
                    'term'
                ).strip()
                collection_category_scheme = collection_category.get(
                    'scheme'
                ).strip()
                collection_category_label = collection_category.get(
                    'label'
                ).strip()
                service_document_parsed[
                    "collections"
                ][
                    collection_url
                ][
                    "categories"
                ][
                    collection_category_term
                ] = {
                    "label": collection_category_label,
                    "scheme": collection_category_scheme,
                }

            # Get the collection primary categories
            service_document_parsed[
                "collections"
            ][
                collection_url
            ][
                "primary_categories"
            ] = {}
            collection_primary_categories = collection.iterdescendants(
                tag='{http://arxiv.org/schemas/atom/}primary_category'
            )
            for collection_primary_category in collection_primary_categories:
                collection_primary_category_term = \
                    collection_primary_category.get(
                        'term'
                    ).strip()
                collection_primary_category_scheme = \
                    collection_primary_category.get(
                        'scheme'
                    ).strip()
                collection_primary_category_label = \
                    collection_primary_category.get(
                        'label'
                    ).strip()
                service_document_parsed[
                    "collections"
                ][
                    collection_url
                ][
                    "primary_categories"
                ][
                    collection_primary_category_term
                ] = {
                    "label": collection_primary_category_label,
                    "scheme": collection_primary_category_scheme,
                }

        return service_document_parsed

    def get_collections(self):
        """
        """
        return self.service_document_parsed.get("collections")

    def get_categories(self, collection_url):
        """
        """
        return {
            "mandatory": self.service_document_parsed.get(
                "collections",
            ).get(
                collection_url,
                {}
            ).get(
                "primary_categories"
            ),
            "optional": self.service_document_parsed.get(
                "collections"
            ).get(
                collection_url,
                {}
            ).get(
                "categories"
            ),
        }

    def get_accepted_file_types(self, collection_url):
        """
        """
        return self.service_document_parsed.get(
            "collections"
        ).get(
            collection_url,
            {}
        ).get(
            "accepts"
        )

    def get_maximum_file_size(self):
        """
        Return size in bytes.
        """
        return self.service_document_parsed.get("maxUploadSize")

    def _prepare_media(self, media):
        """
        TODO: this function should decide if and how to consolidate the files
              depending on * the maximum file size
                       and * the accepted packaging options
        """

        return media

    def _prepare_media_headers(self, file_info, metadata):
        """
        """

        headers = SwordClientServer._prepare_media_headers(
            self,
            file_info,
            metadata
        )

        headers['Host'] = 'arxiv.org'

        if file_info['checksum']:
            headers['Content-MD5'] = file_info['checksum']

        # NOTE: It looks like media deposit only accepts the "X-On-Behalf-Of"
        #       header when both the author_name and author_email are present
        #       in the given format:
        #       "A. Scientist" <ascientist@institution.edu>.
        (author_name, author_email, dummy) = metadata.get(
            'author',
            (None, None, None)
        )
        if author_email:
            if author_name and self._is_ascii(author_name):
                headers['X-On-Behalf-Of'] = "\"%s\" <%s>" % (
                    author_name,
                    author_email
                )
            else:
                headers['X-On-Behalf-Of'] = "%s" % (author_email,)

        if CFG_ARXIV_ORG_VERBOSE:
            headers['X-Verbose'] = 'True'

        if CFG_ARXIV_ORG_DRY_RUN:
            headers['X-No-Op'] = 'True'

        return headers

    def _prepare_media_response(self, response):
        """
        """

        # NOTE: Could we get the media_link from the response headers?
        # media_link = response.headers.get('Location')

        try:
            response_xml = response.read()
            response.close()
            response_etree = etree.XML(response_xml)
            response_links = response_etree.findall(
                '{http://www.w3.org/2005/Atom}link'
            )
            for response_link in response_links:
                if response_link.attrib.get('rel') == 'edit-media':
                    media_link = response_link.attrib.get('href')
                    break
        except:
            media_link = None

        return media_link

    def _prepare_media_response_error(self, error):
        """
        """

        try:
            error_xml = error.read()
            error.close()
            error_etree = etree.XML(error_xml)
            error_msg = error_etree.findtext(
                '{http://www.w3.org/2005/Atom}summary'
            )
            if not error_msg:
                raise Exception
            return error_msg
        except:
            return "HTTP Error %s: %s" (error.code, error.msg)

    def _prepare_metadata(self, metadata, media_response):
        """
        """

        # Namespaces
        # TODO: de-hardcode the namespaces
        atom_ns = 'http://www.w3.org/2005/Atom'
        atom_nsmap = {None: atom_ns}
        arxiv_ns = 'http://arxiv.org/schemas/atom/'
        arxiv_nsmap = {'arxiv': arxiv_ns}

        # The root element of the atom entry
        entry_element = etree.Element('entry', nsmap=atom_nsmap)

        # The title element
        # (SWORD/APP - arXiv.org mandatory)
        # TODO: This is mandatory, we shouldn't check
        #       at this point if it's there or not.
        title = metadata['title']
        if title:
            title_element = etree.Element('title')
            title_element.text = escape(title, True).decode('utf-8')
            entry_element.append(title_element)

        # The id element
        # (SWORD/APP mandatory)
        # TODO: This is mandatory, we shouldn't check
        #       at this point if it's there or not.
        recid = metadata['recid']
        if recid:
            id_element = etree.Element('id')
            id_element.text = str(recid)
            entry_element.append(id_element)

        # The updated element
        # (SWORD/APP mandatory)
        # TODO: This is mandatory, we shouldn't check
        #       at this point if it's there or not.
        modification_date = metadata['modification_date']
        if modification_date:
            updated_element = etree.Element('updated')
            updated_element.text = modification_date
            entry_element.append(updated_element)

        # The author element
        # (arXiv.org mandatory)
        # NOTE: The author element is used for the authenticated user,
        #       i.e. the person who initiates the submission.
        #       The repeatable contributor element is used to specify the
        #       individual authors of the material being deposited to arXiv.
        #       At least one /contributor/email node must be present in order
        #       to inform arXiv of the email address of the primary contact
        #       author. If multiple /contributor/email nodes are found,
        #       the first will be used. Optionally the primary contact author's
        #       (name and) email address can also be specified in the
        #       X-On-Behalf-Of HTTP header extension, e.g.:
        #       X-On-Behalf-Of: "A. Scientist" <ascientist@institution.edu>
        #       (http://arxiv.org/help/submit_sword#Ingestion)
        author_element = etree.Element('author')
        author_name_element = etree.Element('name')
        author_name_element.text = escape(self.username, True).decode('utf-8')
        author_element.append(author_name_element)
        author_email_element = etree.Element('email')
        author_email_element.text = escape(self.email, True).decode('utf-8')
        author_element.append(author_email_element)
        entry_element.append(author_element)

        # The contributors element(s)
        # (arXiv.org mandatory)
        # TODO: This is mandatory, we shouldn't check
        #       at this point if it's there or not.
        # NOTE: At least one /contributor/email node must be present in order
        #       to inform arXiv of the email address of the primary contact
        #       author.
        (author_name, author_email, author_affiliation) = metadata['author']
        if author_name or author_email or author_affiliation:
            contributor_element = etree.Element('contributor')
            if author_name:
                contributor_name_element = etree.Element('name')
                contributor_name_element.text = escape(
                    author_name,
                    True
                ).decode('utf-8')
                contributor_element.append(contributor_name_element)
            if author_email:
                contributor_email_element = etree.Element('email')
                contributor_email_element.text = escape(
                    author_email,
                    True
                ).decode('utf-8')
                contributor_element.append(contributor_email_element)
            # TODO: Remove this hack with something more elegant.
            else:
                contributor_email_element = etree.Element('email')
                contributor_email_element.text = escape(
                    self.email,
                    True
                ).decode('utf-8')
                contributor_element.append(contributor_email_element)
            if author_affiliation:
                contributor_affiliation_element = etree.Element(
                    '{%s}affiliation' % (arxiv_ns,),
                    nsmap=arxiv_nsmap
                )
                contributor_affiliation_element.text = escape(
                    author_affiliation,
                    True
                ).decode('utf-8')
                contributor_element.append(contributor_affiliation_element)
            entry_element.append(contributor_element)

        contributors = metadata['contributors']
        for (contributor_name,
             contributor_email,
             contributor_affiliation
             ) in contributors:
            contributor_element = etree.Element('contributor')
            if contributor_name:
                contributor_name_element = etree.Element('name')
                contributor_name_element.text = escape(
                    contributor_name,
                    True
                ).decode('utf-8')
                contributor_element.append(contributor_name_element)
            if contributor_email:
                contributor_email_element = etree.Element('email')
                contributor_email_element.text = escape(
                    contributor_email,
                    True
                ).decode('utf-8')
                contributor_element.append(contributor_email_element)
            if contributor_affiliation:
                contributor_affiliation_element = etree.Element(
                    '{%s}affiliation' % (arxiv_ns,),
                    nsmap=arxiv_nsmap
                )
                contributor_affiliation_element.text = escape(
                    contributor_affiliation,
                    True
                ).decode('utf-8')
                contributor_element.append(contributor_affiliation_element)
            entry_element.append(contributor_element)

        # The content element
        # (arXiv.org optional)
        # NOTE: Contains or links to the complete content of the entry.
        #       Content must be provided if there is no alternate link,
        #       and should be provided if there is no summary.
        #       (http://www.atomenabled.org/developers/syndication/#recommendedEntryElements)

        # The summary element
        # (arXiv.org mandatory)
        # TODO: This is mandatory, we shouldn't check
        #       at this point if it's there or not.
        #       The same goes for the minimum length of 20.
        abstract = metadata['abstract']
        if abstract:
            # TODO: Replace this hack with something more elegant.
            if len(abstract) < 20:
                abstract += '.' * (20 - len(abstract))
            summary_element = etree.Element('summary')
            summary_element.text = escape(abstract, True).decode('utf-8')
            entry_element.append(summary_element)

        # The category element(s)
        # (arXiv.org optional)
        optional_categories = metadata['optional_categories']
        for optional_category in optional_categories:
            optional_category_element = etree.Element(
                'category',
                term=optional_category['term'],
                scheme=optional_category['scheme'],
                label=optional_category['label'],
            )
            entry_element.append(optional_category_element)

        # The primary_category element
        # (arXiv.org mandatory)
        mandatory_category = metadata['mandatory_category']
        mandatory_category_element = etree.Element(
            '{%s}primary_category' % (arxiv_ns,), nsmap=arxiv_nsmap,
            term=mandatory_category['term'],
            scheme=mandatory_category['scheme'],
            label=mandatory_category['label'],
        )
        entry_element.append(mandatory_category_element)

        # The report_no element(s)
        # (arXiv.org optional)
        rn = metadata['rn']
        if rn:
            report_no_element = etree.Element(
                '{%s}report_no' % (arxiv_ns,),
                nsmap=arxiv_nsmap
            )
            report_no_element.text = escape(rn, True).decode('utf-8')
            entry_element.append(report_no_element)

        additional_rn = metadata['additional_rn']
        for rn in additional_rn:
            report_no_element = etree.Element(
                '{%s}report_no' % (arxiv_ns,),
                nsmap=arxiv_nsmap
            )
            report_no_element.text = escape(rn, True).decode('utf-8')
            entry_element.append(report_no_element)

        # The doi element
        # (arXiv.org optional)
        doi = metadata['doi']
        if doi:
            doi_element = etree.Element(
                '{%s}doi' % (arxiv_ns,),
                nsmap=arxiv_nsmap
            )
            doi_element.text = escape(doi, True).decode('utf-8')
            entry_element.append(doi_element)

        # The journal_ref element(s)
        # (arXiv.org optional)
        (
            journal_code,
            journal_title,
            journal_page,
            journal_year
        ) = metadata['journal_info']
        if journal_title:
            journal_info = "%s" % (journal_title,)
            if journal_code:
                journal_info += ": %s" % (journal_code,)
            if journal_year:
                journal_info += " (%s)" % (journal_year,)
            if journal_page:
                journal_info += " pp. %s" % (journal_page,)
            journal_ref_element = etree.Element(
                '{%s}journal_ref' % (arxiv_ns,),
                nsmap=arxiv_nsmap
            )
            journal_ref_element.text = escape(
                journal_info, True
            ).decode('utf-8')
            entry_element.append(journal_ref_element)

        # The comment element
        # (arXiv.org optional)
        # NOTE: The <arxiv:comment> element contains the typical author
        #       comments found on most arXiv articles:
        #       "23 pages, 8 figures and 4 tables"
        # TODO: How does this map to metadata['comments']
        #       and metadata['internal_notes']?

        # The link element(s)
        # (arXiv.org mandatory)
        for file_response in media_response.itervalues():
            if not file_response['error']:
                link_element = etree.Element(
                    'link',
                    href=file_response['msg'],
                    type=file_response['mime'],
                    rel='related'
                )
                entry_element.append(link_element)

        prepared_metadata = etree.tostring(
            entry_element,
            xml_declaration=True,
            encoding='utf-8',
            pretty_print=True
        )

        return prepared_metadata

    def _prepare_metadata_headers(self, metadata):
        """
        """

        headers = SwordClientServer._prepare_metadata_headers(
            self,
            metadata
        )

        headers['Host'] = 'arxiv.org'

        # NOTE: It looks like media deposit only accepts the "X-On-Behalf-Of"
        #       header when both the author_name and author_email are present
        #       in this format: "A. Scientist" <ascientist@institution.edu>.
        (
            author_name,
            author_email,
            dummy
        ) = metadata.get('author', (None, None, None))
        if author_email:
            if author_name and self._is_ascii(author_name):
                headers['X-On-Behalf-Of'] = "\"%s\" <%s>" % (
                    author_name,
                    author_email
                )
            else:
                headers['X-On-Behalf-Of'] = "%s" % (author_email,)

        if CFG_ARXIV_ORG_VERBOSE:
            headers['X-Verbose'] = 'True'

        if CFG_ARXIV_ORG_DRY_RUN:
            headers['X-No-Op'] = 'True'

        return headers

    def _prepare_metadata_response(self, response):
        """
        """

        links = {}

        try:
            response_xml = response.read()
            response.close()
            response_etree = etree.XML(response_xml)
            response_links = response_etree.findall(
                '{http://www.w3.org/2005/Atom}link'
            )
            for response_link in response_links:
                if response_link.attrib.get('rel') == 'alternate':
                    links['alternate'] = response_link.attrib.get('href')
                if response_link.attrib.get('rel') == 'edit':
                    links['edit'] = response_link.attrib.get('href')
        except:
            links['alternate'] = None
            links['edit'] = None

        return links

    def _prepare_metadata_response_error(self, error):
        """
        """

        try:
            error_xml = error.read()
            error.close()
            error_etree = etree.XML(error_xml)
            error_msg = error_etree.findtext(
                '{http://www.w3.org/2005/Atom}summary'
            )
            if not error_msg:
                raise Exception
            return error_msg
        except:
            return "HTTP Error %s: %s" (error.code, error.msg)

    def _prepare_response(self, media_response, metadata_response):
        """
        """

        response = {}

        # Update the general response with the metadata response
        response.update(metadata_response)

        # If there were errors with the media,
        # also update the general response with the media response
        if metadata_response['error'] and media_response:
            for file_response in media_response.itervalues():
                if file_response['error']:
                    response['media_response'] = media_response
                    break

        return response

    def _prepare_status_response(self, response):
        """
        """

        status_and_error = {}

        try:
            response_xml = response.read()
            response.close()
            response_etree = etree.XML(response_xml)
            response_status = response_etree.findall('status')
            if response_status:
                status_and_error['status'] = response_status[0].text
                if status_and_error['status'] == "published":
                    response_arxiv_id = response_etree.findall('arxiv_id')
                    if response_arxiv_id:
                        status_and_error[
                            'status'
                        ] = "<a href=\"{0}{1}\">{2}</a>".format(
                            "http://arxiv.org/abs/",
                            response_arxiv_id[0].text,
                            "published"
                        )
            else:
                status_and_error['status'] = None
            response_error = response_etree.findall('error')
            if response_error:
                status_and_error['error'] = response_error[0].text
            else:
                status_and_error['error'] = None
        except:
            status_and_error['status'] = None
            status_and_error['error'] = None

        return status_and_error

    @staticmethod
    def _is_ascii(s):
        """
        """

        try:
            s.decode("ascii")
        except:
            return False
        else:
            return True

# NOTE: in order to edit an existing submission:
#       * First all the media resources should be individually posted
#         or deposited packed together into a zip file.
#       * Then a metadata wrapper is PUT to the link with "rel=/edit/"
#         which was part of the atom entry response to the
#         original wrapper deposit.
#         ...
#         request = urllib2.Request('http://example.org', data='your_put_data')
#         request.get_method = lambda: 'PUT'
#         ...


def arxiv_org(settings):
    """
    Instantiates the remote SWORD server.
    """

    return ArxivOrg(settings)
