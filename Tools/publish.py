from lxml import etree
from pathlib import Path

publication_base_path = r"../docs"
def publish_item(data, name, relative_path="", base_path=publication_base_path):
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
    item_file_path.write_bytes(etree.tostring(data, pretty_print=True))


redirect_html_template = """
<!DOCTYPE html>
<html>
    <body>
        <meta http-equiv = "refresh" content = "0; url = {path}" />
    </body>
</html>"""

frontpage_html_template = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Energy Reference Data SKOS Concept Schemes</title>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-L1R5VF4NBS"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());    
      gtag('config', 'G-L1R5VF4NBS');
    </script>
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

# TODO - add a conf file for data to be published
# TODO - create nice HTML page with all published data to root
# TODO - add status to ConceptScheme and Concept so that official and unofficial lists can be differenciated

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
        rdf_root = etree.Element('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF')
        rdf_root.append(concept)

        publish_item(rdf_root, name, relative_path)

print(f"Generating frontpage to {publication_base_path}")
Path(publication_base_path).joinpath("index.html").write_text(frontpage_html_template.format(frontpage_rows))
print("Done")

