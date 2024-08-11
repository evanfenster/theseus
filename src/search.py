import os
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv
from model.node import Node
from model.relationship import Relationship
from model.path import Path
from enum import Enum
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Set up OpenAI API key
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI()

def search(graph: Dict[str, Node], query: str):
    node_names = Enum('Entity', {x: x for x in graph.keys()})
    # Select a source node
    source_name = select_source_node(node_names, query)
    source_node = graph[source_name]
    print("Question: " + query)
    print("Optimal starting entity: " + source_name)

    # Create our starting path
    path = Path()
    path.add_node(source_node)

    # Begin search
    print("Starting search ...")
    bfs(graph, query, [path], set([source_node]))

# bfs - BEST First Search
def bfs(graph: Dict[str, Node], query: str, paths: list[Path], visited: set()):
    # maintain a list of "paths" taken so far: entity -> relationship -> entity -> relationship -> etc. etc. 
    # Complete: true/false - ask LLM if it knows enough based on current set of paths to answer question
    # Optional[NextNode]: if !Complete, continue BFS (BestFirstSearch), from NextNode and append new information to that path
    # repeat
    options = []
    for path in paths: 
        last_node = path.last_node()
        for neighbor in last_node.edges.keys():
            if neighbor not in visited:
                path_copy = Path()
                path_copy.elements = path.elements.copy()
                path_copy.add_edge(last_node.edges[neighbor])
                path_copy.add_node(graph[neighbor.name])
                options.append(path_copy)
    
    options_enum = Enum('Option', {f'option_{i}': i for i in range(len(options))})
    
    class NextStep(BaseModel):
        reasoning: str
        complete: bool
        next_step: options_enum

    options_string = [f"option_{i}: {option}" for i, option in enumerate(options)]
    print(options_string)
    
    system_prompt = """
    You are an AI designed to assist in a graph search algorithm. Your task is to analyze the current paths explored and determine the next step to explore, as well as whether the current information is sufficient to answer the original query.

    Instructions:
    1. Review the paths explored so far and the original query.
    2. Determine if the information gathered so far is sufficient to answer the query.
    3. If the current information is enough to answer the query without exploring any further, set 'complete' to True.
    4. If more information is needed to answer the query, set 'complete' to False.
    5. Regardless of whether 'complete' is True or False, select the most promising 'next_step' to explore based on its potential to provide relevant information for the query.
    6. Note that there may not be an obvious next_step that will bring us much closer to answering the question, but we should still pick the best choice among the available options.
    """
    user_prompt = f"""
    Based on the information provided, please determine if we already have enough information to answer the question without taking any extra steps. If we do, set 'complete' to True. Otherwise, set 'complete' to False.

    If 'complete' is False, determine which next step will give the best chance of eventually answering the question, even if it doesn't provide much more detail immediately.

    Note that for each option, only the last edge and node are new; the rest of the path has already been explored.

    When selecting the next step:
    1. Choose the option that you believe will lead us closer to answering the query, even if it doesn't provide immediate answers.
    2. Consider how this step might open up new paths or connections that could be valuable later.
    3. Remember that the best next step might not directly relate to the answer, but could provide crucial context or lead to important connections.

    Always select a next step, even if you set 'complete' to True.

    Remember to consider the context of the query and the information we've gathered so far when making your decision.

    Query: {query}
    Options: {options_string}
    """

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Query: {query}\nPaths explored: {paths}\nOptions: {options}\nDetermine if the search is complete or which node to explore next."}
        ],
        response_format=NextStep,
    )

    result = completion.choices[0].message.parsed
    print("Reasoning: " + result.reasoning)
    print("Complete?: " + str(result.complete))
    print("Option Chosen: " + result.next_step.name)

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






