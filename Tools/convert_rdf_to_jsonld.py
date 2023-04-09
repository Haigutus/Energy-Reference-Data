from rdflib import Graph
from lxml import etree
from pathlib import Path

#from rdflib.plugin import register, Serializer, Parser
#from rdflib.serializer import SerializerRegistry

# Register the JSON-LD serializer and parser with rdflib
#register('json-ld', Serializer, 'rdflib_jsonld.serializer', 'JsonLDSerializer')
#SerializerRegistry.register('json-ld', (Parser, 'rdflib_jsonld.parser', 'JsonLDParser'), (), {
#    "useNativeTypes": True,
#    "useRdfType": True
#})

# Load RDF/XML data into an rdflib graph

source_rdf = r'/home/kristjan/GIT/Energy-Reference-Data/docs/PowerFlowSettings.rdf'

def convert_rdfxml_to_jsonld(source_path, destination_path):
    # Parse to graph
    g = Graph()
    g.parse(source_path, format='application/rdf+xml')

    # Extend context
    context = {f"@{key}": value for key, value in etree.parse(source_path).getroot().nsmap.items()}
    context["@language"] = "en"

    # Serialize rdflib graph to JSON-LD
    jsonld_data = g.serialize(format='json-ld', indent=4, context=context)

    # Write JSON-LD data to a file
    Path(destination_path).write_text(jsonld_data)


convert_rdfxml_to_jsonld(source_rdf, "data_def.jsonld")
