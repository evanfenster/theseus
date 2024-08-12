import tkinter as tk
from tkinter import ttk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Dict
from model.node import Node
from model.relationship import Relationship
from model.path import Path
from search import search
import os

def get_knowledge_graph(graph: Dict[str, 'Node'], final_path: Path, permissions: set[int], ax=None):
    # Create a NetworkX graph
    G = nx.DiGraph()

    # Add nodes and edges to the graph
    for node_name, node in graph.items():
        G.add_node(node_name)
        for target_node, relationships in node.edges.items():
            for relationship in relationships:
                G.add_edge(node_name, target_node.name, label=relationship.information)

    # Create a matplotlib figure and axis if not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=(14, 10))
    else:
        fig = ax.figure

    # Use a spring layout for the entire graph, spaced out to fill the screen
    pos = nx.spring_layout(G, k=1.5, iterations=50)
    # Scale the layout to fit the entire screen
    pos = {node: (x*2-1, y*2-1) for node, (x, y) in pos.items()}

    # Color nodes and edges based on the final path and permissions
    node_colors = {}
    edge_colors = {}
    if final_path:
        path_nodes = final_path.get_nodes()
        for i, node in enumerate(path_nodes):
            if i == 0:
                node_colors[node.name] = 'yellow'
            elif i == len(path_nodes) - 1:
                node_colors[node.name] = 'purple'
            else:
                node_colors[node.name] = 'green'
        
        for i in range(0, len(final_path.elements) - 1, 2):
            source = final_path.elements[i].name
            target = final_path.elements[i+2].name
            edge_colors[(source, target)] = 'green'

    # Color nodes and edges based on permissions
    for node_name, node in graph.items():
        if node_name not in node_colors:
            if -1 in permissions or any(doc in permissions for doc in node.documents):
                node_colors[node_name] = 'lightblue'
            else:
                node_colors[node_name] = 'lightgray'

    for edge in G.edges():
        if edge not in edge_colors:
            source, target = edge
            relationships = graph[source].edges[graph[target]]
            if -1 in permissions or any(rel.document_source in permissions for rel in relationships):
                edge_colors[edge] = 'lightblue'
            else:
                edge_colors[edge] = 'lightgray'

    # Draw the graph with colored nodes and edges
    nx.draw(G, pos, with_labels=True, 
            node_color=[node_colors.get(node, 'lightblue') for node in G.nodes()],
            edge_color=[edge_colors.get(edge, 'gray') for edge in G.edges()],
            node_size=4000, font_size=10, font_weight='bold', 
            linewidths=1.5, arrows=True, arrowsize=20, ax=ax)

    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, label_pos=0.5, font_size=8, font_color='black', ax=ax)

    # Add node information as text
    for node_name, node in graph.items():
        x, y = pos[node_name]
        ax.text(x, y+0.1, f"Docs: {', '.join(map(str, node.documents))}", ha='center', va='center', bbox=dict(facecolor='white', edgecolor='none', alpha=0.7), fontsize=8)
        
        fact_lines = [f"{fact} (Doc: {doc_id})" for doc_id, facts in node.facts.items() for fact in facts]
        fact_text = "\n".join(fact_lines)
        ax.text(x, y-0.1, fact_text, ha='center', va='top', bbox=dict(facecolor='white', edgecolor='none', alpha=0.7), fontsize=8)

    ax.set_title("Knowledge Graph Visualization", fontsize=14)
    ax.axis('off')

    return fig

def create_graph_tab(notebook, graph):
    graph_tab = ttk.Frame(notebook)
    notebook.add(graph_tab, text="Graph")

    fig = get_knowledge_graph(graph, None, {-1})  # Default to full permissions
    canvas = FigureCanvasTkAgg(fig, master=graph_tab)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    graph_tab.canvas = canvas
    graph_tab.permissions = {-1}  # Initialize with full permissions

    return graph_tab

def create_question_tab(notebook, graph, graph_tab):
    question_tab = ttk.Frame(notebook)
    notebook.add(question_tab, text="Ask a Question")

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
        permissions = getattr(question_tab, 'permissions', {-1})
        result, path = search(graph, query, 3, permissions)
        best_guess_text.delete('1.0', tk.END)
        best_guess_text.insert(tk.END, result.best_guess)
        positive_explanation_text.delete('1.0', tk.END)
        positive_explanation_text.insert(tk.END, result.positive_explation)
        potential_issues_text.delete('1.0', tk.END)
        potential_issues_text.insert(tk.END, result.potential_issues)
        
        print("Updating graph visualization...")
        if hasattr(graph_tab, 'canvas'):
            graph_tab.canvas.figure.clear()
            ax = graph_tab.canvas.figure.add_subplot(111)
            get_knowledge_graph(graph, path, permissions, ax)
            graph_tab.canvas.draw()
            print("REDREW")
        else:
            print("No canvas attribute found in graph_tab")

    submit_button = tk.Button(question_tab, text="Submit", command=submit_question)
    submit_button.pack(pady=10)

    return question_tab

def create_third_tab(notebook, graph_tab, question_tab, graph):
    third_tab = ttk.Frame(notebook)
    notebook.add(third_tab, text="Document Permissions")

    documents_dir = "documents"
    checkboxes = []
    var_list = []

    # Add Global Permissions checkbox
    global_var = tk.IntVar()
    global_checkbox = tk.Checkbutton(third_tab, text="Global Permissions", variable=global_var)
    global_checkbox.pack(anchor='w', padx=20, pady=10)

    for filename in os.listdir(documents_dir):
        if filename.endswith(".txt"):
            var = tk.IntVar()
            checkbox = tk.Checkbutton(third_tab, text=filename, variable=var)
            checkbox.pack(anchor='w', padx=20, pady=5)
            checkboxes.append(checkbox)
            var_list.append(var)

    def save_permissions():
        permissions = set()
        if global_var.get() == 1:
            permissions.add(-1)
        permissions.update(i for i, var in enumerate(var_list) if var.get() == 1)
        if not permissions:
            permissions = {-1}  # If no checkboxes are selected, give full access
        graph_tab.permissions = permissions
        question_tab.permissions = permissions
        print(f"Permissions saved: {permissions}")
        
        # Update the graph with new permissions
        update_graph(graph_tab, graph, permissions)

    save_button = tk.Button(third_tab, text="Save Permissions", command=save_permissions)
    save_button.pack(pady=20)

    return third_tab

def update_graph(graph_tab, graph, permissions):
    if hasattr(graph_tab, 'canvas'):
        graph_tab.canvas.figure.clear()
        ax = graph_tab.canvas.figure.add_subplot(111)
        get_knowledge_graph(graph, None, permissions, ax)
        graph_tab.canvas.draw()
        print("Graph updated with new permissions")
    else:
        print("No canvas attribute found in graph_tab")

def visualize(graph: Dict[str, 'Node']):
    root = tk.Tk()
    root.title("Graph Visualization with Tabs")

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    graph_tab = create_graph_tab(notebook, graph)
    question_tab = create_question_tab(notebook, graph, graph_tab)
    third_tab = create_third_tab(notebook, graph_tab, question_tab, graph)

    close_button = tk.Button(root, text="Close", command=root.quit)
    close_button.pack(pady=10)

    root.mainloop()