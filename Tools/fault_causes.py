# -------------------------------------------------------------------------------
# Name:        Fault Types
# Purpose:     Converts Fault Types from CIM to SKOS
#
# Author:      kristjan.vilgo
#
# Created:     2022-12-09
# Copyright:   (c) kristjan.vilgo 2022
# Licence:     GPLv2
# -------------------------------------------------------------------------------

import pandas
import RDF_parser
import json
import uuid
from datetime import datetime



ID = "f4c70c71-77e2-410e-9903-cbd85305cdc4"
VERSION = "1"
NAME = "FaultCauseType"
DEFINITION = "ENTSO-E Fault Cause Reference model"
ISSUED = datetime.utcnow().isoformat()
DIST_ID = str(uuid.uuid4())


data = pandas.read_RDF(["PRA_faultCauseTypes_RD.xml"])
data = data.merge(data.query("VALUE == 'FaultCauseType' and KEY == 'Type'")["ID"])

INSTANCE_ID = data.INSTANCE_ID.iloc[0]


data["ID"] = f"{NAME}/" + data["ID"]
data = RDF_parser.rename_and_append_key(data, "Type", "type", original_value=NAME, new_value=f"http://iec.ch/TC57/CIM100#{NAME}")


# Distribution part, needed for filename
header_list = [
                (DIST_ID, "Type", "Distribution", INSTANCE_ID),
                (DIST_ID, "label", f"../GeneratedData/{NAME}.rdf", INSTANCE_ID),
                #(DIST_ID, "issued", ISSUED, INSTANCE_ID),
                (DIST_ID, "modified", ISSUED, INSTANCE_ID),
                (DIST_ID, "version", VERSION, INSTANCE_ID),

                # Concept scheme definition
                (NAME, "Type", "ConceptScheme", INSTANCE_ID),
                (NAME, "type", "http://www.w3.org/ns/dcat#Dataset", INSTANCE_ID),
                #(NAME, "issued", ISSUED, INSTANCE_ID),
                (NAME, "modified", ISSUED, INSTANCE_ID),
                (NAME, "version", VERSION, INSTANCE_ID),
                #(NAME, "label", NAME, INSTANCE_ID),
                (NAME, "prefLabel", NAME, INSTANCE_ID),
                (NAME, "identifier", ID, INSTANCE_ID),
                (NAME, "keyword", "RD", INSTANCE_ID),
                (NAME, "definition", DEFINITION, INSTANCE_ID)
                ]

data = pandas.concat([pandas.DataFrame(header_list, columns=["ID", "KEY", "VALUE", "INSTANCE_ID"]), data])


# Bring some original values under new keys to data
data = RDF_parser.rename_and_append_key(data, "IdentifiedObject.name", "prefLabel")
data = RDF_parser.rename_and_append_key(data, "IdentifiedObject.description", "definition")
data = RDF_parser.rename_and_append_key(data, "IdentifiedObject.mRID", "identifier")

# Add urn:uuid to identifier
data.update("urn:uuid:" + data.query("KEY == 'identifier'").VALUE)

data = RDF_parser.rename_and_append_key(data, "type", "Type", original_value=f"http://iec.ch/TC57/CIM100#{NAME}", new_value="Concept")

data = RDF_parser.add_key_and_value(data, type="Concept", key="inScheme", value=NAME)
data = RDF_parser.add_key_and_value(data, type="Concept", key="topConceptOf", value=NAME)


rdf_map = RDF_parser.load_export_conf(["conf_skos.json",
                                       "conf_dcat.json",
                                       "conf_cim100.json",
                                       "conf_eumd.json",
                                       "conf_rdf_rdfs.json"])

namespace_map = {
    "cim": "http://iec.ch/TC57/CIM100#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "dcat": "http://www.w3.org/ns/dcat#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "at": "http://publications.europa.eu/ontology/authority/",
    "dcterms": "http://purl.org/dc/terms/",
    "eumd": "http://entsoe.eu/ns/Metadata-European#"
}

# Export triplet to CGMES
data.export_to_cimxml(rdf_map=rdf_map,
                      namespace_map=namespace_map,
                      export_undefined=False,
                      export_type="xml_per_instance"
                      )