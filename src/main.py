from model.node import Node
from model.relationship import Relationship
from typing import Set, Dict
from graph_creator import create_knowledge_graph
from visualization_tool import visualize

def main():
    # Initialize the graph
    graph: Dict[str, Node] = {}

    # Read and process documents
    documents = read_documents()

    graph = create_knowledge_graph(documents)
    visualize(graph)


def read_documents() -> Dict[int, str]:
    # Placeholder function to read documents
    # In a real implementation, this would read from files or a database
    return {
        1: open("documents/story1.txt").read(),
        2: open("documents/story2.txt").read(),
        3: open("documents/story3.txt").read(),
    }

if __name__ == "__main__":
    main()
