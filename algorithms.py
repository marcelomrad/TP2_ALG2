from __future__ import annotations
import numpy as np
import networkx as nx
from typing import List
from typing import Tuple
import heapq

import numpy.typing as npt

## Twice Around the Tree Algorithm ##

def twice_around_tree(graph: np.ndarray, start_node: int = 0) -> List[int]:
    graph_nx = nx.from_numpy_array(graph)

    mst = nx.minimum_spanning_tree(graph_nx)

    dfs_preorder = list(nx.dfs_preorder_nodes(mst, source=start_node))

    return dfs_preorder + [start_node]


### Christofides Algorithm ###

def christofides(graph: np.ndarray, start_node: int = 0) -> List[int]:

    graph_nx = nx.from_numpy_matrix(graph)

    mst = nx.minimum_spanning_tree(graph_nx)

    odd_degree_nodes = [node for node in mst.nodes if mst.degree[node] % 2 == 1]

    induced_subgraph = graph_nx.subgraph(odd_degree_nodes)

    min_weight_matching = nx.min_weight_matching(induced_subgraph, maxcardinality=True)

    eulerian_multigraph = nx.MultiGraph(mst)

    eulerian_multigraph.add_edges_from(min_weight_matching)

    eulerian_circuit = list(nx.eulerian_circuit(eulerian_multigraph))

    hamiltonian_cycle = []
    for u, _ in eulerian_circuit:
        if u not in hamiltonian_cycle:
            hamiltonian_cycle.append(u)

    return hamiltonian_cycle + [start_node]

###### BRANCH AND BOUND ######

NDArrayInt = npt.NDArray[np.int_]
NDArrayFloat = npt.NDArray[np.float_]

ArrayDeInteiros = np.ndarray
ArrayDeFloats = np.ndarray

class NoDeBusca:
    def __init__(self, limite: float, custo: float, caminho: ArrayDeInteiros, arestas_contadas: ArrayDeInteiros, tamanho_do_grafo: int):
        self.limite: float = limite
        self.custo: float = custo
        self.caminho: ArrayDeInteiros = caminho
        self.nivel: int = len(caminho)
        self.arestas_contadas: ArrayDeInteiros = arestas_contadas
        self.visitados: ArrayDeInteiros = np.zeros(tamanho_do_grafo, dtype=int)
        self.visitados[caminho] = 1
    
    def __lt__(self, outro: NoDeBusca) -> bool:
        return self.limite < outro.limite or (self.limite == outro.limite and self.custo < outro.custo)

def calcular_limite_do_grafo(grafo: ArrayDeInteiros) -> Tuple[float, ArrayDeInteiros]:
    total = 0
    arestas_contadas = np.zeros((len(grafo), 2), dtype=int) 
    for i in range(len(grafo)):
        duas_menores_arestas = np.partition(grafo[i], 2)[:2]
        arestas_contadas[i, :] = np.argsort(duas_menores_arestas)[:2]  
        total += sum(duas_menores_arestas)
    return total / 2, arestas_contadas


def atualizar_limite(limite_anterior: float, no_atual: int, novo_no: int, arestas_contadas: ArrayDeInteiros, grafo: ArrayDeFloats) -> Tuple[float, ArrayDeInteiros]:
    novo_limite = limite_anterior - (grafo[no_atual][arestas_contadas[no_atual][0]] + grafo[novo_no][arestas_contadas[novo_no][0]])
    novo_limite += grafo[no_atual][novo_no] + grafo[novo_no][no_atual]
    return novo_limite, arestas_contadas

def branch_and_bound(grafo: ArrayDeFloats) -> ArrayDeInteiros:
    limite_inicial, arestas_contadas = calcular_limite_do_grafo(grafo)
    raiz = NoDeBusca(limite_inicial, 0, np.array([0]), arestas_contadas, len(grafo))
    fila_de_prioridades = [raiz]
    heapq.heapify(fila_de_prioridades)
    melhor_custo = float("inf")
    melhor_caminho = np.array([])

    while fila_de_prioridades:
        no_atual = heapq.heappop(fila_de_prioridades)
        if no_atual.nivel == len(grafo):
            if melhor_custo > no_atual.custo:
                melhor_custo = no_atual.custo
                melhor_caminho = no_atual.caminho
        else:
            for proximo_no in range(1, len(grafo)):
                if not no_atual.visitados[proximo_no]:
                    novo_limite, novas_arestas_contadas = atualizar_limite(no_atual.limite, no_atual.caminho[-1], proximo_no, no_atual.arestas_contadas, grafo)
                    if novo_limite < melhor_custo:
                        novo_caminho = np.append(no_atual.caminho, proximo_no)
                        novo_no = NoDeBusca(novo_limite, no_atual.custo + grafo[no_atual.caminho[-1]][proximo_no], novo_caminho, novas_arestas_contadas, len(grafo))
                        heapq.heappush(fila_de_prioridades, novo_no)
    return melhor_caminho