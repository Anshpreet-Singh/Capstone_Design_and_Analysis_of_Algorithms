# Capstone_Design_and_Analysis_of_Algorithms
# Mini-Courier Planner

A small Python project for the Design & Analysis of Algorithms capstone assignment. It combines four algorithms in one courier-planning example:

1. **Merge Sort** - sorts parcels by earliest delivery deadline. If two parcels have the same deadline, the parcel with higher priority comes first.
2. **0/1 Knapsack using Dynamic Programming** - chooses the most valuable group of parcels that fits in the vehicle.
3. **Dijkstra's Algorithm** - finds shortest road distances in the delivery map.
4. **Nearest Neighbor TSP Approximation** - visits the nearest unvisited delivery point and finally returns to the depot.

## 1. Files in this project

- `Mini_Courier_Planner_Report.docx` - report covering all five assignment phases. Fill in your name and roll number before submission.
- `mini_courier_planner.py` - complete Python program.
- `sample_data.json` - sample parcels, vehicle capacity and road distances.
- `test_planner.py` - simple automatic correctness tests.
- `benchmark_results.csv` - runtime measurements for 10, 20, 40 and 80 parcels.
- `runtime_chart.png` - graph showing how runtime changes as input size increases.
- `sample_run_output.txt` - example output of the main program.
- `benchmark_output.txt` - example output of the performance test.
- `requirements.txt` - optional package needed for the runtime chart.

## 2. How to run the project

Open a terminal in this folder.

Run the main courier planner:

```bash
python mini_courier_planner.py
```

Run the performance tests and create the runtime chart:

```bash
python mini_courier_planner.py --benchmark
```

Run the correctness tests:

```bash
python -m unittest test_planner.py
```

If Matplotlib is not installed, install it with:

```bash
python -m pip install -r requirements.txt
```

The main program uses only Python's standard library. Matplotlib is required only to create the chart.

## 3. Sample input

The sample vehicle capacity is **12 kg**. Every parcel has an ID, destination, weight, deadline, priority and value. The map is stored as road edges. For example, `['DEPOT', 'A', 4]` means the road between the depot and location A is 4 km. Roads are treated as two-way roads.

## 4. Sample result

The program sorts the parcels in this order:

`P104, P102, P106, P101, P103, P105`

The Dynamic Programming solution selects:

`P104, P102, P106, P101`

Their combined weight is **12 kg**, and their combined value is **325**.

The nearest-neighbor delivery route is:

`DEPOT -> D -> B -> F -> A -> DEPOT`

The total route distance is **19 km** for the sample map.

## 5. Simple explanation of the program

- First, Merge Sort arranges parcels so urgent parcels appear earlier.
- Next, Knapsack DP checks possible parcel combinations and chooses the highest-value combination that does not exceed 12 kg.
- Dijkstra calculates the shortest road distance from one location to the other locations.
- Nearest Neighbor repeatedly chooses the closest delivery point that has not yet been visited. It returns to the depot after the last delivery.
- The benchmark mode repeats the same work with larger generated datasets and records the time taken.

## 6. Important note

Nearest Neighbor is an **approximation**. It gives a practical route quickly, but it does not guarantee the mathematically shortest possible full tour. Runtime values depend on the computer and may differ slightly when the project is run again.
