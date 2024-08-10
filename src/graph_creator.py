import os
from typing import Dict, List, Tuple
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
from model.node import Node
from model.relationship import Relationship

# Load environment variables
load_dotenv()

# Set up OpenAI API key
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI()

def create_knowledge_graph(documents: Dict[int, str]) -> Dict[str, Node]:
    graph: Dict[str, Node] = {}

    print("Extracting entities and relationships from documents...")
    for doc_id, content in documents.items():
        print(f"Extracting entities and relationships from document {doc_id}...")
        info = extract_entities_and_relationships(content)
        
        # Add nodes to the graph
        for entity in info.entities:
            name = entity.name
            descriptors = entity.descriptors_not_relationships
            add_node(graph, name, descriptors, doc_id)
        
        # Add relationships to the graph
        for rel in info.relationships:
            source = rel.source_entity
            target = rel.target_entity
            relator = rel.relationship_from_source_to_target
            if source not in graph:
                add_node(graph, source, [], doc_id)
            if target not in graph:
                add_node(graph, target, [], doc_id)
            proper_relationship = Relationship(relator, doc_id, {}, False)
            reverse_relationship = Relationship(relator, doc_id, {}, True)
            graph[source].add_relationship(graph[target], proper_relationship)
            graph[target].add_relationship(graph[source], reverse_relationship)

    return graph

def add_node(graph: Dict[str, Node], name: str, facts: List[str], doc_id: int) -> None:
    if name not in graph:
        graph[name] = Node(name)
    graph[name].add_document(doc_id)
    for fact in facts:
        graph[name].add_fact(doc_id, fact)

def extract_entities_and_relationships(content: str):

    class Entity(BaseModel):
        name: str
        descriptors_not_relationships: list[str]

    class Relationship(BaseModel):
        source_entity: str
        target_entity: str
        relationship_from_source_to_target: str

    class Information(BaseModel):
        entities: list[Entity]
        relationships: list[Relationship]

    extrapolator_prompt = """
    You are a helpful assistant that extracts entities and relationships from text.
    
    Guidelines:
    - Any specific facts about an entity should be listed as a descriptor.
    - If a fact relates an entity to another entity, it should be listed as a relationship.
    
    Please analyze the given text and extract entities and relationships accordingly.
    """
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": extrapolator_prompt},
            {"role": "user", "content": content}
        ],
        response_format=Information,
    )

    info = completion.choices[0].message.parsed
    
    return info
