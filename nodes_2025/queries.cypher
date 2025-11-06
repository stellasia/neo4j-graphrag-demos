MATCH path=(:`__Entity__`)--(:`__Entity__`) RETURN path

MATCH (e:`__Entity__`)-[:FROM_CHUNK]->(c:Chunk)
WITH e, count(c) as nbChunks
WHERE nbChunks > 1
RETURN e

MATCH path=(:`__Entity__` {name: "Methane"})-[:FROM_CHUNK]->(:Chunk) RETURN path

MATCH path=(:`__Entity__`)--(:`__Entity__` {name: "Carbon emissions"})-[:FROM_CHUNK]->(:Chunk)
RETURN path

CREATE (:`__Entity__`:GreenhouseGas {name: "carbonic dioxide"})-[:OBSERVED_IN]->(:`__Entity__`:Country {name: "Greenland"})
