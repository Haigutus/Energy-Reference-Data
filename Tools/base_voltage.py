import uuid
import pandas
from datetime import datetime
import RDF_parser

def rename_and_append_key(data, original_key, new_key, original_value=None, new_value=None):

    if original_value:
        description = pandas.DataFrame(data.query(f"KEY == '{original_key}' and VALUE =='{original_value}'"))
        description["VALUE"] = new_value
    else:
        description = pandas.DataFrame(data.query(f"KEY == '{original_key}'"))

    description["KEY"] = new_key
    data = data.append(description, ignore_index=True)
    return data

def add_key_and_value(data, type, key, value, id=None):

    if id:
        filter = data.query("ID == @id and KEY == 'Type' and VALUE == @type")

    else:
        filter = data.query("KEY == 'Type' and VALUE == @type")

    filter["KEY"] = key
    filter["VALUE"] = value

    data = data.append(filter, ignore_index=True)
    return data


def fix_uuid(uuid_string):

    try:
        return str(uuid.UUID(uuid_string))
    except Exception as error:
        print(error)
        print(uuid_string)
        return uuid_string





ID = "4261296f-4625-4a92-9b8e-ab5369f29a86"
VERSION = "1"
NAME = "BaseVoltage"
DEFINITION = "List of commonly used Base Voltages"
ISSUED = datetime.utcnow().isoformat()
DIST_ID = str(uuid.uuid4())
INSTANCE_ID = str(uuid.uuid4())

# Distribution part, needed for filename
header_list = [
                (DIST_ID, "Type", "Distribution", INSTANCE_ID),
                (DIST_ID, "label", f"../GeneratedData/{NAME}.rdf", INSTANCE_ID),
                #(DIST_ID, "issued", ISSUED, INSTANCE_ID),
                (DIST_ID, "modified", ISSUED, INSTANCE_ID),
                (DIST_ID, "version", VERSION, INSTANCE_ID),

                # Concept scheme definition
                (NAME, "Type", "ConceptScheme", INSTANCE_ID),
                #(NAME, "issued", ISSUED, INSTANCE_ID),
                (NAME, "modified", ISSUED, INSTANCE_ID),
                (NAME, "version", VERSION, INSTANCE_ID),
                #(NAME, "label", NAME, INSTANCE_ID),
                (NAME, "prefLabel", NAME, INSTANCE_ID),
                (NAME, "identifier", ID, INSTANCE_ID),
                #(NAME, "keyword", "BV", INSTANCE_ID),
                (NAME, "definition", DEFINITION, INSTANCE_ID)
                ]

data = pandas.read_RDF([r"C:\Users\kristjan.vilgo\Documents\GitHub\USVDM\Tools\ENTSOE_BOUNDARY_UPDATE\export\20211007T0000Z__ENTSOE_EQBD_001.zip"])
basevoltages = data.filter_by_type("BaseVoltage")

# Fix UUID representation where possible
basevoltages.ID = basevoltages.ID.apply(fix_uuid)

# Add ID-s as dcterms identifiers
id_data = basevoltages.query("KEY == 'Type'")
id_data.VALUE = id_data.ID
id_data.KEY = "identifier"

basevoltages = pandas.concat([basevoltages, id_data])

# Set instance ID
basevoltages["INSTANCE_ID"] = INSTANCE_ID

# Set new ID, that includes base path
basevoltages["ID"] = f"{NAME}/" + basevoltages["ID"]

data = pandas.concat([pandas.DataFrame(header_list, columns=["ID", "KEY", "VALUE", "INSTANCE_ID"]), basevoltages])






# Bring some original values under new keys to data
#data = rename_and_append_key(data, "EICCode_MarketDocument.long_Names.name", "altLabel")
#data = rename_and_append_key(data, "EICCode_MarketDocument.lastRequest_DateAndOrTime.date", "start.use")
data = rename_and_append_key(data, "IdentifiedObject.name", "prefLabel")
data = rename_and_append_key(data, "IdentifiedObject.description", "definition")
data = rename_and_append_key(data, "IdentifiedObject.mRID", "identifier")

data = rename_and_append_key(data, "Type", "Type", original_value=NAME, new_value="Concept")

type_data = data.query("KEY == 'Type' and VALUE == @NAME")
type_data["KEY"] = "type"
type_data["VALUE"] = f"http://iec.ch/TC57/CIM100#{NAME}"
data.update(type_data)

data = add_key_and_value(data, type="Concept", key="inScheme", value=NAME)
data = add_key_and_value(data, type="Concept", key="topConceptOf", value=NAME)




rdf_map = RDF_parser.load_export_conf(["conf_skos.json",
                                       "conf_dcat.json",
                                       "conf_cim100.json",
                                       "conf_rdf_rdfs.json"])

namespace_map = {
    "cim": "http://iec.ch/TC57/CIM100#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "dcat": "http://www.w3.org/ns/dcat#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "at": "http://publications.europa.eu/ontology/authority/",
    "dcterms": "http://purl.org/dc/terms/",
}

# Export triplet to CGMES
data.export_to_cimxml(rdf_map=rdf_map,
                      namespace_map=namespace_map,
                      export_undefined=False,
                      export_type="xml_per_instance",
                      debug=False
                      )

