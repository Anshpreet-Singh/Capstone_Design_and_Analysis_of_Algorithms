"""Mini-Courier Planner: sorting, knapsack, Dijkstra and nearest-neighbor TSP.

Run the sample project:
    python mini_courier_planner.py

Run the performance tests and create a chart:
    python mini_courier_planner.py --benchmark
"""

import argparse
import csv
import json
import random
import time
from heapq import heappop, heappush
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def load_sample_data():
    """Read parcels, road edges and vehicle capacity from sample_data.json."""
    file_path = BASE_DIR / "sample_data.json"
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def merge_sort_parcels(parcels):
    """Sort by earliest deadline first, then by higher priority."""
    if len(parcels) <= 1:
        return parcels[:]

    middle = len(parcels) // 2
    left = merge_sort_parcels(parcels[:middle])
    right = merge_sort_parcels(parcels[middle:])
    sorted_list = []
    i = j = 0

    while i < len(left) and j < len(right):
        left_key = (left[i]["deadline_days"], -left[i]["priority"])
        right_key = (right[j]["deadline_days"], -right[j]["priority"])
        if left_key <= right_key:
            sorted_list.append(left[i])
            i += 1
        else:
            sorted_list.append(right[j])
            j += 1

    sorted_list.extend(left[i:])
    sorted_list.extend(right[j:])
    return sorted_list


def knapsack_dp(parcels, capacity_kg):
    """Choose the highest-value combination that fits in the vehicle."""
    number_of_parcels = len(parcels)
    dp = [[0] * (capacity_kg + 1) for _ in range(number_of_parcels + 1)]

    for i in range(1, number_of_parcels + 1):
        weight = parcels[i - 1]["weight_kg"]
        value = parcels[i - 1]["value"]
        for capacity in range(capacity_kg + 1):
            dp[i][capacity] = dp[i - 1][capacity]
            if weight <= capacity:
                take_value = value + dp[i - 1][capacity - weight]
                dp[i][capacity] = max(dp[i][capacity], take_value)

    # Move backwards through the DP table to find which parcels were selected.
    selected = []
    remaining_capacity = capacity_kg
    for i in range(number_of_parcels, 0, -1):
        if dp[i][remaining_capacity] != dp[i - 1][remaining_capacity]:
            parcel = parcels[i - 1]
            selected.append(parcel)
            remaining_capacity -= parcel["weight_kg"]

    selected.reverse()
    return selected, dp[number_of_parcels][capacity_kg]


def build_graph(edges, nodes):
    """Create an undirected weighted graph using an adjacency list."""
    graph = {node: [] for node in nodes}
    for start, end, distance in edges:
        graph[start].append((end, distance))
        graph[end].append((start, distance))
    return graph


def dijkstra(graph, start):
    """Find shortest distances from start to every reachable graph node."""
    distances = {node: float("inf") for node in graph}
    previous = {node: None for node in graph}
    distances[start] = 0
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_node = heappop(priority_queue)
        if current_distance > distances[current_node]:
            continue

        for neighbour, road_distance in graph[current_node]:
            new_distance = current_distance + road_distance
            if new_distance < distances[neighbour]:
                distances[neighbour] = new_distance
                previous[neighbour] = current_node
                heappush(priority_queue, (new_distance, neighbour))

    return distances, previous


def nearest_neighbor_route(graph, depot, delivery_locations):
    """Build a quick delivery tour by repeatedly visiting the nearest stop."""
    # Keep the original order for predictable tie-breaking and remove duplicates.
    delivery_locations = list(dict.fromkeys(delivery_locations))
    unvisited = set(delivery_locations)
    route = [depot]
    total_distance = 0
    current = depot

    while unvisited:
        distances, _ = dijkstra(graph, current)
        reachable = [location for location in delivery_locations
                     if location in unvisited and distances[location] != float("inf")]
        if not reachable:
            raise ValueError("Some delivery points cannot be reached from the current location.")

        next_stop = min(reachable, key=lambda location: distances[location])
        total_distance += distances[next_stop]
        route.append(next_stop)
        unvisited.remove(next_stop)
        current = next_stop

    # Return to the depot after the final delivery.
    distances, _ = dijkstra(graph, current)
    if distances[depot] == float("inf"):
        raise ValueError("The depot cannot be reached from the final delivery point.")
    total_distance += distances[depot]
    route.append(depot)
    return route, total_distance


def run_sample():
    data = load_sample_data()
    parcels = data["parcels"]
    capacity = data["capacity_kg"]
    depot = data["depot"]
    nodes = [depot] + [parcel["destination"] for parcel in parcels]
    graph = build_graph(data["edges"], nodes)

    print("=" * 62)
    print("                 MINI-COURIER PLANNER")
    print("=" * 62)
    print(f"Vehicle carrying capacity: {capacity} kg\n")

    start = time.perf_counter()
    sorted_parcels = merge_sort_parcels(parcels)
    sorting_time = time.perf_counter() - start

    print("1. PARCELS SORTED (deadline first, then priority)")
    for parcel in sorted_parcels:
        print(f"   {parcel['id']} | Destination {parcel['destination']} | "
              f"Deadline: {parcel['deadline_days']} days | Priority: {parcel['priority']}")

    start = time.perf_counter()
    selected, total_value = knapsack_dp(sorted_parcels, capacity)
    knapsack_time = time.perf_counter() - start
    total_weight = sum(parcel["weight_kg"] for parcel in selected)

    print("\n2. OPTIMAL PARCELS SELECTED (0/1 Knapsack DP)")
    for parcel in selected:
        print(f"   {parcel['id']} -> {parcel['destination']} | "
              f"Weight: {parcel['weight_kg']} kg | Value: {parcel['value']}")
    print(f"   Total weight: {total_weight}/{capacity} kg")
    print(f"   Total value: {total_value}")

    start = time.perf_counter()
    depot_distances, _ = dijkstra(graph, depot)
    dijkstra_time = time.perf_counter() - start
    print("\n3. SHORTEST DISTANCES FROM DEPOT (Dijkstra)")
    for parcel in parcels:
        destination = parcel["destination"]
        print(f"   DEPOT to {destination}: {depot_distances[destination]} km")

    destinations = [parcel["destination"] for parcel in selected]
    start = time.perf_counter()
    route, route_distance = nearest_neighbor_route(graph, depot, destinations)
    route_time = time.perf_counter() - start

    print("\n4. APPROXIMATE DELIVERY ROUTE (Nearest Neighbor TSP)")
    print("   " + " -> ".join(route))
    print(f"   Total route distance: {route_distance} km")

    print("\n5. RUNTIME OF MAIN STEPS")
    print(f"   Merge sort:             {sorting_time * 1000:.4f} ms")
    print(f"   Knapsack DP:            {knapsack_time * 1000:.4f} ms")
    print(f"   One Dijkstra run:       {dijkstra_time * 1000:.4f} ms")
    print(f"   Nearest-neighbor route: {route_time * 1000:.4f} ms")
    print("\nNote: Runtime changes depending on the computer and input size.")
    print("=" * 62)


def generate_test_data(number_of_parcels, seed=42):
    """Create repeatable test data for performance measurement."""
    rng = random.Random(seed + number_of_parcels)
    parcels = []
    nodes = ["DEPOT"]
    for number in range(1, number_of_parcels + 1):
        destination = f"C{number}"
        nodes.append(destination)
        parcels.append({
            "id": f"P{number}",
            "destination": destination,
            "weight_kg": rng.randint(1, 5),
            "deadline_days": rng.randint(1, 60),
            "priority": rng.randint(1, 5),
            "value": rng.randint(20, 150)
        })

    # A connected, undirected test road network (one road between every pair).
    edges = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            edges.append([nodes[i], nodes[j], rng.randint(1, 20)])

    graph = build_graph(edges, nodes)
    capacity = max(1, sum(parcel["weight_kg"] for parcel in parcels) // 2)
    return parcels, graph, capacity


def measure_average_ms(function, repeats=7, loops=3):
    """Measure an operation several times to reduce timing noise."""
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        for _ in range(loops):
            function()
        samples.append((time.perf_counter() - start) / loops)
    return (sum(samples) / len(samples)) * 1000


def run_benchmark():
    sizes = [10, 20, 40, 80]
    results = []

    print("Running performance tests. Please wait for the results...\n")
    for size in sizes:
        parcels, graph, capacity = generate_test_data(size)
        sorted_parcels = merge_sort_parcels(parcels)
        selected, _ = knapsack_dp(sorted_parcels, capacity)
        destinations = [parcel["destination"] for parcel in selected]

        sort_ms = measure_average_ms(lambda: merge_sort_parcels(parcels))
        knapsack_ms = measure_average_ms(lambda: knapsack_dp(sorted_parcels, capacity))
        dijkstra_ms = measure_average_ms(lambda: dijkstra(graph, "DEPOT"))
        route_ms = measure_average_ms(
            lambda: nearest_neighbor_route(graph, "DEPOT", destinations)
        )

        def complete_planner():
            ordered = merge_sort_parcels(parcels)
            chosen, _ = knapsack_dp(ordered, capacity)
            dijkstra(graph, "DEPOT")
            nearest_neighbor_route(
                graph, "DEPOT", [parcel["destination"] for parcel in chosen]
            )

        total_ms = measure_average_ms(complete_planner)
        results.append({
            "parcels": size,
            "merge_sort_ms": sort_ms,
            "knapsack_dp_ms": knapsack_ms,
            "dijkstra_one_run_ms": dijkstra_ms,
            "nearest_neighbor_route_ms": route_ms,
            "complete_planner_ms": total_ms
        })
        print(f"{size:>3} parcels | complete planner: {total_ms:.4f} ms")

    csv_path = BASE_DIR / "benchmark_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    chart_path = BASE_DIR / "runtime_chart.png"
    try:
        import matplotlib.pyplot as plt

        x_values = [row["parcels"] for row in results]
        plt.figure(figsize=(9, 5.5))
        plt.plot(x_values, [row["merge_sort_ms"] for row in results], marker="o", label="Merge sort")
        plt.plot(x_values, [row["knapsack_dp_ms"] for row in results], marker="o", label="Knapsack DP")
        plt.plot(x_values, [row["dijkstra_one_run_ms"] for row in results], marker="o", label="Dijkstra (one run)")
        plt.plot(x_values, [row["nearest_neighbor_route_ms"] for row in results], marker="o", label="Nearest-neighbor route")
        plt.plot(x_values, [row["complete_planner_ms"] for row in results], marker="o", linewidth=2.5, label="Complete planner")
        plt.xlabel("Number of parcels / delivery points")
        plt.ylabel("Average runtime (milliseconds)")
        plt.title("Mini-Courier Planner: Runtime Comparison")
        plt.xticks(x_values)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(chart_path, dpi=180)
        plt.close()
        print(f"\nRuntime chart saved to: {chart_path.name}")
    except ImportError:
        print("\nMatplotlib is not installed, so the chart was not created.")
        print("Install it with: python -m pip install matplotlib")

    print(f"Benchmark table saved to: {csv_path.name}")
    print("\nBenchmark summary (milliseconds):")
    for row in results:
        print(f"{row['parcels']:>3} parcels: "
              f"sort={row['merge_sort_ms']:.4f}, "
              f"knapsack={row['knapsack_dp_ms']:.4f}, "
              f"Dijkstra={row['dijkstra_one_run_ms']:.4f}, "
              f"route={row['nearest_neighbor_route_ms']:.4f}, "
              f"total={row['complete_planner_ms']:.4f}")


def main():
    parser = argparse.ArgumentParser(description="Mini-Courier Planner")
    parser.add_argument(
        "--benchmark", action="store_true",
        help="test larger datasets and create a runtime chart"
    )
    args = parser.parse_args()

    if args.benchmark:
        run_benchmark()
    else:
        run_sample()


if __name__ == "__main__":
    main()
