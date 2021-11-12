# -------------------------------------------------------------------------------
# Name:        ENTSO-E EIC registry parser
# Purpose:     Loads EIC registry XML from web to pandas DataFrame in a triplestore like manner
#
# Author:      kristjan.vilgo
#
# Created:     2020-01-31
# Copyright:   (c) kristjan.vilgo 2020
# Licence:     GPLv2
# -------------------------------------------------------------------------------

import requests
import pandas
from lxml import etree

pandas.set_option('display.max_columns', 20)
pandas.set_option('display.width', 1000)


def get_allocated_eic_triplet():
    allocated_eic_url = "https://www.entsoe.eu/fileadmin/user_upload/edi/library/eic/allocated-eic-codes.xml"
    allocated_eic = requests.get(allocated_eic_url)

    xml_tree = etree.fromstring(allocated_eic.content)

    eic_data_list = []

    EICs = xml_tree.iter("{*}EICCode_MarketDocument")

    for EIC in EICs:
        ID = EIC[0].text

        elements = [{"element": EIC}]
        for element in elements:

            for field in element["element"].getchildren():

                parent_name = element.get("parent_name")
                element_name = element['element'].tag.split('}')[1]
                field_name = field.tag.split('}')[1]

                if not parent_name:
                    parent_name = element_name
                else:
                    parent_name = f"{parent_name}.{element_name}"

                name = f"{parent_name}.{field_name}"

                if len(field.getchildren()) == 0:
                    eic_data_list.append({"ID": ID, "KEY": name, "VALUE": field.text})
                else:
                    elements.append({"parent_name": parent_name, "element": field})

    return pandas.DataFrame(eic_data_list)
