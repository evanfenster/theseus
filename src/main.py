from model.node import Node
from model.relationship import Relationship
from typing import Set, Dict
from graph_creator import create_knowledge_graph
from visualization_tool import visualize
from search import search
import os

def main():
    # Initialize the graph
    graph: Dict[str, Node] = {}

    # Read and process documents
    documents = read_documents()

    graph = create_knowledge_graph(documents)

    search(graph, "Who is Sue's favorite customer?")
    #visualize(graph)


def read_documents() -> Dict[int, str]:
    documents = {}
    document_id = 1
    documents_dir = "documents"
    for filename in os.listdir(documents_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(documents_dir, filename)
            with open(file_path, 'r') as file:
                documents[document_id] = file.read()
            document_id += 1
    return documents

if __name__ == "__main__":
    main()
