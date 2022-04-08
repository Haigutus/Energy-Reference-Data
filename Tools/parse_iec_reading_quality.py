import xmltodict
import uuid
import json
import pandas
import RDF_parser

reading_quality_type = {
    1: {"name": "ReadingQualityType.systemId",
        "values": {
            0: "Not Applicable",
            1: "End Device",
            2: "Metering system (data collection) network",
            3: "Meter Data Management System",
            4: "Other system (not listed)",
            5: "Externally specified (see accompany data)"
        }
        },
    2: {"name": "ReadingQualityType.category",
        "values": {
            0: "Valid",
            1: "Diagnostics related",
            2: "Power quality related issues at the data collection point",
            3: "Tamper / Revenue Protection related",
            4: "Data collection related",
            5: "Failed reasonability testing",
            6: "Failed validation testing",
            7: "Edited",
            8: "Estimated",
            10: "Questionable",
            11: "Derived",
            12: "Projected"
        }
        },
    3: {"name": "ReadingQualityType.subCategory",
        "values": {
            0: {
                0: "Data Valid",
                1: "Validated",
                },
            2: {
                32: "Power Fail",
                },
            4: {
                9: "Clock Changed",
                131: "Manual Read",
                },
            5: {
                259: "Known Missing Read",
            },
            6: {
                0: "Failed validation - Generic",
            },
            7: {
                0: "Manually Edited - Generic",
            },
            8: {
                0: "Estimated - Generic",
            },
            11: {
                0: "Derived - Deterministic",
            }
        }
        },

}

reading_quality = [
 {'mRID': '2.5.259',    'description': 'Not Acquired'},
 {'mRID': '1.4.9',      'description': 'Time Shift'},
 {'mRID': '1.2.32',     'description': 'Power Down'},
 {'mRID': '1.4.131',    'description': 'Value Acquired By HHT'},
 {'mRID': '2.8.0',      'description': 'Estimated Value'},
 {'mRID': '2.7.0',      'description': 'Norm Value Changed By User'},
 {'mRID': '2.6.0',      'description': 'Invalid Value'},
 {'mRID': '2.11.0',     'description': 'Aggregation Incomplete'},
 {'mRID': '1.0.0',      'description': 'Status OK (no status)'}
]


def parse_reading_quality_type_to_tree(type_string="1.0.0", description=None):
    coded_values = type_string.split(".")
    parsed = {"@mRID": type_string}
    for position in reading_quality_type.keys():

        if position == 3:
            parsed[reading_quality_type[position]["name"]] = reading_quality_type[position]["values"].get(int(coded_values[position - 2])).get(int(coded_values[position - 1]))
        else:
            parsed[reading_quality_type[position]["name"]] = reading_quality_type[position]["values"].get(int(coded_values[position - 1]))

    if description:
        parsed["description"] = description

    #print(xmltodict.unparse({"readingQualityType": parsed}, pretty=True))
    return parsed


xml = xmltodict.unparse({"ReadingQualityTypes": {"@xmlns": "http://iec.ch/TC57/2011/MeterReadings#",
                                                 "ReadingQualityType":[parse_reading_quality_type_to_tree(reading["mRID"], reading["description"]) for reading in reading_quality]}}, pretty=True)
print(xml)

with open("../GeneratedData/cim_MeterReadings_ReadingQualityTypes.xml", "w") as file_object:
    file_object.write(xml)

data_list = []

ISSUED = "2022-02-18" #TODO
VERSION = "1"

NAME = "MeterReadingsQualityTypes"
UID = '6074aa6b-de29-41bc-a4b5-b2bedbeaeffd'
DEFINITION = "Meter Reading Quality Types"

ID = NAME
INSTANCE_ID = NAME
DIST_ID = str(uuid.uuid4())

data_list.extend(
            [
                # Distribution part, needed for filename
                (DIST_ID, "Type", "Distribution", INSTANCE_ID),
                (DIST_ID, "label", "../GeneratedData/cim_MeterReadings_ReadingQualityTypes.rdf", INSTANCE_ID),
                #(DIST_ID, "issued", ISSUED, INSTANCE_ID),
                (DIST_ID, "modified", ISSUED, INSTANCE_ID),
                (DIST_ID, "version", VERSION, INSTANCE_ID),

                # Concept scheme definition
                (ID, "Type", "ConceptScheme", INSTANCE_ID),
                #(ID, "issued", ISSUED, INSTANCE_ID),
                (ID, "modified", ISSUED, INSTANCE_ID),
                (ID, "version", VERSION, INSTANCE_ID),
                #(ID, "label", NAME, INSTANCE_ID),
                (ID, "prefLabel", NAME, INSTANCE_ID),
                (ID, "identifier", UID, INSTANCE_ID),
                (ID, "definition", DEFINITION, INSTANCE_ID)

            ]
        )

ConceptScheme_ID = ID
for reading in reading_quality:

    ID = f"{ConceptScheme_ID}/{reading['mRID']}"
    INSTANCE_ID = ConceptScheme_ID

    data_list.extend(
        [
            (ID, "Type", "Concept", INSTANCE_ID),
            (ID, "inScheme", ConceptScheme_ID, INSTANCE_ID),
            (ID, "topConceptOf", ConceptScheme_ID, INSTANCE_ID),
            # (ID, "enumeration", code_value, INSTANCE_ID),
            (ID, "identifier", reading['mRID'], INSTANCE_ID),
            (ID, "type", "cim:ReadingQualityType", INSTANCE_ID),
        ]
    )

    if reading['description'] is not None:
        data_list.extend([
            (ID, "definition", reading['description'], INSTANCE_ID),
            (ID, "IdentifiedObject.name", reading['description'], INSTANCE_ID)
        ])

    for key, value in parse_reading_quality_type_to_tree(type_string=reading['mRID']).items():
        key = key.replace("@", "IdentifiedObject.")
        data_list.append((ID, key, value, INSTANCE_ID))


data = pandas.DataFrame(data_list, columns=["ID", "KEY", "VALUE", "INSTANCE_ID"])


#export_format = "conf_dcat_cim_metering.json"
#with open(export_format, "r") as conf_file:
#    rdf_map = json.load(conf_file)

rdf_map = RDF_parser.load_export_conf(["conf_skos.json",
                                       "conf_dcat.json",
                                       "conf_cim16.json",
                                       "conf_rdf_rdfs.json"])

namespace_map = {
    "cim":      "http://iec.ch/TC57/2013/CIM-schema-cim16#",
    "rdf":      "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xml":      "http://www.w3.org/XML/1998/namespace",
    "rdfs":     "http://www.w3.org/2000/01/rdf-schema#",
    "dcat":     "http://www.w3.org/ns/dcat#",
    "dc":       "http://purl.org/dc/elements/1.1/",
    "dcterms":  "http://purl.org/dc/terms/",
    "skos":     "http://www.w3.org/2004/02/skos/core#",
}

# Export triplet to CGMES
data.export_to_cimxml(rdf_map=rdf_map,
                      namespace_map=namespace_map,
                      export_undefined=False,
                      export_type="xml_per_instance")
