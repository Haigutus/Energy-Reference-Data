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

data_list = []

message_documentation = xml_tree.find("//{*}documentation")

# Add all code lists
code_lists = xml_tree.iter("{*}simpleType")

for code_list in code_lists:

    code_list_documentation = code_list.find("{*}annotation/{*}documentation")

    if code_list_documentation is not None:

        ISSUED = message_documentation.find("ReleaseDate").text
        VERISON = message_documentation.find("Version").text
        #dcat: version
        #dcterms: issued

        NAME = code_list.attrib["name"]
        UID = code_list_documentation.find("Uid").text
        DEFINITION = code_list_documentation.find("Definition").text

        ID = NAME
        INSTANCE_ID = NAME
        DIST_ID = str(uuid.uuid4())

        data_list.extend(
            [
                # Distribution part, needed for filename
                (DIST_ID, "Type", "Distribution", INSTANCE_ID),
                (DIST_ID, "label", f"entsoe-codelist-{NAME}.rdf", INSTANCE_ID),
                (DIST_ID, "issued", ISSUED, INSTANCE_ID),
                (DIST_ID, "version", VERISON, INSTANCE_ID),

                # Concept scheme definition
                (ID, "Type", "ConceptScheme", INSTANCE_ID),
                (ID, "label", NAME, INSTANCE_ID),
                (ID, "prefLabel", NAME, INSTANCE_ID),
                (ID, "identifier", UID, INSTANCE_ID),
                (ID, "definition", DEFINITION, INSTANCE_ID)
                # TODO split name to words

            ]
        )

        # Add documentation
        for element in message_documentation.getchildren():
            data_list.append((DIST_ID, element.tag, element.text, INSTANCE_ID))

        for element in code_list_documentation.getchildren():
            data_list.append((ID, element.tag, element.text, INSTANCE_ID))

# Add all codes
codes = xml_tree.findall("//{*}enumeration")

for code in codes:

    ConceptScheme_ID = code.find("../..").attrib["name"]
    INSTANCE_ID = ConceptScheme_ID
    code_value = code.attrib["value"]
    ID = f"{ConceptScheme_ID}/{code_value}"

    data_list.extend(
        [
            (ID, "Type", "Concept", INSTANCE_ID),
            (ID, "inScheme", ConceptScheme_ID, INSTANCE_ID),
            (ID, "topConceptOf", ConceptScheme_ID, INSTANCE_ID),
            (ID, "enumeration", code_value, INSTANCE_ID),
            (ID, "identifier", code_value, INSTANCE_ID)
        ]
    )

    code_description = code.find("{*}annotation/{*}documentation/CodeDescription")

    if code_description is not None:

        TITLE = code_description.find("Title").text
        DEFINITION = code_description.find("Definition").text

        data_list.extend(
            [
                (ID, "label", TITLE, INSTANCE_ID),
                (ID, "prefLabel", TITLE, INSTANCE_ID),
                (ID, "definition", DEFINITION, INSTANCE_ID)
            ]
        )

        for element in code_description.getchildren():
            data_list.append((ID, element.tag, element.text))

# Convert to dataframe
data = pandas.DataFrame(data_list, columns=["ID", "KEY", "VALUE", "INSTANCE_ID"])




export_format = "code_list.json"
with open(export_format, "r") as conf_file:
    rdf_map = json.load(conf_file)

namespace_map = {
    "cim": "http://iec.ch/TC57/2013/CIM-schema-cim16#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "dcat": "http://www.w3.org/ns/dcat#",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "ecl": "urn:entsoe.eu:wgedi:codelists",
    "xs": "http://www.w3.org/2001/XMLSchema"
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