import tkinter as tk
from tkinter import ttk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Dict
from model.node import Node
from model.relationship import Relationship
from search import search

def get_knowledge_graph(graph: Dict[str, 'Node']):
    # Create a NetworkX graph
    G = nx.DiGraph()

    # Add nodes and edges to the graph
    for node_name, node in graph.items():
        if node_name != "__Detective__":
            G.add_node(node_name)
            for target_node, relationships in node.edges.items():
                for relationship in relationships:
                    if not relationship.backwards:
                        G.add_edge(node_name, target_node.name, label=relationship.information)

    # Create a matplotlib figure and axis
    fig, ax = plt.subplots(figsize=(14, 10))

    # Use a different layout algorithm for better visualization of distinct components
    components = list(nx.connected_components(G.to_undirected()))
    if len(components) > 1:
        # If there are multiple components, use separate layouts for each
        pos = {}
        offset = 0
        for component in components:
            subgraph = G.subgraph(component)
            sub_pos = nx.circular_layout(subgraph, scale=1.5)
            # Offset each component to avoid overlap
            sub_pos = {node: (x + offset, y) for node, (x, y) in sub_pos.items()}
            pos.update(sub_pos)
            offset += 8/len(components)  # Adjust this value to increase/decrease space between components
    else:
        # If there's only one component, use circular layout for the entire graph
        pos = nx.circular_layout(G, scale=2.0)

    # Draw the graph with thicker edges
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=4000, font_size=10, font_weight='bold', edge_color='gray', linewidths=1.5, arrows=True, arrowsize=20, ax=ax)

    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, label_pos=0.5, font_size=8, font_color='black', ax=ax)

    # Add node information as text
    for node_name, node in graph.items():
        if node_name != "__Detective__":
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
    question_tab = ttk.Frame(notebook)
    third_tab = ttk.Frame(notebook)

    notebook.add(graph_tab, text="Graph")
    notebook.add(question_tab, text="Ask a Question")
    notebook.add(third_tab, text="Third Tab")

    # Add graph to the first tab
    fig = get_knowledge_graph(graph)
    canvas = FigureCanvasTkAgg(fig, master=graph_tab)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

    # Add question input and results to the second tab
    question_label = tk.Label(question_tab, text="Enter your question:")
    question_label.pack(pady=10)

    question_entry = tk.Entry(question_tab, width=50)
    question_entry.pack(pady=10)

    result_frame = ttk.Frame(question_tab)
    result_frame.pack(fill='both', expand=True, padx=20, pady=20)

    best_guess_label = tk.Label(result_frame, text="Best Guess:")
    best_guess_label.pack(anchor='w')
    best_guess_text = tk.Text(result_frame, height=3, wrap='word')
    best_guess_text.pack(fill='x', pady=5)

    positive_explanation_label = tk.Label(result_frame, text="Positive Explanation:")
    positive_explanation_label.pack(anchor='w')
    positive_explanation_text = tk.Text(result_frame, height=5, wrap='word')
    positive_explanation_text.pack(fill='x', pady=5)

    potential_issues_label = tk.Label(result_frame, text="Potential Issues:")
    potential_issues_label.pack(anchor='w')
    potential_issues_text = tk.Text(result_frame, height=3, wrap='word')
    potential_issues_text.pack(fill='x', pady=5)

    def submit_question():
        query = question_entry.get()
        result = search(graph, query, 3)
        best_guess_text.delete('1.0', tk.END)
        best_guess_text.insert(tk.END, result.best_guess)
        positive_explanation_text.delete('1.0', tk.END)
        positive_explanation_text.insert(tk.END, result.positive_explation)
        potential_issues_text.delete('1.0', tk.END)
        potential_issues_text.insert(tk.END, result.potential_issues)

    submit_button = tk.Button(question_tab, text="Submit", command=submit_question)
    submit_button.pack(pady=10)

    # Add text to the third tab
    third_label = tk.Label(third_tab, text="Third Tab", font=("Arial", 16))
    third_label.pack(padx=20, pady=20)

    # Add a button to close the window
    close_button = tk.Button(root, text="Close", command=root.quit)
    close_button.pack(pady=10)

    # Wait for the window to be closed
    root.mainloop()