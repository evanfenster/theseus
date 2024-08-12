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
    result, history = bfs(graph, query, [path], set([source_node]), depth, [], permissions)
    print(result.best_guess)
    print(result.positive_explation)
    print(result.potential_issues)
    return result, history

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
def bfs(graph: Dict[str, Node], query: str, paths: list[Path], visited: set(), max_iterations: int, history: list[str, Path], permissions: set() = {-1}):
    options = []
    option_num_to_path_num = {}
    for i, path in enumerate(paths): 
        curr_path = Path()
        for node in path.get_nodes():
            curr_path.add_node(node)
            for neighbor in node.edges.keys():
                if neighbor not in visited and (-1 in permissions or any(rel.document_source in permissions for rel in node.edges[neighbor])):
                    copy_curr_path = curr_path.copy()
                    copy_curr_path.add_edge(node.edges[neighbor])
                    copy_curr_path.add_node(graph[neighbor.name])
                    option_num_to_path_num[len(options)] = i
                    options.append(copy_curr_path)
            next_edge_idx = i*2+1
            if (len(path.elements) > next_edge_idx):
                curr_path.add_edge(path.elements[next_edge_idx])
    
    # If no more possible paths (#TO-DO potentially add starting at another source node in different CC)
    if not options:
        return solidify_answer(query, history), history

    options_enum = Enum('Option', {f'option_{i}': i for i in range(len(options))})
    
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
    path_taken_num = option_num_to_path_num[option_num]
    paths[path_taken_num] = options[option_num]
    history.append((reasoning, paths[path_taken_num]))
    if complete or max_iterations <= 1:
        # Need to actually return all paths taken
        return solidify_answer(query, history), history
    else:
        visited_node = paths[path_taken_num].last_node()
        visited.add(visited_node)
        return bfs(graph, query, paths, visited, max_iterations - 1, history, permissions)

def solidify_answer(query: str, history: list[str, Path]):
    class Answer(BaseModel):
        best_guess: str
        positive_explation: str
        potential_issues: str

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
            {"role": "user", "content": ANSWER_USER_PROMPT.format(query=query, history=history)}
        ],
        response_format=Answer,
    )

    return completion.choices[0].message.parsed






