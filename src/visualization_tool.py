import tkinter as tk
from tkinter import ttk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Dict
from model.node import Node
from model.relationship import Relationship

def get_knowledge_graph(graph: Dict[str, 'Node']):
    # Create a NetworkX graph
    G = nx.DiGraph()

    # Add nodes and edges to the graph
    for node_name, node in graph.items():
        G.add_node(node_name)
        for target_node, relationships in node.edges.items():
            for relationship in relationships:
                if not relationship.backwards:
                    G.add_edge(node_name, target_node.name, label=relationship.information)

    # Create a matplotlib figure and axis
    fig, ax = plt.subplots(figsize=(14, 10))

    # Use a different layout algorithm for better spacing
    pos = nx.circular_layout(G)

    # Draw the graph with thicker edges
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=4000, font_size=10, font_weight='bold', edge_color='gray', linewidths=1.5, arrows=True, arrowsize=20, ax=ax)

    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, label_pos=0.5, font_size=8, font_color='black', ax=ax)

    # Add node information as text
    for node_name, node in graph.items():
        x, y = pos[node_name]
        ax.text(x, y+0.1, f"Docs: {', '.join(map(str, node.documents))}", ha='center', va='center', bbox=dict(facecolor='white', edgecolor='none', alpha=0.7), fontsize=8)
        
        # Split facts into lines to avoid overlapping
        fact_lines = [f"{fact} (Doc: {doc_id})" for doc_id, facts in node.facts.items() for fact in facts]
        fact_text = "\n".join(fact_lines)
        ax.text(x, y-0.1, fact_text, ha='center', va='top', bbox=dict(facecolor='white', edgecolor='none', alpha=0.7), fontsize=8)

    ax.set_title("Knowledge Graph Visualization", fontsize=14)
    ax.axis('off')

    return fig

def visualize(graph: Dict[str, 'Node']):
    # Create the main application window
    root = tk.Tk()
    root.title("Graph Visualization with Tabs")

    # Create a Notebook (a tab control)
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # Create tabs
    graph_tab = ttk.Frame(notebook)
    second_tab = ttk.Frame(notebook)
    third_tab = ttk.Frame(notebook)

    notebook.add(graph_tab, text="Graph")
    notebook.add(second_tab, text="Second Tab")
    notebook.add(third_tab, text="Third Tab")

    # Add graph to the first tab
    fig = get_knowledge_graph(graph)
    canvas = FigureCanvasTkAgg(fig, master=graph_tab)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

    # Add text to the second and third tabs
    second_label = tk.Label(second_tab, text="Second Tab", font=("Arial", 16))
    second_label.pack(padx=20, pady=20)

    third_label = tk.Label(third_tab, text="Third Tab", font=("Arial", 16))
    third_label.pack(padx=20, pady=20)

    # Start the Tkinter main loop
    root.mainloop()