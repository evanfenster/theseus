import os
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv
from model.node import Node
from model.relationship import Relationship
from model.path import Path
from enum import Enum
from pydantic import BaseModel
from prompts.search_prompts import SOURCE_SYSTEM_PROMPT, SEARCH_SYSTEM_PROMPT, SEARCH_USER_PROMPT, ANSWER_SYSTEM_PROMPT, ANSWER_USER_PROMPT

# Load environment variables
load_dotenv()

# Set up OpenAI API key
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI()

def search(graph: Dict[str, Node], query: str, depth: int, permissions: set() = {-1}):
    if -1 in permissions:
        node_names = Enum('Entity', {x: x for x in graph.keys()})
    else:
        node_names = Enum('Entity', {x: x for x in graph.keys() if any(doc in permissions for doc in graph[x].documents)})
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
    result, final_path = bfs(graph, query, [path], set([source_node]), depth, permissions)
    print(result.best_guess)
    print(result.positive_explation)
    print(result.potential_issues)
    return result, final_path

def select_source_node(nodes: Enum, query: str):
    class SourceNode(BaseModel):
        source: nodes

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": SOURCE_SYSTEM_PROMPT},
            {"role": "user", "content": "Given the following question, select an entity that most closely matches something DIRECTLY MENTIONED in the question: " + query}
        ],
        response_format=SourceNode,
    )

    ans = completion.choices[0].message.parsed
    return ans.source.name

# bfs - BEST First Search
def bfs(graph: Dict[str, Node], query: str, paths: list[Path], visited: set(), max_iterations: int, permissions: set() = {-1}):
    options = []
    option_num_to_path_num = {}
    for i, path in enumerate(paths): 
        for node in path.get_nodes():
            for neighbor in node.edges.keys():
                if neighbor not in visited and (-1 in permissions or any(rel.document_source in permissions for rel in node.edges[neighbor])):
                    path_copy = Path()
                    path_copy.elements = path.elements.copy()
                    path_copy.add_edge(node.edges[neighbor])
                    path_copy.add_node(graph[neighbor.name])
                    option_num_to_path_num[len(options)] = i
                    options.append(path_copy)
    
    # TO-DO: Better handling of exploring all possible paths based on source node
    # This just repeats last search until depth expires
    # Could pick new source node or end early
    if options:
        options_enum = Enum('Option', {f'option_{i}': i for i in range(len(options))})
    else:
        options_enum = Enum('Option', {f'option_{i}': i for i in range(1)})
        options = [paths[-1]]
    
    class NextStep(BaseModel):
        reasoning: str
        complete: bool
        next_step: options_enum

    options_string = [f"option_{i}: {option.to_string(permissions)}" for i, option in enumerate(options)]

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": SEARCH_SYSTEM_PROMPT},
            {"role": "user", "content": SEARCH_USER_PROMPT.format(query=query, options_string=options_string)}
        ],
        response_format=NextStep,
    )

    result = completion.choices[0].message.parsed

    print("#--------------------------------------------------------------#")
    print("Options:")
    for i, option in enumerate(options):
        print(f"option_{i}: {option.to_string(permissions)}")
    print("Reasoning: " + result.reasoning)
    print("Complete?: " + str(result.complete))
    print("Option Chosen: " + result.next_step.name)
    print("#--------------------------------------------------------------#")

    complete = result.complete
    reasoning = result.reasoning
    option_num = int(result.next_step.name.split("_")[-1])
    if complete or max_iterations <= 1:
        return solidify_answer(query, reasoning, options[option_num], permissions)
    else:
        path_taken_num = option_num_to_path_num[option_num]
        paths[path_taken_num] = options[option_num]
        visited_node = paths[path_taken_num].last_node()
        visited.add(visited_node)
        return bfs(graph, query, paths, visited, max_iterations - 1, permissions)

def solidify_answer(query: str, reasoning: str, path: Path, permissions: set() = {-1}):
    class Answer(BaseModel):
        best_guess: str
        positive_explation: str
        potential_issues: str

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
            {"role": "user", "content": ANSWER_USER_PROMPT.format(query=query, reasoning=reasoning, final_path=path.to_string(permissions))}
        ],
        response_format=Answer,
    )

    return (completion.choices[0].message.parsed, path)






