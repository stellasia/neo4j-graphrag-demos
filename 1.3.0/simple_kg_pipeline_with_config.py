"""In this example, the pipeline is defined in a JSON ('simple_kg_pipeline_config.json')
or YAML ('simple_kg_pipeline_config.yaml') file.

According to the configuration file, some parameters will be read from the env vars
(Neo4j credentials and the OpenAI API key).

pip install "neo4j-graphrag[openai, experimental]"

python 1.3.0/simple_kg_pipeline_with_config.py
"""

import asyncio
import logging

## If env vars are in a .env file, uncomment:
## (requires pip install python-dotenv)
# from dotenv import load_dotenv
# load_dotenv()
# env vars manually set for testing:
import os
from pathlib import Path

from neo4j_graphrag.experimental.pipeline.config.runner import PipelineRunner
from neo4j_graphrag.experimental.pipeline.pipeline import PipelineResult

logging.basicConfig()
logging.getLogger("neo4j_graphrag").setLevel(logging.DEBUG)

# os.environ["NEO4J_URI"] = "bolt://localhost:7687"
# os.environ["NEO4J_USER"] = "neo4j"
# os.environ["NEO4J_PASSWORD"] = "password"
# # os.environ["OPENAI_API_KEY"] = "sk-..."


root_dir = Path(__file__).parent
# file_path = root_dir / "configs" / "simple_kg_pipeline_config.yaml"
file_path = root_dir / "configs" / "simple_kg_pipeline_config_param_resolver.json"
# file_path = root_dir / "configs" / "simple_kg_pipeline_config_custom_component.json"

# Text to process
TEXT = """Duke Leto Atreides of House Atreides, ruler of the ocean world Caladan, is assigned by the Padishah
 Emperor Shaddam IV to serve as fief ruler of the planet Arrakis."""


async def main() -> PipelineResult:
    pipeline = PipelineRunner.from_config_file(file_path)
    return await pipeline.run({"text": TEXT})


if __name__ == "__main__":
    print(asyncio.run(main()))
