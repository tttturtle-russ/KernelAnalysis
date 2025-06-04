import os
import networkx as nx
import pygraphviz as pgv

def load_dot_file(dot_file):
    """ Load a .dot file into a NetworkX graph while preserving node attributes. """
    graph = nx.DiGraph()
    ag = pgv.AGraph(string=open(dot_file).read())

    for node in ag.nodes():
        graph.add_node(node, **node.attr)  # Preserve attributes
    
    for edge in ag.edges():
        graph.add_edge(edge[0], edge[1])

    return graph

def load_call_graph(callgraph_dir):
    """ Load the callgraph from a .dot file in the specified directory. """
    call_graph = {}
    for filename in os.listdir(callgraph_dir):
        if filename.endswith(".dot"):
            callgraph_path = os.path.join(callgraph_dir, filename)
            graph = load_dot_file(callgraph_path)
            for node in graph.nodes:
                if graph.out_degree(node) > 0:  # If node calls other functions
                    call_graph[node] = [n for n in graph.neighbors(node)]
    return call_graph

def generate_inter_cfg(intra_cfg_dir, callgraph_dir):
    """ Generate the Inter-CFG from intra-CFGs and the Call Graph, preserving node attributes. """
    intra_cfgs = {}
    
    # Step 1: Load intra-CFGs
    for filename in os.listdir(intra_cfg_dir):
        if filename.endswith(".dot"):
            function_name = filename[1:-4]  # Strip . and .dot to get function name
            intra_cfg_path = os.path.join(intra_cfg_dir, filename)
            intra_cfgs[function_name] = load_dot_file(intra_cfg_path)

    # Step 2: Load the Call Graph
    call_graph = load_call_graph(callgraph_dir)

    # Step 3: Create the Inter-CFG
    inter_cfg = nx.DiGraph()

    # Step 4: Merge the intra-CFGs into the inter-CFG while preserving context
    for function_name, func_cfg in intra_cfgs.items():
        for node, attributes in func_cfg.nodes(data=True):  # Keep attributes
            inter_cfg.add_node(node, **attributes, function=function_name)  # Preserve function context
        inter_cfg.add_edges_from(func_cfg.edges)
        
        # Identify call sites and insert interprocedural edges
        for node in func_cfg.nodes:
            if "call_" in node:  # Call instruction
                callee_function = node.split("call_")[-1]  # Extract callee function name
                if callee_function in intra_cfgs:
                    # Link call site to function entry
                    inter_cfg.add_edge(node, f"{callee_function}_entry", label="call")
                    # Return edge from function exit to caller return site
                    inter_cfg.add_edge(f"{callee_function}_exit", f"{function_name}_return", label="return")

    # Step 5: Add call-return links based on the Call Graph
    for caller, callees in call_graph.items():
        for callee in callees:
            # Ensure functions exist in intra-CFGs before adding edges
            if caller in intra_cfgs and callee in intra_cfgs:
                inter_cfg.add_edge(f"{caller}_exit", f"{callee}_entry", label="call")

    return inter_cfg

def save_inter_cfg(inter_cfg, output_file):
    """ Save the Inter-CFG to a .dot file while keeping all node attributes. """
    with open(output_file, "w") as f:
        f.write("digraph InterCFG {\n")
        for node, attr in inter_cfg.nodes(data=True):
            attr_string = ", ".join(f'{key}="{value}"' for key, value in attr.items() if value)  # Format attributes
            f.write(f'    "{node}" [{attr_string}];\n')
        for u, v, attr in inter_cfg.edges(data=True):
            label = attr.get("label", "")
            f.write(f'    "{u}" -> "{v}" [label="{label}"];\n')
        f.write("}\n")


if __name__ == "__main__":
    # Set directories for intra-CFGs and the call graph
    intra_cfg_dir = "/home/qiaozhang/hidpath/intra-cfg"  # Path to the folder containing intra-CFG .dot files
    callgraph_dir = "/home/qiaozhang/hidpath/callgraph"  # Path to the folder containing the callgraph .dot files

    # Generate Inter-CFG
    inter_cfg = generate_inter_cfg(intra_cfg_dir, callgraph_dir)
    
    # Save the Inter-CFG to a .dot file
    save_inter_cfg(inter_cfg, "Newinter_cfg.dot")
    print("Inter-CFG generated and saved as 'inter_cfg.dot'.")
