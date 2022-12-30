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
from datetime import datetime
from lxml import etree
import RDF_parser
import json

pandas.set_option('display.max_columns', 20)
pandas.set_option('display.width', 1000)


def get_metadata_from_xml(xml, include_namespace=False, include_root=False):
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

    if include_root:
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


def get_allocated_eic_triplet(allocated_eic_url="https://www.entsoe.eu/fileadmin/user_upload/edi/library/eic/allocated-eic-codes.xml"):
    allocated_eic = requests.get(allocated_eic_url)

    xml_tree = etree.fromstring(allocated_eic.content)

    ID = "f4c70c71-77e2-410e-9903-cbd85305cdc4"
    VERSION = "1"
    NAME = "EIC"
    DEFINITION = "Energy Identification Codes"
    ISSUED = datetime.utcnow().isoformat()
    DIST_ID = str(uuid.uuid4())

    eic_data_list = [
        (DIST_ID, "Type", "Distribution"),
        (DIST_ID, "label", "../GeneratedData/allocated-eic.rdf"),


        (NAME, "Type", "ConceptScheme"),
        (NAME, "type", "http://www.w3.org/ns/dcat#Dataset"),
        (NAME, "prefLabel", "Energy Identification Codes"),
        # (NAME, "issued", ISSUED, INSTANCE_ID),
        # (NAME, "modified", ISSUED),
        # (NAME, "version", VERSION),
        (NAME, "prefLabel", NAME),
        (NAME, "identifier", ID),
        (NAME, "keyword", "EIC"),
        (NAME, "definition", DEFINITION)
    ]


    for key, value in get_metadata_from_xml(xml_tree).items():
        eic_data_list.append((NAME, key, value))

    EICs = xml_tree.iter("{*}EICCode_MarketDocument")

    for EIC in EICs:
        ID = f"{NAME}/{EIC[0].text}"

        elements = [{"element": EIC}]
        # eic_data_list.append((ID, "Type", EIC.tag.split('}')[1]))
        eic_data_list.extend([
            (ID, "Type", "Concept"),
            (ID, "inScheme", NAME),
            (ID, "topConceptOf", NAME)
        ])

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


def rename_and_append_key(data, original_key, new_key):
    description = pandas.DataFrame(data.query(f"KEY == '{original_key}'"))
    description["KEY"] = new_key
    data = data.append(description, ignore_index=True)
    return data


# Get published EIC
data = get_allocated_eic_triplet()

# Add header files
data = rename_and_append_key(data, "revisionNumber", "version")
data = rename_and_append_key(data, "eic:createdDateTime", "modified")
data = rename_and_append_key(data, "EICCode_MarketDocument.display_Names.name", "prefLabel")

# Add fields for SKOS
data = rename_and_append_key(data, "EICCode_MarketDocument.long_Names.name", "altLabel")
data = rename_and_append_key(data, "EICCode_MarketDocument.lastRequest_DateAndOrTime.date", "start.use")
data = rename_and_append_key(data, "EICCode_MarketDocument.display_Names.name", "prefLabel")
data = rename_and_append_key(data, "EICCode_MarketDocument.description", "definition")

# Add fields for EIC
data = rename_and_append_key(data, "EICCode_MarketDocument.mRID", "IdentifiedObject.mRID")
data = rename_and_append_key(data, "EICCode_MarketDocument.long_Names.name", "IdentifiedObject.name")
data = rename_and_append_key(data, "EICCode_MarketDocument.display_Names.name", "Names.name")
data = rename_and_append_key(data, "EICCode_MarketParticipant.ACERCode_Name.name", "Names.name")
data = rename_and_append_key(data, "EICCode_MarketParticipant.VATCode_Name.name", "Names.name")
data = rename_and_append_key(data, "EICCode_MarketDocument.description", "IdentifiedObject.description")
data = rename_and_append_key(data, "EICCode_MarketDocument.docStatus.value", "Document.docStatus")
data = rename_and_append_key(data, "EICCode_MarketDocument.attributeInstanceComponent.attribute", "AttributeInstanceComponent.attribute")
data = rename_and_append_key(data, "EICCode_MarketDocument.lastRequest_DateAndOrTime.date", "DateAndOrTime.date")
data = rename_and_append_key(data, "EICCode_MarketDocument.Function_Names.name", "DateAndOrTime.date")

# Add functions
for group_name, group_data in data.query("KEY == 'EICCode_MarketDocument.Function_Names.name'").groupby("VALUE"):
    # Clean name for ID use
    group_id = f"EIC/Function/{group_name.title().replace(' ', '')}"

    data = data.append([
        {"ID": group_id, "KEY": "Type", "VALUE": "Collection"},
        {"ID": group_id, "KEY": "prefLabel", "VALUE": group_name}
    ], ignore_index=True)

    # Transform data
    group_data["VALUE"] = group_data["ID"]
    group_data["ID"] = group_id
    group_data["KEY"] = "member"  # skos:member

    data = pandas.concat([data, group_data], ignore_index=True)

# TODO - Add EIC object types, by creating column with 3-rd letter of EIC and then group by, as above

object_type_names = {
    'X': {'name': 'Party', 'description': r''},
    'Y': {'name': 'Area', 'description': r''},
    'Z': {'name': 'Measurement point', 'description': r''},
    'W': {'name': 'Resource object', 'description': r''},
    'T': {'name': 'Tie-line', 'description': r''},
    'V': {'name': 'Location', 'description': r''},
    'A': {'name': 'Substations', 'description': r''}}

object_types = pandas.DataFrame(data.query("KEY == 'Type' and VALUE == 'Concept'"))
object_types["EIC_Type"] = object_types.ID.str[6:7]  # 3. letter defines EIC type

for group_code, group_data in object_types.groupby("EIC_Type"):
    # Clean name for ID use
    group_name = object_type_names[str(group_code)]['name']
    group_id = f"EIC/ObjectType/{group_name.title().replace(' ', '')}"

    data = data.append([
        {"ID": group_id, "KEY": "Type", "VALUE": "Collection"},
        {"ID": group_id, "KEY": "label", "VALUE": group_name}
    ], ignore_index=True)

    # Transform data
    group_data["VALUE"] = group_data["ID"]
    group_data["ID"] = group_id
    group_data["KEY"] = "member"  # skos:member

    data = pandas.concat([data, group_data[["ID", "KEY", "VALUE"]]], ignore_index=True)



# Start Export
# Add graph ID (expected by export function as multiple graphs could be included)
data["INSTANCE_ID"] = str(uuid.uuid4())


rdf_map = RDF_parser.load_export_conf(["conf_skos.json",
                                       "conf_dcat.json",
                                       "conf_eic.json",
                                       "conf_rdf_rdfs.json"])

namespace_map = {
    "cim": "http://iec.ch/TC57/2013/CIM-schema-cim16#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "dcat": "http://www.w3.org/ns/dcat#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "at": "http://publications.europa.eu/ontology/authority/",
    "eic": "urn:iec62325.351:tc57wg16:451-n:eicdocument:1:0"
}

# Export triplet to CGMES
data.export_to_cimxml(rdf_map=rdf_map,
                      namespace_map=namespace_map,
                      default_namespace="urn:iec62325.351:tc57wg16:451-n:eicdocument:1:0",
                      export_undefined=True,
                      export_type="xml_per_instance"
                      )
