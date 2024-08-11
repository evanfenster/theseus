import os
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv
from model.node import Node
from model.relationship import Relationship
from enum import Enum
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Set up OpenAI API key
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI()

def search(graph: Dict[str, Node], query: str):
    node_names = Nodes = Enum('Entity', {x: x for x in graph.keys()})
    # Select a source node
    source_name = select_source_node(node_names, query)
    print(query)
    print(source_name)
    source_node = graph[source_name]
    # bfs(graph, query, source_node, set([source_node]))

# bfs - BEST First Search
def bfs(graph: Dict[str, Node], query: str, current_node: Node, visited: set()):
    # maintain a list of "paths" taken so far: entity -> relationship -> entity -> relationship -> etc. etc. 
    # Complete: true/false - ask LLM if it knows enough based on current set of paths to answer question
    # Optional[NextNode]: if !Complete, continue BFS (BestFirstSearch), from NextNode and append new information to that path
    # repeat
    pass

def select_source_node(nodes: Enum, query: str):
    class SourceNode(BaseModel):
        source: nodes

    system_prompt = """
    You are an AI designed to select the most relevant entity from a given list based on a question provided. Your task is to analyze the question and choose the entity from the list that best corresponds to the context or content of the question.

    Instructions:
    1. Read the list of entities carefully.
    2. Analyze the question provided by the user.
    3. Select the entity from the list that most accurately matches or relates to the question.
    4. Remember, the chosen entity should match something listed in the question. It should NOT answer the question itself. 
    """

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Given the following question, select an entity that most closely matches something DIRECTLY MENTIONED in the question: " + query}
        ],
        response_format=SourceNode,
    )

    ans = completion.choices[0].message.parsed
    return ans.source.name






