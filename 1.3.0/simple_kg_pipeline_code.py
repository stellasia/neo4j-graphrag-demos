"""
pip install "neo4j-graphrag[openai, experimental]"
"""

import asyncio

import neo4j
from neo4j_graphrag.llm.openai_llm import OpenAILLM
from neo4j_graphrag.embeddings import OpenAIEmbeddings
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.experimental.pipeline.pipeline import PipelineResult
from neo4j_graphrag.experimental.components.types import LexicalGraphConfig
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import FixedSizeSplitter
from neo4j_graphrag.experimental.pipeline.types import (
    EntityInputType,
    RelationInputType,
)


# Neo4j db infos
URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")
DATABASE = "neo4j"


# Instantiate Entity and Relation objects. This defines the
# entities and relations the LLM will be looking for in the text.
ENTITIES: list[EntityInputType] = [
    # entities can be defined with a simple label...
    "Person",
    # ... or with a dict if more details are needed,
    # such as a description:
    {"label": "House", "description": "Family the person belongs to"},
    # or a list of properties the LLM will try to attach to the entity:
    {"label": "Planet", "properties": [{"name": "weather", "type": "STRING"}]},
]
# same thing for relationships:
RELATIONS: list[RelationInputType] = [
    "PARENT_OF",
    {
        "label": "HEIR_OF",
        "description": "Used for inheritor relationship between father and sons",
    },
    {"label": "RULES", "properties": [{"name": "fromYear", "type": "INTEGER"}]},
]
POTENTIAL_SCHEMA = [
    ("Person", "PARENT_OF", "Person"),
    ("Person", "HEIR_OF", "House"),
    ("House", "RULES", "Planet"),
]

async def main() -> PipelineResult:
    llm = OpenAILLM(
        model_name="gpt-4o",
        model_params={
            "max_tokens": 2000,
            "response_format": {"type": "json_object"},
            "temperature": 0,
        },
    )
    embedder = OpenAIEmbeddings()
    with neo4j.GraphDatabase.driver(URI, auth=AUTH) as driver:
        kg_builder = SimpleKGPipeline(
            llm=llm,
            driver=driver,
            embedder=embedder,
            entities=ENTITIES,
            relations=RELATIONS,
            potential_schema=POTENTIAL_SCHEMA,
            neo4j_database=DATABASE,
            from_pdf=False,
            text_splitter=FixedSizeSplitter(
                chunk_size=500,
                chunk_overlap=20,
            ),
            # pdf_loader=None,
            # kg_writer=None,
            on_error="IGNORE",
            # prompt_template="",
            # perform_entity_resolution=True,
            lexical_graph_config=LexicalGraphConfig(
                chunk_node_label="TextPart",
            ),
        )
        res = await kg_builder.run_async(text="Duke Leto Atreides of House Atreides, ruler of the ocean world Caladan, is assigned by the Padishah Emperor Shaddam IV to serve as fief ruler of the planet Arrakis.")
    await llm.async_client.close()
    return res


if __name__ == "__main__":
    res = asyncio.run(main())
    print(res)
