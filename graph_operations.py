import random
import numpy as np
import networkx as nx
from tkinter import messagebox

class GraphOperations:
    def __init__(self):
        self.G = nx.Graph()

    #Function to add nodes to the graph 
    def add_node(self, node_value):
        try:
            self.G.add_node(node_value)
        except Exception as e:
            print(f"An error occurred while adding a node: {e}")
            
    #Function to delete node from the graph
    def delete_node(self, node_value):
        try:
            if node_value in self.G.nodes:
                self.G.remove_node(node_value)
            else:
                print(f"Node {node_value} not found in the graph.")
        except Exception as e:
            print(f"An error occurred while deleting a node: {e}")
            
    #Function to add edge between 2 nodes 
    def add_edge(self, edge_value1, edge_value2):
        try:
            if edge_value1 in self.G.nodes and edge_value2 in self.G.nodes:
                self.G.add_edge(edge_value1, edge_value2)
            else:
                print(f"One or both nodes ({edge_value1}, {edge_value2}) not found in the graph.")
        except Exception as e:
            print(f"An error occurred while adding an edge: {e}")
            
    #Function to delete edge between 2 nodes
    def delete_edge(self, edge_value1, edge_value2):
        try:
            if edge_value1 in self.G.nodes and edge_value2 in self.G.nodes:
                if self.G.has_edge(edge_value1, edge_value2):
                    self.G.remove_edge(edge_value1, edge_value2)
                else:
                    print(f"Edge ({edge_value1}, {edge_value2}) not found in the graph.")
            else:
                print(f"One or both nodes ({edge_value1}, {edge_value2}) not found in the graph.")
        except Exception as e:
            print(f"An error occurred while deleting an edge: {e}")
            
    #Function to print the graph 
    def print_graph(self):
        try:
            for edge in self.G.edges:
                print(edge)
        except Exception as e:
            print(f"An error occurred while printing the graph: {e}")


   
    #Start Backtracking algorithm 
    def solve_graph_backtracking(self, G, stop_event, time_limit_seconds):
        # Reset colors for all nodes to None
        for node in G.nodes:
            G.nodes[node]["color"] = None

        num_colors = 1
        result = self.color_graph_backtracking(G, num_colors, stop_event)

        # Increment the number of colors until a valid coloring is found
        while not result and not stop_event.is_set():
            num_colors += 1
            result = self.color_graph_backtracking(G, num_colors, stop_event)

        # If no valid coloring is found, display an error message
        if not result and not stop_event.is_set():
            messagebox.showinfo(
                "Error", "Graph cannot be colored with minimum colors.")

    def color_graph_backtracking(self, G, num_colors, stop_event):
        # Base case: If the stop event is set, return False
        if stop_event.is_set():
            return False

        # Iterate through all nodes
        for node in G.nodes:
            # If the node is not colored, try coloring it with each color from 1 to num_colors
            if G.nodes[node]["color"] is None:
                for color in range(1, num_colors + 1):
                    if self.is_safe(G, node, color):
                        # If it's safe to color the node with the current color, set the color
                        G.nodes[node]["color"] = color

                        # Recursively try to color the next node
                        if self.color_graph_backtracking(G, num_colors, stop_event):
                            return True  # If a valid coloring is found, return True

                        # If coloring the next node did not lead to a valid coloring, backtrack
                        G.nodes[node]["color"] = None  # Reset color

                # If no color is found for the current node, return False
                return False

        return True  # If all nodes are colored, return True

    def is_safe(self, G, node, color):
        # Check if the node is already colored with the current color
        if G.nodes[node].get("color") is not None:
            return False

        # Check if any neighboring node has the same color
        for neighbor in G.neighbors(node):
            if G.nodes[neighbor].get("color") == color:
                return False

        return True  # If it's safe to color the node with the current color, return True

    #End of Backtracking algorithm 
    
    
    #Start of genetic algorithm
def genetic_algorithm(adjacency_matrix, population_size, generations, mutation_rate):
    adjacency_list = adjacency_matrix.tolist()  # Convert matrix to nested list
    num_nodes = len(adjacency_list)

    def initialize_individual():
        return [random.randint(1, max_colors) for _ in range(num_nodes)]

    def calculate_fitness(individual):
        conflicts = 0
        for i in range(num_nodes):
            for j in range(num_nodes):
                if adjacency_list[i][j] and individual[i] == individual[j]:
                    conflicts += 1
        return conflicts

    def crossover(parent1, parent2):
        crossover_point = random.randint(1, num_nodes - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2

    def mutate(individual):
        if random.random() < mutation_rate:
            mutation_point = random.randint(0, num_nodes - 1)
            new_color = max(individual) + 1
            individual[mutation_point] = new_color

    # Convert each row to tuple
    max_colors = len(set(tuple(row) for row in adjacency_matrix.tolist()))
    population = [initialize_individual() for _ in range(population_size)]

    for generation in range(generations):
        fitness_scores = [calculate_fitness(
            individual) for individual in population]
        selected_indices = np.argsort(fitness_scores)[:2]
        parent1, parent2 = population[selected_indices[0]
                                      ], population[selected_indices[1]]

        child1, child2 = crossover(parent1, parent2)

        mutate(child1)
        mutate(child2)

        replace_indices = np.argsort(fitness_scores)[-2:]
        population[replace_indices[0]] = child1
        population[replace_indices[1]] = child2

    best_individual = population[np.argmin(fitness_scores)]
    return best_individual
    #End of genetic algorithm




