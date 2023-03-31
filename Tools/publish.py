from lxml import etree
from pathlib import Path


def publish_item(data, name, relative_path="", base_path=r"../docs"):
    # Define all folder and path names
    item_path = Path(base_path).joinpath(Path(relative_path)).joinpath(Path(name))
    print(f"Publishing {item_path}")

    item_file_name = Path(f"{name}.rdf")

    item_file_path = item_path.joinpath(item_file_name)
    item_index_path = item_path.joinpath(Path("index.html"))

    # Create path
    item_path.mkdir(parents=True, exist_ok=True)

    # Write index.html
    item_index_path.write_text(redirect_html_template.format(path=item_file_name))

    # Write .rdf data itself
    item_file_path.write_bytes(etree.tostring(data))


redirect_html_template = """
<!DOCTYPE html>
<html>
    <body>
        <meta http-equiv = "refresh" content = "0; url = {path}" />
    </body>
</html>"""



data_to_publish = [
    "../GeneratedData/PowerFlowSettings.rdf",
    "../GeneratedData/BaseVoltage.rdf",
    "../GeneratedData/entsoe-codelist-StandardEicTypeList.rdf",
    "../GeneratedData/entsoe-codelist-StandardMarketProductTypeList.rdf",
    "../GeneratedData/entsoe-codelist-StandardReasonCodeTypeList.rdf",
    "../GeneratedData/entsoe-codelist-StandardRoleTypeList.rdf",
    "../GeneratedData/entsoe-codelist-StandardStatusTypeList.rdf"
]

# TODO - add a conf file for data to be published
# TODO - create nice HTML page with all published data to root
# TODO - add status to ConceptScheme and Concept so that official and unofficial lists can be differenciated


for item in data_to_publish:
    # Parse XML and find relevant elements
    data = etree.parse(item)
    concept_scheme = data.find("{*}ConceptScheme")
    concepts = data.iterfind("{*}Concept")

    # Extract metadata from ConceptScheme
    concept_scheme_metadata = {child.tag.split("}")[1]: child.text for child in concept_scheme.getchildren() if child.text != None}

    # Publish ConceptCheme
    publish_item(data, concept_scheme_metadata["prefLabel"])

    # Publish Concepts
    for concept in concepts:
        name = concept.attrib.values()[0].split("/")[-1]
        relative_path = concept_scheme_metadata["prefLabel"]
        publish_item(concept, name, relative_path)

print("Done")

