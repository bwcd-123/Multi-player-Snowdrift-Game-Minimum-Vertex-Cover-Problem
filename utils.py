import networkx as nx
import random
import copy
import io
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


default_nodes = [i for i in range(1, 11)]
default_edges = [
    (1, 2), (2, 3), (3, 4), (4, 5), (1, 5),
    (1, 6), (2, 7), (3, 8), (4, 9), (5, 10),
    (6, 7), (7, 8), (8, 9), (9, 10), (6, 10)
]
unite_color = 'red'
defect_color = 'blue'


def init_graph(nodes=default_nodes, edges=default_edges):
    """
    Initialize a graph with the given nodes and edges.
    
    Args:
        nodes: list
            List of nodes. Default is [1, 2, ..., 10]
        edges: list
            List of edges. Default is [(1, 2), (3, 9), ..., (10, 1)]
            
    Returns:
        G: networkx.Graph
            The initialized graph.
            
        pos: dict
    """
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    pos = nx.spring_layout(G)

    for node, _ in G.nodes(data=True):
        G.nodes[node]['cooperate']= random.choice([True, False])
        G.nodes[node]['color'] = unite_color if G.nodes[node]['cooperate'] else defect_color
    return G, pos


def show_graph(G, pos, title='Graph'):
    """
    Show the graph using matplotlib.
    
    Args:
        G: networkx.Graph
            The graph to be shown.
            
        pos: dict
            The position of the nodes.
            
        title: str
            The title of the graph. Default is 'Graph'.
            
    Returns:
        buffered: io.BytesIO
            The image of the graph.
    """
    colors = [G.nodes[node]['color'] for node in G.nodes]

    # use draw function of NetworkX to draw the graph
    nx.draw(G, pos, node_color=colors)
    
    plt.title(title)
    legend_elements = [Line2D([0], [0], color=unite_color, lw=4, label='Cooperator'),
                    Line2D([0], [0], color=defect_color, lw=4, label='Defector')]
    plt.legend(handles=legend_elements)
    plt.show()


def get_graph(G, pos):
    """
    get the graph buffer.
    
    Args:
        G: networkx.Graph
            The graph to be saved.
            
        pos: dict
            The position of the nodes.
            
    Returns:
        buffered: io.BytesIO
            The image of the graph.
    """
    colors = [G.nodes[node]['color'] for node in G.nodes]

    # use draw function of NetworkX to draw the graph
    nx.draw(G, pos, node_color=colors)
    
    legend_elements = [Line2D([0], [0], color=unite_color, lw=4, label='Cooperator'),
                    Line2D([0], [0], color=defect_color, lw=4, label='Defector')]
    plt.legend(handles=legend_elements)

    # save the image to a buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='PNG')
    plt.close()

    return buffer


def compute_update(G, r):
    """
    Compute the reward for each node in the graph.
        And update the state of these nodes.
    
    Args:
        G: networkx.Graph
            The graph to be updated.
            
        r: float
            The cost of coorperate.
            
    Returns:
        G: networkx.Graph
            The updated graph.
        
        stable: bool
            Whether the graph is stable.
    """
    stable = True
    graph = G.copy()
    for node in graph.nodes():
        # get the neighbors of the current node
        neighbors = graph.neighbors(node)
        # count the number of cooperators and defectors in the neighbors
        cooperators = 0.0
        defectors = 0.0
        
        for neighbor in neighbors:
            if graph.nodes[neighbor]['cooperate']:
                cooperators += 1
            else:
                defectors += 1
        
        # compute the rewards for the current node of both state
        reward_cooperate = 1 * cooperators + (1 - r) * defectors
        reward_defect = (1 + r) * cooperators + 0 * defectors

        # update the state of the current node, and judge that the graph doesn't change
        new_state = True if reward_cooperate > reward_defect else False
        if graph.nodes[node]['cooperate'] != new_state:
            stable = False
            graph.nodes[node]['cooperate'] = new_state
            graph.nodes[node]['color'] = unite_color if graph.nodes[node]['cooperate'] else defect_color
        
    return graph, stable


def run_game(graph, pos, r_list, max_epoch):
    """
    Run the game for a given graph.
        and it will compute the final graphs for different rewards.
    
    Args:
        graph: networkx.Graph
            The graph to be updated.
            
        pos: dict
            The position of each node in the graph.
            
        r_list: list[float]
            The costs of coorperate.
            
        max_epoch: int
            The maximum number of epochs.
            
    Returns:
        final_images: [matplotlib.image.AxesImage]
            The images of the final graphs.
            
    """
    final_images = []
    mncs = []
    for r in r_list:
        # initial_graph = graph.copy()
        print("running game with r =", r)
        final_graph, stable = compute_update(graph, r)
        for i in range(max_epoch):
            # show_graph(initial_graph, pos, title='init')
            if stable:
                print(f"graph is stable at epoch {i}\n")
                final_image = get_graph(final_graph, pos)
                is_mnc = judge_MNC(final_graph)
                break
            final_graph, stable = compute_update(final_graph, r)

        if not stable:
            print('the graph is not stable\n')
            is_mnc = judge_MNC(final_graph)
            final_image = get_graph(final_graph, pos)
    
        final_images.append(final_image)
        mncs.append(is_mnc)

    return final_images, mncs


def judge_MNC(graph):
    """
    Judge whether the graph is a Minimum Node Cover.（极小节点覆盖）
    
    Args:
        graph: networkx.Graph
            The graph to be updated.
            
    Returns:
        is_MNC: bool
            Whether the graph is a Minimum Node Cover.
            
    """
    is_MNC = True
    for u, v in graph.edges():
        if graph.nodes[u]['cooperate'] == False and graph.nodes[v]['cooperate'] == False:
            is_MNC = False
            break
        
    return is_MNC