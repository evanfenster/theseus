from model.node import Node
from model.relationship import Relationship
from typing import Set, Dict
from graph_creator import create_knowledge_graph
import sys
import networkx as nx
import matplotlib.pyplot as plt

def main():
    # Initialize the graph
    graph: Dict[str, Node] = {}

    # Read and process documents
    documents = read_documents()

    def visualize_knowledge_graph(graph: Dict[str, 'Node']):
        # Create a NetworkX graph
        G = nx.DiGraph()

        # Add nodes and edges to the graph
        for node_name, node in graph.items():
            G.add_node(node_name)
            for target_node, relationships in node.edges.items():
                for relationship in relationships:
                    if not relationship.backwards:
                        G.add_edge(node_name, target_node.name, label=relationship.information)

        # Set up the plot
        plt.figure(figsize=(14, 10))  # Increase figure size for better readability

        # Use a different layout algorithm for better spacing
        pos = nx.circular_layout(G)

        # Draw the graph with thicker edges
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=4000, font_size=10, font_weight='bold', edge_color='gray', linewidths=1.5, arrows=True, arrowsize=20)

        # Draw edge labels
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, label_pos=0.5, font_size=8, font_color='black')

        # Add node information as text
        for node_name, node in graph.items():
            x, y = pos[node_name]
            plt.text(x, y+0.1, f"Docs: {', '.join(map(str, node.documents))}", ha='center', va='center', bbox=dict(facecolor='white', edgecolor='none', alpha=0.7), fontsize=8)
            
            # Split facts into lines to avoid overlapping
            fact_lines = [f"{fact} (Doc: {doc_id})" for doc_id, facts in node.facts.items() for fact in facts]
            fact_text = "\n".join(fact_lines)
            plt.text(x, y-0.1, fact_text, ha='center', va='top', bbox=dict(facecolor='white', edgecolor='none', alpha=0.7), fontsize=8)

        plt.title("Knowledge Graph Visualization", fontsize=14)
        plt.axis('off')
        plt.tight_layout()
        plt.show()


    graph = create_knowledge_graph(documents)
    visualize_knowledge_graph(graph)

    # # Extract entities and relationships
    # for doc_id, content in documents.items():
    #     entities, relationships = extract_entities_and_relationships(content)
        
    #     # Add nodes and relationships to the graph
    #     for entity in entities:
    #         if entity not in graph:
    #             graph[entity] = Node(entity)
    #         graph[entity].add_document(doc_id)
        
    #     for rel in relationships:
    #         source, target, rel_type = rel
    #         if source in graph and target in graph:
    #             relationship = Relationship(rel_type, {doc_id})
    #             graph[source].add_relationship(graph[target], relationship)

    # # Perform graph analysis
    # analyze_graph(graph)

    # # User interaction loop
    # while True:
    #     query = input("Enter your query (or 'quit' to exit): ")
    #     if query.lower() == 'quit':
    #         break
    #     results = search_graph(graph, query)
    #     display_results(results)

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
