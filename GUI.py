# Import necessary modules and libraries
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
from graph_operations import GraphOperations, genetic_algorithm
import time

# Define the main application class
class GraphColoringApp:
        
    def __init__(self, master):
        # Initialize the GraphOperations class for graph-related operations
        self.graph_operations = GraphOperations()
        # Variable to signal stopping conditions for background processes
        self.stop_event = None
        # Reference to the main Tkinter window
        self.master = master
        self.master.title("Graph Coloring App")
        # Create and pack a frame for user interface elements
        frame = ttk.Frame(self.master)
        frame.pack(pady=20)
        # Entry widget for the number of nodes in the graph
        self.num_nodes_entry = ttk.Entry(frame, width=5, font=('Arial', 14))
        self.num_nodes_entry.insert(0, "2")
        self.num_nodes_entry.pack(side=tk.LEFT, padx=10)
        
        # Entry widget for the number of edges in the graph
        self.num_edges_entry = ttk.Entry(frame, width=5, font=('Arial', 14))
        self.num_edges_entry.insert(0, "1")
        self.num_edges_entry.pack(side=tk.LEFT, padx=10)
        
         # Text widget for specifying edge connections in the graph
        self.edge_connections_text = scrolledtext.ScrolledText(
            frame, width=20, height=5, wrap=tk.WORD)
        self.edge_connections_text.pack(side=tk.LEFT, padx=10, pady=10)
        
         # Radio buttons for selecting the algorithm (Backtracking or Genetic Algorithm)
        self.algorithm_choice = tk.StringVar(value="Backtracking")
        backtracking_radio = tk.Radiobutton(frame, text="Backtracking", variable=self.algorithm_choice,
                                            value="Backtracking", font=('Arial', 14))
        backtracking_radio.pack(side=tk.LEFT, padx=10)

        genetic_radio = tk.Radiobutton(frame, text="Genetic Algorithm", variable=self.algorithm_choice,
                                       value="Genetic Algorithm", font=('Arial', 14))
        genetic_radio.pack(side=tk.LEFT, padx=10)
        
        # Button to create and solve the graph based on user input
        solve_button = ttk.Button(
            frame, text="Create and Solve", command=self.create_and_solve_graph, style='TButton')
        solve_button.pack(side=tk.BOTTOM, pady=20)

        # Label to display the time taken for the algorithm to run
        self.time_label = ttk.Label(
            self.master, text="Time: ", font=('Arial', 14))
        self.time_label.pack(side=tk.BOTTOM)
 
        # Canvas for displaying the graph plot
        self.canvas = None
   
   
    # Method to create and solve the graph based on user input and choices
    def create_and_solve_graph(self):
        try:
             # Extract numerical values for the number of nodes and edges the user entered
            num_nodes = int(self.num_nodes_entry.get())
            num_edges = int(self.num_edges_entry.get())
            
             # Calculate the maximum number of edges for a complete graph
            max_edges = (num_nodes * (num_nodes - 1)) // 2
            
             # Check if the number of edges exceeds the maximum allowed
            if num_edges > max_edges:
                messagebox.showerror(
                    "Error", f"Maximum number of edges for a complete graph is {max_edges}")
                return
        except ValueError:
             # Display an error message if the input values are not valid numbers
            messagebox.showerror(
                "Error", "Please enter valid numerical values for nodes and edges.")
            return

        # Clear existing graph
        self.graph_operations.G.clear()

        # Add nodes to the graph
        for node in range(1, num_nodes + 1):
            self.graph_operations.add_node(node)

        # Add edges based on user input 
        #The text is extracted from the beginning to the end
        edge_connections = self.edge_connections_text.get(
            "1.0", tk.END).strip() 
        try:
            #assume that every line has new edge connection 
            for edge in edge_connections.split('\n'):
                # Parse and add edges to the graph
                v1, v2 = map(int, edge.split(','))
                self.graph_operations.add_edge(v1, v2)
        except ValueError:
            # Display an error message if the edge connections are not valid
            messagebox.showerror(
                "Error", "Please enter valid edge connections.")
            return
        
         # Create a subplot for displaying the graph
        self.fig, self.ax = plt.subplots()

        if self.algorithm_choice.get() == "Backtracking":
            # Set a reasonable time limit 
            time_limit_seconds = 5
            start_time = time.time()
            self.run_backtracking_with_timeout(time_limit_seconds)
            end_time = time.time()
            #show the time algorithm spend on solving the problem
            self.time_label.config(
            text=f"Backtracking Time: {end_time - start_time:.4f} seconds")
        elif self.algorithm_choice.get() == "Genetic Algorithm":
            start_time = time.time()
            self.solve_graph_genetic()
            end_time = time.time()
            #show the time algorithm spend on solving the problem
            self.time_label.config(
            text=f"Genetic Algorithm Time: {end_time - start_time:.4f} seconds")

        self.display_result()
        
        
        
    def run_backtracking_with_timeout(self, time_limit_seconds):
        # Create a threading.Event to signal the backtracking thread to stop
        stop_event = threading.Event()

        # Run the backtracking algorithm in a separate thread
        backtracking_thread = threading.Thread(
            target=self.graph_operations.solve_graph_backtracking,
            args=(self.graph_operations.G, stop_event, time_limit_seconds)
        )
        backtracking_thread.start()

        # Wait for the specified time limit
        backtracking_thread.join(timeout=time_limit_seconds)

        # Check if the thread is still alive (not completed within the time limit)
        if backtracking_thread.is_alive():
            # Set the stop event to signal the thread to stop
            stop_event.set()
            backtracking_thread.join()  # Wait for the thread to stop

            messagebox.showinfo(
                "Error", "Backtracking algorithm exceeded time limit."
            )
            

    def solve_graph_genetic(self):
        # Parameters for the genetic algorithm
        num_colors = 1
        population_size = 50
        generations = 1000
        mutation_rate = 0.01
        
        # Extract the adjacency matrix of the graph and convert it to numpy matrix 
        adjacency_matrix = nx.adjacency_matrix(self.graph_operations.G).todense()
        
        # Retrieve current colors assigned to nodes (if any)
        current_colors = [self.graph_operations.G.nodes[n].get(
            "color", None) for n in self.graph_operations.G.nodes]
        
        # Run the genetic algorithm to find a valid coloring
        result_genetic = genetic_algorithm(
            adjacency_matrix, population_size, generations, mutation_rate)

        # Check if the result is valid and has the correct number of colors
        if not result_genetic or len(result_genetic) != len(self.graph_operations.G.nodes):
            messagebox.showinfo(
                "Error", "Graph cannot be colored with minimum colors.")
        else:
             # Process the result and assign unique colors to nodes
            unique_colors = list(set(result_genetic))
            color_mapping = {old_color: new_color for old_color, new_color in zip(
                unique_colors, range(1, len(unique_colors) + 1))}

            # Assign colors to nodes, even if they have no edges
            for i, node in enumerate(self.graph_operations.G.nodes):
                self.graph_operations.G.nodes[node]["color"] = color_mapping.get(
                    result_genetic[i], None)

    def display_result(self):
        # Clear the existing content in the matplotlib subplot
        self.ax.clear()

        # Create a circular layout for the graph using networkx
        pos = nx.circular_layout(self.graph_operations.G)

        # Extract the colors assigned to each node from the graph
        node_colors = [self.graph_operations.G.nodes[n].get(
            "color", None) for n in self.graph_operations.G.nodes]

        try:
            #Check if any color is none (any node is not colored)
            if any(color is not None for color in node_colors):
                # Draw the entire graph with labels, node colors, and a color map using matplotlib
                nx.draw(self.graph_operations.G, pos, with_labels=True, node_color=node_colors,
                        cmap=plt.cm.rainbow, ax=self.ax,
                        vmin=min(color for color in node_colors if color is not None),
                        vmax=max(color for color in node_colors if color is not None))
            else:
                # Show a message if there are no nodes with colors to display
                messagebox.showinfo("Info", "No nodes with colors to display.")
        except Exception as e:
            # Print the error details
            print(f"An error occurred during graph display: {e}")

        # If a previous canvas exists, destroy it to update the displayed graph
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Create a new Tkinter canvas for the updated graph using FigureCanvasTkAgg
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)

        # Pack the canvas to the top of the Tkinter window, filling both X and Y directions
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Draw the updated canvas
        self.canvas.draw()


if __name__ == "__main__":
    #Creates the main window
    root = tk.Tk()
    #creates  object that represents our graph coloring application.
    app = GraphColoringApp(root)
    #make our app ready to respond user actions 
    root.mainloop()
