import networkx as nx
import re

# Step 1: Parse the DOT file
def parse_dot(dot_file):
    G = nx.DiGraph()
    
    with open(dot_file, 'r') as f:
        lines = f.readlines()
        
        # Parse nodes and edges
        for line in lines:
            # Remove extra spaces and handle empty lines
            line = line.strip()
            
            if '->' in line:  # Handle edges
                match = re.match(r'(\S+)\s*->\s*(\S+)', line)
                if match:
                    from_node = match.group(1)
                    to_node = match.group(2)
                    G.add_edge(from_node, to_node)
            
            elif '[shape=record' in line:  # Handle nodes (we can ignore actual labels)
                match = re.match(r'(\S+)\s*\[shape=record, label="\{.*\}"]', line)
                if match:
                    node = match.group(1)
                    G.add_node(node)
                    
    return G

# Step 2: Find all paths using DFS from init_node to target_node (node A)
def find_paths(graph, start_node, target_node):
    all_paths = []
    
    # Depth First Search (DFS) with path tracking
    def dfs(current_node, path):
        if current_node == target_node:
            all_paths.append(path)
            return
        
        for neighbor in graph.neighbors(current_node):
            if neighbor not in path:  # To avoid cycles
                dfs(neighbor, path + [neighbor])
    
    # Start DFS from the initial node
    dfs(start_node, [start_node])
    
    return all_paths

# Step 3: Write the result to a text file
def write_paths_to_file(all_paths, output_file):
    with open(output_file, 'w') as f:
        if not all_paths:
            f.write("No paths found\n")
        else:
            for idx, path in enumerate(all_paths, 1):
                f.write(f"Path {idx}: {path}\n")

# Main function to process the graph and find paths
def main(dot_file, init_node, target_node, output_file):
    # Parse the DOT file to create a graph
    graph = parse_dot(dot_file)
    
    # Find all paths from the init node to the target node
    all_paths = find_paths(graph, init_node, target_node)
    
    # Write the formatted paths to a file
    write_paths_to_file(all_paths, output_file)

# Example usage
if __name__ == "__main__":
    # Specify the path to your DOT file, init node, target node, and output file
    dot_file = './inter_cfg.dot'
    init_node = 'Node0x55b11a499610'  # Example init node
    #target_node = 'Node0x55dc7fd1a880'   # i8253.c -> 204
    target_node = 'Node0x55dc7fd1a910' # i8253.c -> 210
    output_file = './output_paths.txt'  # Output file where paths will be saved
    
    # Run the main function
    main(dot_file, init_node, target_node, output_file)

