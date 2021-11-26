# -------------------------------------------------------------------------------
# Name:        ENTSO-E codelist parser
# Purpose:     Loads codelist XSD to pandas DataFrame in a triplestore like manner
#
# Author:      kristjan.vilgo
#
# Created:     2021-11-26
# Copyright:   (c) kristjan.vilgo 2020
# Licence:     GPLv2
# -------------------------------------------------------------------------------

import pandas
import uuid
from lxml import etree
import RDF_parser
import json

pandas.set_option('display.max_columns', 20)
pandas.set_option('display.width', 1000)

xml_tree = etree.parse("urn-entsoe-eu-wgedi-codelists.xsd")

nsmap = xml_tree.getroot().nsmap

ID = str(uuid.uuid4())
eic_data_list = [
    (ID, "Type", "Distribution"),
    (ID, "label", "entsoe-codelist.rdf")
]

# Add documentation
for element in xml_tree.find("//{*}documentation").getchildren():
    eic_data_list.append((ID, element.tag, element.text))

# Add all code lists
code_lists = xml_tree.iter("{*}simpleType")

for code_list in code_lists:

    code_list_documentation = code_list.find("{*}annotation/{*}documentation")

    if code_list_documentation is not None:
        #ID = str(uuid.uuid4())
        #ID = code_list_documentation.find("Uid")
        ID = code_list.attrib["name"]
        eic_data_list.extend(
            [
                (ID, "Type", "CodeList"),
                (ID, "name", code_list.attrib["name"])
            ]
        )

        for element in code_list_documentation.getchildren():
            eic_data_list.append((ID, element.tag, element.text))

# Add all codes
codes = xml_tree.findall("//{*}enumeration")

for code in codes:

    code_list_id = code.find("../..").attrib["name"]
    code_value = code.attrib["value"]
    ID = f"{code_list_id}#{code_value}"

    eic_data_list.extend(
        [
            (ID, "Type", "Code"),
            (ID, "Code.CodeList", code_list_id),
            (ID, "code", code_value)
        ]
    )

    code_description = code.find("{*}annotation/{*}documentation/CodeDescription")

    if code_description is not None:
        for element in code_description.getchildren():
            eic_data_list.append((ID, element.tag, element.text))


data = pandas.DataFrame(eic_data_list, columns=["ID", "KEY", "VALUE"])


data["INSTANCE_ID"] = str(uuid.uuid4())

export_format = "code_list.json"
with open(export_format, "r") as conf_file:
    rdf_map = json.load(conf_file)

namespace_map = {
    "cim":"http://iec.ch/TC57/2013/CIM-schema-cim16#",
    "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs":"http://www.w3.org/2000/01/rdf-schema#",
    "dcat":"http://www.w3.org/ns/dcat#",
    None:"urn:entsoe.eu:wgedi:codelists"
}

# Export triplet to CGMES
data.export_to_cimxml(rdf_map=rdf_map,
                      namespace_map=namespace_map,
                      export_undefined=True,
                      export_type="xml_per_instance")

#TODO - Ask for fix: Titre -> Title
#TODO - Ask for fix: Only number in Version
#TODO - Ask for fix: Only number in Release
#TODO - Ask for fix: Some Uid have trailing spaces
#TODO - Swich to scos
#TODO - Maybe concept and export per CodeList?