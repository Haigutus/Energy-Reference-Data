from lxml import etree
from pathlib import Path
from rdflib import Graph

publication_base_path = r"../docs"
def publish_item(data, name, relative_path="", base_path=publication_base_path):
    # Define all folder and path names
    item_path = Path(base_path).joinpath(Path(relative_path)).joinpath(Path(name))
    print(f"Publishing {item_path}")

    item_file_name = Path(name)

    item_file_path = item_path.parent.joinpath(item_file_name)
    item_index_path = item_path.joinpath(Path("index.html"))

    # Create path
    item_path.mkdir(parents=True, exist_ok=True)

    # Write index.html
    item_index_path.write_text(redirect_html_template.format(path=item_file_name.with_suffix(".rdf")))

    # Write .rdf data
    item_file_path.with_suffix(".rdf").write_bytes(etree.tostring(data, pretty_print=True))

    # Generate .jsonld data based on .rdf
    convert_rdfxml_to_jsonld(item_file_path.with_suffix(".rdf"), item_file_path.with_suffix(".jsonld"))

    # Generate .ttl data based on .rdf
    convert_rdfxml_to_turtle(item_file_path.with_suffix(".rdf"), item_file_path.with_suffix(".ttl"))

from pathlib import Path

def clean_directory(path: str, excluded_files: set):
    path = Path(path)
    folders_to_delete = []
    for item in path.iterdir():
        if item.is_dir():
            folders_to_delete.append(item)
            clean_directory(item, excluded_files)
        elif item.is_file() and item.name not in excluded_files:
            item.unlink()
    for folder in  folders_to_delete:
        if not any(folder.iterdir()):
            folder.rmdir()

def convert_rdfxml_to_jsonld(source_path, destination_path):
    # Parse to graph
    graph = Graph()
    graph.parse(source_path, format='application/rdf+xml')

    # Extend context
    context = {f"@{key}": value for key, value in etree.parse(source_path).getroot().nsmap.items()}
    #context["@language"] = "en"

    # Serialize rdflib graph to JSON-LD
    data = graph.serialize(format='json-ld', indent=4, context=context, sort_keys=False, use_native_types=True)

    # Write JSON-LD data to a file
    Path(destination_path).write_text(data)

def convert_rdfxml_to_turtle(source_path, destination_path):
    # Parse to graph
    graph = Graph()
    graph.parse(source_path, format='application/rdf+xml')

    # Serialize rdflib graph to JSON-LD
    data = graph.serialize(format='turtle')

    # Write JSON-LD data to a file
    Path(destination_path).write_text(data)



redirect_html_template = """
<!DOCTYPE html>
<html>
    <head>
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-L1R5VF4NBS"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
        
          gtag('config', 'G-L1R5VF4NBS');
        </script>
    </head>    
    <body>
        <meta http-equiv = "refresh" content = "0; url = ../{path}" />
    </body>
</html>"""

frontpage_html_template = """
<!DOCTYPE html>
<html>
  <head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-L1R5VF4NBS"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
    
      gtag('config', 'G-L1R5VF4NBS');
    </script>
    
    <!-- Metadata Section -->
    <meta charset="UTF-8">
    <title>Energy Reference Data SKOS Concept Schemes</title>
    <meta name="description" content="This project aims to create common reference data for energy-related business processes using SKOS, DCAT, and CIM.">
    <meta name="keywords" content="reference data, energy, SKOS, DCAT, CIM, rdf, cim, dcat, skos, entso-e, codelists, EIC, CGMES, meter reading">
    <meta name="robots" content="index,follow">
    <meta name="dc.language" content="en">
    <meta name="dc.title" content="Energy Reference Data SKOS Concept Schemes">
    <meta name="dc.description" content="This project aims to create common reference data for energy-related business processes using SKOS, DCAT, and CIM.">
    <meta name="dc.subject" content="reference data, energy, SKOS, DCAT, CIM, rdf, cim, dcat, skos, entso-e, codelists, EIC, CGMES, meter reading">
    <style>
           body {{
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        background-color: #fff;
        color: #000;
      }}
      header {{
        background-color: #000;
        color: #fff;
        padding: 20px;
        text-align: center;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }}
      header a {{
        display: flex;
        align-items: center;
        color: #fff;
        text-decoration: none;
      }}
      header img {{
        height: 50px;
        margin-right: 10px;
      }}
      h1 {{
        margin: 0;
        font-size: 2em;
        font-weight: bold;
        text-transform: uppercase;
      }}
      main {{
        max-width: 1600px;
        margin: 0 auto;
        padding: 20px;
        line-height: 1.5;
      }}
      table {{
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 20px;
      }}
      th, td {{
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
      }}
      th {{
        background-color: #f2f2f2;
        font-weight: bold;
        text-transform: uppercase;
      }}
      a {{
        color: #000;
        text-decoration: none;
        font-weight: bold;
      }}
      a:hover {{
        color: #f00;
      }}
    </style>
  </head>
  <body>
    <header>
      <div></div>      
      <h1>Energy Reference Data</h1>
      <a href="https://github.com/Haigutus/Energy-Reference-Data" target="_blank">
        <img src="github-mark-white.svg" alt="GitHub Logo">
      </a>
    </header>
    <main>
      <table>
        <thead>
          <tr>
            <th>Label</th>
            <th>Definition</th>
            <th>Modified</th>
            <th>Version</th>            
            <th>Identifier</th>
          </tr>
        </thead>
        <tbody>
          {}
          <!-- Add more rows for each concept scheme -->
        </tbody>
      </table>
    </main>
  </body>
</html>
"""

table_row_html_template = """
<tr>
    <td><a href="{prefLabel}">{prefLabel}</a></td>
    <td>{definition}</td>
    <td>{modified}</td>
    <td>{version}</td>
    <td>{identifier}</td>        
</tr>
"""



data_to_publish = [
    "../GeneratedData/PowerFlowSettings.rdf",
    "../GeneratedData/BaseVoltage.rdf",
    "../GeneratedData/entsoe-codelist-StandardEicTypeList.rdf",
    "../GeneratedData/entsoe-codelist-StandardMarketProductTypeList.rdf",
    "../GeneratedData/entsoe-codelist-StandardReasonCodeTypeList.rdf",
    "../GeneratedData/entsoe-codelist-StandardRoleTypeList.rdf",
    "../GeneratedData/entsoe-codelist-StandardStatusTypeList.rdf"
]

files_to_keep = {
    "CNAME",
    "github-mark-white.svg"
}

# TODO - add a conf file for data to be published
# TODO - add status to ConceptScheme and Concept so that official and unofficial lists can be differentiated

# Clean
clean_directory(publication_base_path, files_to_keep)
# Generate new content
frontpage_rows = ""
for item in data_to_publish:
    # Parse XML and find relevant elements
    parser = etree.XMLParser(remove_blank_text=True)
    data = etree.parse(item, parser=parser)
    concept_scheme = data.find("{*}ConceptScheme")
    concepts = data.iterfind("{*}Concept")

    # Extract metadata from ConceptScheme
    concept_scheme_metadata = {child.tag.split("}")[1]: child.text for child in concept_scheme.getchildren() if child.text != None}
    frontpage_rows += table_row_html_template.format(**concept_scheme_metadata)

    # Publish ConceptCheme
    publish_item(data, concept_scheme_metadata["prefLabel"])

    # Publish Concepts
    for concept in concepts:
        name = concept.attrib.values()[0].split("/")[-1]
        relative_path = concept_scheme_metadata["prefLabel"]

        # Wrap concept in RDF root element
        rdf_root = etree.Element('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF', nsmap=concept.nsmap)
        rdf_root.append(concept)

        publish_item(rdf_root, name, relative_path)

print(f"Generating frontpage to {publication_base_path}")
Path(publication_base_path).joinpath("index.html").write_text(frontpage_html_template.format(frontpage_rows))
print("Done")

