import tsplib95
import networkx as nx
import numpy as np
import time
import sys
import psutil
from threading import Timer
from algorithms import twice_around_tree, christofides, branch_and_bound
from typing import List

def load_tsp_problem(file_path):
    # Carrega o problema TSP
    problem = tsplib95.load(file_path)

    # Converte para um grafo do NetworkX para facilitar a manipulação
    graph = problem.get_graph()

    return problem, graph

def get_process_memory():
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)  # Retorna o uso de memória em MB

def calculate_cycle_quality(graph: np.ndarray, cycle: List[int]) -> float:
    total_distance = 0
    for i in range(len(cycle) - 1):
        total_distance += graph[cycle[i], cycle[i + 1]]
    return total_distance

def timeout_handler():
    print("Tempo limite excedido (30 minutos). Execução abortada.")
    sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Uso: python main.py [caminho_para_o_arquivo.tsp] [algoritmo]")
        print("Algoritmos: twice, christofides")
        sys.exit(1)

    file_path = sys.argv[1]
    algorithm = int(sys.argv[2])

    problem, graph = load_tsp_problem(file_path)
    adjacency_matrix = nx.to_numpy_array(graph)

    # Define um temporizador para 30 minutos
    timer = Timer(1800, timeout_handler)
    timer.start()

    initial_memory = get_process_memory()
    start_time = time.time()

    try:
        if algorithm == 1:
            hamiltonian_cycle = twice_around_tree(adjacency_matrix, start_node=0)
        elif algorithm == 2:
            hamiltonian_cycle = christofides(adjacency_matrix, start_node=0)
        elif algorithm == 3:
            hamiltonian_cycle = branch_and_bound(adjacency_matrix)
        else:
            print("Algoritmo não reconhecido.")
            sys.exit(1)
    finally:
        timer.cancel()

    end_time = time.time()
    final_memory = get_process_memory()

    execution_time = end_time - start_time
    memory_used = final_memory - initial_memory
    cycle_quality = calculate_cycle_quality(adjacency_matrix, hamiltonian_cycle)

    print(f"Tempo de execução: {execution_time} segundos")
    print(f"Uso de memória: {memory_used} MB")
    print(f"Qualidade da solução (distância total): {cycle_quality}")

if __name__ == "__main__":
    main()