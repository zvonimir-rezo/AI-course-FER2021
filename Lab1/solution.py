import sys
import heapq

## NODE CLASS
from queue import PriorityQueue


class Node:
    def __init__(self, name, parent, cost):
        self.name = name
        self.parent = parent
        self.cost = cost
        if cost == 0 or parent is None:
            self.total_cost = 0
        else:
            self.total_cost = parent.total_cost + cost

    def __lt__(self, other):
        if self.total_cost == other.total_cost:
            return self.name < other.name
        return self.total_cost < other.total_cost

    def __gt__(self, other):
        if self.total_cost == other.total_cost:
            return self.name > other.name
        return self.total_cost > other.total_cost


## HEURISTIC NODE
class HeuristicNode(Node):
    def __init__(self, name, parent, cost, heuristic_cost):
        super().__init__(name, parent, cost)
        self.heuristic_cost = heuristic_cost

    def __lt__(self, other):
        if (self.heuristic_cost + self.total_cost) == (other.heuristic_cost + other.total_cost):
            return self.name < other.name
        return (self.heuristic_cost + self.total_cost) < (other.heuristic_cost + other.total_cost)

    def __gt__(self, other):
        if (self.heuristic_cost + self.total_cost) == (other.heuristic_cost + other.total_cost):
            return self.name > other.name
        return (self.heuristic_cost + self.total_cost) > (other.heuristic_cost + other.total_cost)


# MAIN
def main():
    algorithm = ""
    path_state_space = ""
    path_heuristic = ""
    check_optimistic = False
    check_consistent = False
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--alg":
            algorithm = sys.argv[i+1]
        elif sys.argv[i] == "--ss":
            path_state_space = sys.argv[i+1]
        elif sys.argv[i] == "--h":
            path_heuristic = sys.argv[i+1]
        elif sys.argv[i] == "--check-optimistic":
            check_optimistic = True
        elif sys.argv[i] == "--check-consistent":
            check_consistent = True

    starting_point_name = ""
    finishing_points = set()
    states_succ = {}

    with open(f"{path_state_space}", "r", encoding="utf8") as file:
        lines = file.read().split("\n")
        for line in lines:
            if not line:
                continue
            if line.startswith("#"):
                continue
            if starting_point_name == "":
                starting_point_name = line
            elif len(finishing_points) == 0:
                for l in line.split():
                    finishing_points.add(l)
            else:
                splitted_line = line.split()
                state = splitted_line[0][:-1]
                states_succ[state] = []
                for i in splitted_line[1:]:
                    splitted_next_state = i.split(",")
                    states_succ[state].append((splitted_next_state[0], splitted_next_state[1]))

    solution = None
    if check_optimistic:
        optimistic_check(path_heuristic, states_succ, finishing_points)
    elif check_consistent:
        consistent_check(path_heuristic, states_succ)
    elif algorithm == "bfs":
        print("# BFS")
        solution, states_visited, path_length, total_cost, path = bfs(starting_point_name, finishing_points, states_succ)
    elif algorithm == "ucs":
        print("# UCS")
        solution, states_visited, path_length, total_cost, path = ucs(starting_point_name, finishing_points, states_succ)
    elif algorithm == "astar":
        print(f"# A-STAR {path_heuristic}")
        solution, states_visited, path_length, total_cost, path = a_star(starting_point_name, finishing_points, states_succ,
                                                                         path_heuristic)

    if not check_optimistic and not check_consistent:
        print("[FOUND_SOLUTION]:", "yes" if solution is not None else "no")

    if solution is not None:
        print("[STATES_VISITED]:", states_visited)
        print("[PATH_LENGTH]:", path_length)
        print("[TOTAL_COST]:", total_cost)
        print("[PATH]:", path)


# BREADTH FIRST SEARCH
def bfs(starting_point, finishing_points, states_succ):

    open_q = [Node(starting_point, None, 0)]
    visited = set()
    solution = None
    while open_q:
        node = open_q.pop(0)
        visited.add(node.name)

        if node.name in finishing_points:
            solution = node
            break

        for next_node in sorted(states_succ[node.name]):
            if next_node[0] not in visited:
                open_q.append(Node(next_node[0], node, int(next_node[1])))

    result_path = []
    costs = []
    if solution is not None:
        get_path(solution, result_path, costs)

    return solution, len(visited), len(result_path), float(sum(costs)), " => ".join(map(str, result_path))


# UNIFORM COST SEARCH
def ucs(starting_point, finishing_points, states_succ):
    open_q = []
    heapq.heappush(open_q, Node(starting_point, None, 0))
    heapq.heapify(open_q)
    visited = set()
    solution = None
    while open_q:
        node = heapq.heappop(open_q)
        visited.add(node.name)

        if node.name in finishing_points:
            solution = node
            break

        for next_state in sorted(states_succ[node.name]):
            if next_state[0] not in visited:
                heapq.heappush(open_q, Node(next_state[0], node, int(next_state[1])))

    result_path = []
    costs = []
    if solution is not None:
        get_path(solution, result_path, costs)

    return solution, len(visited), len(result_path), float(sum(costs)), " => ".join(map(str, result_path))


# A_STAR
def a_star(starting_point_name, finishing_points, states_succ, heuristics_path):
    heuristics = read_heuristics(heuristics_path)
    open_dict = {}
    visited_dict = {}
    open_q = []
    heapq.heapify(open_q)
    solution = None
    starting_node = HeuristicNode(starting_point_name, None, 0, heuristics[starting_point_name])
    open_dict[starting_point_name] = starting_node
    heapq.heappush(open_q, starting_node)

    while open_q:
        node = heapq.heappop(open_q)
        open_dict.pop(node.name)
        if node.name in finishing_points:
            solution = node
            break

        visited_dict[node.name] = node

        for next_state in states_succ[node.name]:
            next_node = HeuristicNode(next_state[0], node, int(next_state[1]), heuristics[next_state[0]])

            open_node = None
            visited_node = None

            # CHECK IF THE STATE ALREADY EXISTS IN EITHER OPEN OR VISITED SET
            if next_state[0] in open_dict:
                open_node = open_dict[next_state[0]] #node from open dict
            if next_state[0] in visited_dict:
                visited_node = visited_dict[next_state[0]] #node from visited dict

            if (open_node is not None and open_node < next_node) or (visited_node is not None and visited_node < next_node):
                continue

            # REMOVE FROM OPEN LIST AND DICTIONARY
            if open_node is not None:
                open_dict.pop(open_node.name)
                open_q = [i for i in open_q if i.name != open_node.name]
            if visited_node is not None:
                visited_dict.pop(visited_node.name)

            heapq.heappush(open_q, next_node)
            open_dict[next_node.name] = next_node

    result_path = []
    costs = []
    if solution is not None:
        get_path(solution, result_path, costs)

    return solution, len(visited_dict), len(result_path), float(sum(costs)), " => ".join(map(str, result_path))


def optimistic_check(path_heuristic, states_succ, finishing_points):
    print(f"# HEURISTIC-OPTIMISTIC {path_heuristic}")

    heuristics = read_heuristics(path_heuristic)
    optimistic = True
    for key, value in heuristics.items():
        solution, states_visited, path_length, total_cost, path = ucs(key, finishing_points, states_succ)

        if not value <= total_cost:
            print(f"[CONDITION]: [ERR] h({key}) <= h*: {float(value)} <= {float(total_cost)}")
            optimistic = False
        else:
            print(f"[CONDITION]: [OK] h({key}) <= h*: {float(value)} <= {float(total_cost)}")

    print(f"[CONCLUSION]: Heuristic is{' not' if not optimistic else ''} optimistic.")


def consistent_check(path_heuristic, states_succ):
    print(f"# HEURISTIC-CONSISTENT {path_heuristic}")

    heuristics = read_heuristics(path_heuristic)
    consistent = True
    for key, value in heuristics.items():
        for next_state in states_succ[key]:
            if not value <= heuristics[next_state[0]] + int(next_state[1]):
                print(f"[CONDITION]: [ERR] h({key}) <= h({next_state[0]}) + c: {float(value)} <= {float(heuristics[next_state[0]])} + {float(next_state[1])}")
                consistent = False
            else:
                print(f"[CONDITION]: [OK] h({key}) <= h({next_state[0]}) + c: {float(value)} <= {float(heuristics[next_state[0]])} + {float(next_state[1])}")

    print(f"[CONCLUSION]: Heuristic is{' not' if not consistent else ''} consistent.")


def read_heuristics(path_heuristic):
    heuristics = {}
    with open(f"{path_heuristic}", "r", encoding="utf8") as file:
        lines = file.read().split("\n")
        for line in sorted(lines):
            if not line or line.startswith("#"):
                continue
            splitted_line = line.split(" ")
            heuristics[splitted_line[0][:-1]] = int(splitted_line[1])
    return heuristics


def get_path(state, path, costs):
    if state.parent is not None:
        get_path(state.parent, path, costs)
    path.append(state.name)
    costs.append(state.cost)


if __name__ == '__main__':
    main()
