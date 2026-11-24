"""Basic correctness checks for the Mini-Courier Planner."""
import unittest

from mini_courier_planner import (
    build_graph,
    dijkstra,
    knapsack_dp,
    load_sample_data,
    merge_sort_parcels,
    nearest_neighbor_route,
)


class MiniCourierPlannerTests(unittest.TestCase):
    def setUp(self):
        self.data = load_sample_data()
        self.parcels = self.data["parcels"]
        self.sorted_parcels = merge_sort_parcels(self.parcels)
        nodes = [self.data["depot"]] + [p["destination"] for p in self.parcels]
        self.graph = build_graph(self.data["edges"], nodes)

    def test_merge_sort_deadline_order(self):
        deadlines = [p["deadline_days"] for p in self.sorted_parcels]
        self.assertEqual(deadlines, sorted(deadlines))

    def test_knapsack_stays_within_capacity(self):
        selected, value = knapsack_dp(self.sorted_parcels, self.data["capacity_kg"])
        total_weight = sum(p["weight_kg"] for p in selected)
        self.assertLessEqual(total_weight, self.data["capacity_kg"])
        self.assertEqual(value, 325)

    def test_dijkstra_shortest_distance(self):
        distances, _ = dijkstra(self.graph, "DEPOT")
        self.assertEqual(distances["D"], 3)
        self.assertEqual(distances["A"], 4)

    def test_route_visits_selected_destinations(self):
        selected, _ = knapsack_dp(self.sorted_parcels, self.data["capacity_kg"])
        locations = [p["destination"] for p in selected]
        route, distance = nearest_neighbor_route(self.graph, "DEPOT", locations)
        self.assertEqual(route[0], "DEPOT")
        self.assertEqual(route[-1], "DEPOT")
        self.assertEqual(set(route[1:-1]), set(locations))
        self.assertEqual(len(route[1:-1]), len(set(locations)))
        self.assertEqual(distance, 19)


if __name__ == "__main__":
    unittest.main()
