"""
Set OPENAI_API_KEY env var before running this script
"""
from typing import Any, Optional, Dict

import neo4j
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.retrievers import VectorCypherRetriever, Text2CypherRetriever, ToolsRetriever
from neo4j_graphrag.retrievers.base import Retriever
from neo4j_graphrag.tool import ObjectParameter
from neo4j_graphrag.types import RawSearchResult

# Define database credentials
URI = "neo4j+s://demo.neo4jlabs.com"
AUTH = ("recommendations", "recommendations")
DATABASE = "recommendations"
INDEX_NAME = "moviePlotsEmbedding"


class CypherRetriever(Retriever):
    """A custom retriever to execute a cypher query."""
    def __init__(self, driver: neo4j.Driver, cypher_template: str, cypher_param_description: dict[str, dict[str, str]], neo4j_database: Optional[str] = None):
        super().__init__(driver, neo4j_database)
        self.cypher_template = cypher_template
        self.cypher_param_description = cypher_param_description

    def get_parameters(
        self, parameter_descriptions: Optional[Dict[str, str]] = None
    ) -> "ObjectParameter":
        return ObjectParameter(
            description="",
            properties=self.cypher_param_description,  # type: ignore
        )

    def get_search_results(self, **kwargs: Any) -> RawSearchResult:
        return self.driver.execute_query(
            self.cypher_template,
            parameters_=kwargs,
            database_=self.neo4j_database,
        )

with neo4j.GraphDatabase.driver(URI, auth=AUTH) as driver:
    t2c_llm = OpenAILLM(model_name="gpt-4o")
    tool_retriever_llm = t2c_llm

    movie_actors = VectorCypherRetriever(
        driver=driver,
        index_name=INDEX_NAME,
        embedder=OpenAIEmbeddings(),
        # for each Movie node matched by the vector search, retrieve more context:
        # the name of all actors starring in that movie
        retrieval_query="""
        RETURN  node.title as movieTitle,
                node.plot as moviePlot,
                collect { MATCH (actor:Actor)-[:ACTED_IN]->(node) RETURN actor.name } AS actors,
                score as similarityScore
        """,
        neo4j_database=DATABASE,
    )
    movie_directors = VectorCypherRetriever(
        driver=driver,
        index_name=INDEX_NAME,
        embedder=OpenAIEmbeddings(),
        # for each Movie node matched by the vector search, retrieve more context:
        # the name of all actors starring in that movie
        retrieval_query="""
        RETURN  node.title as movieTitle,
                node.plot as moviePlot,
                collect { MATCH (actor:Actor)<-[:DIRECTED_BY]-(node) RETURN actor.name } AS actors,
                score as similarityScore
        """,
        neo4j_database=DATABASE,
    )
    # t2c_retriever = Text2CypherRetriever(
    #     driver,
    #     llm=t2c_llm,
    #     neo4j_database=DATABASE,
    # )

    cypher_template_retriever = CypherRetriever(
        driver,
        cypher_template="""MATCH (m:Movie)
        WHERE m.title = $movie_title
        RETURN m
        """,
        cypher_param_description={
            "movieTitle": {
                "type": "string",
                # "required": True,
                "description": "The title of the movie."
            }
        },
        neo4j_database=DATABASE,
    )

    tool_retriever = ToolsRetriever(
        driver=driver,
        llm=tool_retriever_llm,
        tools=[
            movie_actors.convert_to_tool(
                name="movie_actors",
                description="List name of actors acting in movies semantically matching the user question",
            ),
            movie_directors.convert_to_tool(
                name="movie_directors",
                description="List name of directors acting in movies semantically matching the user question",
            ),
            cypher_template_retriever.convert_to_tool(
                name="movie_data_from_title",
                description="Fetch movie information from its title",
            ),
            t2c_retriever.convert_to_tool(
                name="t2c_retriever",
                description="Use this tool when no other tool can help. It will directly try to build a Cypher query to query the graph."
            )
        ]
    )

    query_text = "Find actors acting in a movie about aliens"
    retriever_result = tool_retriever.search(query_text=query_text, top_k=1)

    print(
        "Context", retriever_result.items,
    )
    print(
        "Metadata", retriever_result.metadata,
    )

