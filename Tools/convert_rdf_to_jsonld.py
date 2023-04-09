from rdflib import Graph
#from rdflib.plugin import register, Serializer, Parser
#from rdflib.serializer import SerializerRegistry

# Register the JSON-LD serializer and parser with rdflib
#register('json-ld', Serializer, 'rdflib_jsonld.serializer', 'JsonLDSerializer')
#SerializerRegistry.register('json-ld', (Parser, 'rdflib_jsonld.parser', 'JsonLDParser'), (), {
#    "useNativeTypes": True,
#    "useRdfType": True
#})

# Load RDF/XML data into an rdflib graph
g = Graph()
g.parse(r'/home/kristjan/GIT/Energy-Reference-Data/docs/PowerFlowSettings/PowerFlowSettings.rdf', format='application/rdf+xml')

# Serialize rdflib graph to JSON-LD
jsonld_data = g.serialize(format='json-ld', indent=4)

# Write JSON-LD data to a file
with open('data.jsonld', 'w') as f:
    f.write(jsonld_data)
