# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-

# Copyright (C) 2011 Houssem Medhioub - Institut Mines-Telecom
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

"""
Created on Jun 21, 2012

@author: Bilel Msekni
@contact: bilel.msekni@telecom-sudparis.eu
@author: Houssem Medhioub
@contact: houssem.medhioub@it-sudparis.eu
@organization: Institut Mines-Telecom - Telecom SudParis
@version: 0.3
@license: LGPL - Lesser General Public License
"""

try:
    import simplejson as json
except ImportError:
    import json
import pyocni.serialization.cnv_toJSON as extractor
from webob import Response

class From_Text_Plain_to_JSON():

    def format_text_plain_categories_to_json(self, var):
        """
        Converts a HTTP text/plain category into a JSON category
        Args:
            @param var: HTTP text/plain category
        """
        res = extractor.extract_categories_from_body(var)

        kind_list = list()
        mix_list = list()
        act_list = list()

        for item in res:

            term,scheme,ht_class,title,rel,location,attributes,actions = extractor.splitter(item)
            if ht_class == "kind":
                kind_list.append(assemble_category(term,scheme,title,rel,location,attributes,actions))
            elif ht_class == "mixin":
                mix_list.append(assemble_category(term,scheme,title,rel,location,attributes,actions))
            elif ht_class == "action":
                act_list.append(assemble_category(term,scheme,title,rel,location,attributes,actions))

        categories = dict()
        if len(kind_list) is not 0:
            categories['kinds'] = kind_list

        if len(mix_list) is not 0:
            categories['mixins'] = mix_list

        if len(act_list) is not 0:
            categories['actions'] = act_list

        return categories

class From_Text_OCCI_to_JSON():

    def format_text_occi_categories_to_json(self, var):
        """
        Converts a HTTP text/plain category into a JSON category
        Args:
            @param var: HTTP text/plain category
        """
        res = extractor.extract_categories_from_headers(var)

        kind_list = list()
        mix_list = list()
        act_list = list()

        for item in res:

            term,scheme,ht_class,title,rel,location,attributes,actions = extractor.splitter(item)
            if ht_class == "kind":
                kind_list.append(assemble_category(term,scheme,title,rel,location,attributes,actions))
            elif ht_class == "mixin":
                mix_list.append(assemble_category(term,scheme,title,rel,location,attributes,actions))
            elif ht_class == "action":
                act_list.append(assemble_category(term,scheme,title,rel,location,attributes,actions))

        categories = dict()
        if len(kind_list) is not 0:
            categories['kinds'] = kind_list

        if len(mix_list) is not 0:
            categories['mixins'] = mix_list

        if len(act_list) is not 0:
            categories['actions'] = act_list

        return categories

def assemble_category(term,scheme,title,rel,location,attributes,actions):
    """
    Creates a JSON category object
    """
    category = dict()
    if term is not None:
        category['term'] = term
    if scheme is not None:
        category['scheme'] = scheme
    if title is not None:
        category['title'] = title
    if rel is not None:
        category['related'] = extractor.create_JSON_format_relateds(rel)
    if attributes is not None:
        category['attributes'] = extractor.create_JSON_format_attributes (attributes)
    if actions is not None:
        category['actions'] = extractor.create_JSON_format_actions(actions)
    if location is not None:
        category['location'] = location

    return category


if __name__ == "__main__":

    cat = "Category : my_stuff;"\
          "scheme=\"http://example.com/occi/my_stuff#\";"\
          "# class=\"mixin\";"\
          "rel=\"http:/example.com/occi/something_else#mixin\";"\
          "title=\"Storage Resource\";"\
          "location=\"/my_stuff/\";"\
          "attributes=\"occi.storage.size{required} occi.storage.state{immutable}\";"\
          "actions=\"http://schemas.ogf.org/occi/infrastructure/storage/action#resize ...\";"\
          "Category : my_stuff;"\
          "scheme=\"http://example.com/occi/my_stuff#\";"\
          "# class=\"mixin\";"\
          "rel=\"http:/example.com/occi/something_else#mixin\";"\
          "title=\"Storage Resource\";"\
          "location=\"/my_stuff/\";"\
          "attributes=\"occi.storage.size{required} occi.storage.state{immutable}\";"\
          "actions=\"http://schemas.ogf.org/occi/infrastructure/storage/action#resize ...\";"\
          "Category : my_stuff;"\
          "scheme=\"http://example.com/occi/my_stuff#\";"\
          "# class=\"mixin\";"\
          "rel=\"http:/example.com/occi/something_else#mixin\";"\
          "title=\"Storage Resource\";"\
          "location=\"/my_stuff/\";"\
          "attributes=\"occi.storage.size{required} occi.storage.state{immutable}\";"\
          "actions=\"http://schemas.ogf.org/occi/infrastructure/storage/action#resize ...\";"

    obj = From_Text_Plain_to_JSON()
    res = obj.format_text_plain_categories_to_json(cat)
    print res