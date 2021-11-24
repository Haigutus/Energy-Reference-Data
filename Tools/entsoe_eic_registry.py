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
import uuid
from lxml import etree
import RDF_parser
import json

pandas.set_option('display.max_columns', 20)
pandas.set_option('display.width', 1000)


def get_metadata_from_xml(xml, include_namespace=True):
    """Extract all metadata present in XML root element
    Input -> xml as byte string
    Output -> dictionary with metadata"""

    properties_dict = {}

    # Lets get root element and its namespace

    root_element = xml.tag.split("}")

    # Handle XML-s without namespace
    if len(root_element) == 2:
        namespace, root = root_element
    else:
        root, = root_element
        namespace = ""

    properties_dict["root"] = root

    if include_namespace:
        properties_dict["namespace"] = namespace[1:]

    # Lets get all children of root
    for element in xml.getchildren():

        # If element has children then it is not root meta field
        if len(element.getchildren()) == 0:

            element_data = element.tag.split("}")
            if len(element_data) == 2:
                _, element_name = element_data
            else:
                element_name, = element_data

            # If not, then lets add its name and value to properties
            properties_dict[element_name] = element.text

    return properties_dict



def get_allocated_eic_triplet():
    allocated_eic_url = "https://www.entsoe.eu/fileadmin/user_upload/edi/library/eic/allocated-eic-codes.xml"
    allocated_eic = requests.get(allocated_eic_url)

    xml_tree = etree.fromstring(allocated_eic.content)

    ID = str(uuid.uuid4())
    eic_data_list = [
        (ID, "Type", "Distribution"),
        (ID, "label", "allocated-eic.rdf")
    ]

    for key, value in get_metadata_from_xml(xml_tree).items():
        eic_data_list.append((ID, key, value))

    EICs = xml_tree.iter("{*}EICCode_MarketDocument")

    for EIC in EICs:
        ID = EIC[0].text

        elements = [{"element": EIC}]
        eic_data_list.append((ID, "Type", EIC.tag.split('}')[1]))

        for element in elements:

            for field in element["element"].getchildren():

                element_name = element['element'].tag.split('}')[1]
                parent_name = element.get("parent_name")
                field_name = field.tag.split('}')[1]

                if not parent_name:
                    parent_name = element_name
                else:
                    parent_name = f"{parent_name}.{element_name}"

                name = f"{parent_name}.{field_name}"

                if len(field.getchildren()) == 0:
                    eic_data_list.append((ID, name, field.text))
                else:
                    elements.append({"parent_name": parent_name, "element": field})

    return pandas.DataFrame(eic_data_list, columns=["ID", "KEY", "VALUE"])


data = get_allocated_eic_triplet()
data["INSTANCE_ID"] = str(uuid.uuid4())

export_format = "eic.json"
with open(export_format, "r") as conf_file:
    rdf_map = json.load(conf_file)

namespace_map = {
    "cim":"http://iec.ch/TC57/2013/CIM-schema-cim16#",
    "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs":"http://www.w3.org/2000/01/rdf-schema#",
    "dcat":"http://www.w3.org/ns/dcat#",
    None:"urn:iec62325.351:tc57wg16:451-n:eicdocument:1:0"
}

# Export triplet to CGMES
data.export_to_cimxml(rdf_map=rdf_map,
                      namespace_map=namespace_map,
                      export_undefined=True,
                      export_type="xml_per_instance")