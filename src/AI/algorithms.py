import queue as q
import time
import tracemalloc
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from AI.algorithm_registry import AIAlgorithmRegistry
from AI.heuristics import (a_star_heuristic, a_star_heuristic_2,
                           greedy_heuristic, infinite_heuristic)
from game_logic.constants import (A_STAR, AI_FOUND, AI_NOT_FOUND, BFS, DFS,
                                  GREEDY, INFINITE, ITER_DEEP, SINGLE_DEPTH_GREEDY, LEVELS_NAMES,
                                  WEIGHTED_A_STAR)
from utils.ai import child_states, get_num_states, goal_state
from utils.file import moves_to_file, stats_to_file


# For running AI algorithms in parallel
executor = ThreadPoolExecutor(max_workers=1)


class TreeNode:
    def __init__(self, state, parent=None, path_cost=0, depth=0, heuristic_score=0):
        """Initializes a new TreeNode object.

        Args:
            state (GameData): The state of the game (NOT TO BE CONFUSED WITH THE STATES FROM THE STATE MACHINE). This is the data that the AI will use to make its decision while actually playing the game on the board.
            parent (TreeNode, optional): The parent node of the current node. Defaults to None.
            path_cost (int, optional): The cost to reach the current node from the root node. Defaults to 0.
            depth (int, optional): The depth of the current node in the search tree. Defaults to 0.
            heuristic_score (int, optional): The score of the node based on the heuristic function. Defaults to 0.

        """

        self.state = state
        self.parent = parent
        self.children = []
        self.path_cost = path_cost
        self.depth = depth
        self.heuristic_score = heuristic_score

    def add_child(self, child_node):
        """Adds a child node to the current node. Also sets the parent of the child node to the current node.

        Args:
            child_node (TreeNode): The child node to add.

        """

        self.children.append(child_node)
        child_node.parent = self    # Constructor can already do this, it's partially redundant but that's okay

    def __lt__(self, other):
        """Defines the less-than comparison for TreeNode objects.
        This is used by the priority queue to compare nodes.

        Args:
            other (TreeNode): The other TreeNode to compare with.

        Returns:
            bool: True if this node is less than the other node, False otherwise.

        """

        return self.heuristic_score < other.heuristic_score

class AIAlgorithm:
    def __init__(self, level):
        self.current_state = None
        self.next_state = None

        self.level = level

        self.goal_state_func = goal_state if self.level != INFINITE else None # No goal state function for infinite level
        self.operators_func = child_states
        self.time_callback_func = None
        self.res_callback_func = None

        self.stop_flag = False
        self.future = None
        self.result = None

        print(f"[AIAlgorithm] Initialized: {type(self).__name__}")

    def stop(self):
        """Stop the AI algorithm execution.
        Resets everything related to the algorithm running in the background.

        """

        self.stop_flag = True
        if self.future is not None:
            self.future.cancel()
            self.future = None
        self.res_callback_func = None
        self.result = None

    def get_next_move(self, game_data, time_callback_func=None, res_callback_func=None, reset=False):
        """Start running the AI algorithm in the background (separate thread)
        Calls the callback function with the result when it's done.

        Args:
            game_data (GameData): The current game state (NOT TO BE CONFUSED WITH THE STATES FROM THE STATE MACHINE). This is the data that the AI will use to make its decision while actually playing the game on the board.
            time_callback_func (function, optional): The function to call when the algorithm starts and when it ends. Defaults to None.
            res_callback_func (function, optional): The function to call when the algorithm is done. Defaults to None.
            reset (bool, optional): Whether to reset the stored algorithm results. Defaults to False.

        """

        self.stop_flag = False
        self.time_callback_func = time_callback_func
        self.res_callback_func = res_callback_func

        # Reset the AI algorithm results (when current state of the game doesn't match stat expected for result of the algorithm to be used)
        if reset:
            self.next_state = None
            self.future = None
            self.result = None

        # Needed in _execute_algorithm() - when the algorithm is actually run (not every time get_next_move() is called)
        self.current_state = game_data

        # No results yet/anymore, so run the algorithm (again)
        if self.result is None or self.result == []:
            if self.future is None or self.future.done():
                # Run the algorithm in a separate thread
                print(f"[{type(self).__name__}] Submitting algorithm...")
                if self.level == INFINITE:
                    self.future = executor.submit(self.run_algorithm, infinite=True)
                else:
                    self.future = executor.submit(self.run_algorithm)
                self.future.add_done_callback(self._on_algorithm_done)

                if self.time_callback_func is not None:
                    self.time_callback_func()
            else:
                print(f"[{type(self).__name__}] Algorithm already running.")
        else:
            print(f"[{type(self).__name__}] Using stored result.")
            piece_index, piece_position = self._process_result()
            status = AI_FOUND if piece_index is not None and piece_position is not None else AI_NOT_FOUND
            if self.res_callback_func is not None:
                self.res_callback_func(status, piece_index, piece_position)

    def _on_algorithm_done(self, future):
        """Callback function for when the algorithm has finished running.
        Calls the defined callback function if it exists.

        Args:
            future (Future): The future object that contains the result of the algorithm.

        """

        print(f"[{type(self).__name__}] Algorithm done.")
        self.time_callback_func()

        self.result = future.result()
        print(f"Future: {self.future}")
        print(f"Other future: {future}")
        print(f"Are they the same? {self.future == future}")

        if self.result is None:
            if self.res_callback_func is not None:
                self.res_callback_func(AI_NOT_FOUND, None, None)
            return

        piece_index, piece_position = self._process_result()
        status = AI_FOUND if piece_index is not None and piece_position is not None else AI_NOT_FOUND

        if self.res_callback_func is not None:
            self.res_callback_func(status, piece_index, piece_position)

    def _process_result(self):
        self.next_state = self.result[0].state
        print(f"[{type(self).__name__}] Result list: {self.result}")
        # Remove the state that is being played from the result (to avoid playing the same move again in the next call)
        self.result = self.result[1:] if len(self.result) > 1 else None
        print(f"[{type(self).__name__}] Result list after removing the state being played: {self.result}")

        print(f"Piece: {self.next_state.recent_piece[0]}, Piece position: {self.next_state.recent_piece[1]}")
        for i, piece in enumerate(self.current_state.pieces):
            print(f"Piece {i}: {piece}")
            if self.next_state.recent_piece[0] == piece:
                print(f"Piece index: {i}, Piece position: {self.next_state.recent_piece[1]}")
                return i, self.next_state.recent_piece[1]

    def run_algorithm(self, infinite=False):
        """Decorator function to run the AI algorithm and measure its performance (time, memory, states visited).
        Calls the actual implementation of the algorithm.

        Returns:
            List[TreeNode]: The list of nodes from the root (exclusive) to the goal state (inclusive).

        """

        print(f"[{type(self).__name__}] Running algorithm...")
        start_time = time.time()
        tracemalloc.start()

        snapshot_before = tracemalloc.take_snapshot()

        result = self._execute_algorithm(infinite)  # Call the actual implementation

        snapshot_after = tracemalloc.take_snapshot()

        elapsed_time = time.time() - start_time
        tracemalloc.stop()

        stats = snapshot_after.compare_to(snapshot_before, 'lineno')
        peak_mem = sum(stat.size_diff for stat in stats)

        num_states = get_num_states()

        if result is not None:
            print(f"[{type(self).__name__}] Algorithm completed successfully.")
        else:
            print(f"[{type(self).__name__}] Algorithm did not complete successfully. No valid moves found.")

        # Time of storage (to match records between stats and moves)
        irl_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        stats_to_file(
            f"{self.__class__.__name__}_stats.csv",
            irl_timestamp,
            LEVELS_NAMES[self.level],
            True if result else False,
            elapsed_time,
            peak_mem,
            num_states,
            len(result) if result else 0
        )

        if result is not None:
            moves_to_file(
                f"{self.__class__.__name__}_moves.csv",
                irl_timestamp,
                LEVELS_NAMES[self.level],
                elapsed_time,
                len(result),
                [(node.state.recent_piece[0], node.state.recent_piece[1]) for node in result]
            )

        print(f"[{type(self).__name__}] Level: {LEVELS_NAMES[self.level]}")
        print(f"[{type(self).__name__}] Did the algorithm find a solution? {'Yes' if result else 'No'}")
        print(f"[{type(self).__name__}] Time: {elapsed_time:.4f}s")
        print(f"[{type(self).__name__}] Peak Memory Used: {peak_mem / (1024 * 1024):.4f} MB")
        print(f"[{type(self).__name__}] States: {num_states}")
        print(f"[{type(self).__name__}] Number of moves: {len(result) if result else 0}")
        print(f"[{type(self).__name__}] Moves:")
        for i, node in enumerate(result):
            print(f"[{type(self).__name__}] Piece {i+1}: {node.state.recent_piece[0]} to Position: {node.state.recent_piece[1]}")

        return result

    def _execute_algorithm(self, infinite = False):
        """Run the actual AI algorithm

        Returns:
            List[TreeNode]: The list of nodes from the root (exclusive) to the goal state (inclusive).

        """

        raise NotImplementedError(f"{type(self).__name__} must override _execute_algorithm()")

    def order_nodes(self, node):
        """Sort nodes to trace back the path from root to goal.

        Args:
            node (TreeNode): The node containing the goal state or the next state, depending on the algorithm.

        Returns:
            list: The list of nodes from the root (exclusive) to the goal state (inclusive).

        """
        print("Called order_nodes() from the class:", type(self))

        nodes = []
        while node and node.state != self.current_state:
            nodes.append(node)
            node = node.parent
        nodes.reverse() # Reverse the list to get the path from the root to the goal state
        for n in nodes:
            print(f"Node n's state: {n.state}")
        return nodes


class BFSAlgorithm(AIAlgorithm):
    """Implements the Breadth-First Search algorithm (BFS) for the AI to find the next move to play.

    Time Complexity:
        O(b^d * (<complexity of operators_func()> + <complexity of goal_state_func()>) == O(b^d * (p * g^4 + 1)) == O(b^d * p * g^4), where:
        - b is the branching factor
        - d is the depth of the solution
        - p is the number of currently playable pieces
        - g is the grid size
    Space Complexity:
        O(b^d), where b is the branching factor and d is the depth of the solution.

    """

    def _execute_algorithm(self, infinite = False):
        root = TreeNode(self.current_state)  # Root node in the search tree
        queue = deque([root])                # Store the nodes
        visited = set()                      # Contains states, not nodes (to avoid duplicate states reached by different paths)

        while queue:
            if self.stop_flag:
                print("Algorithm stopped early")
                return None

            node = queue.popleft()

            if self.goal_state_func(node.state):
                return self.order_nodes(node)

            for child_state in self.operators_func(node.state):
                if child_state not in visited:
                    child_node = TreeNode(child_state, node, node.path_cost + 1, node.depth + 1)
                    node.add_child(child_node)

                    queue.append(child_node)
                    visited.add(child_state)

        return None # No valid moves found


class DFSAlgorithm(AIAlgorithm):
    """Implements the Depth-First Search algorithm (DFS) for the AI to find the next move to play.
    It uses the iterative version of the algorithm, which is more efficient than the recursive version, especially for large search trees.

    Time Complexity:
        O(b^m * (<complexity of operators_func()> + <complexity of goal_state_func()>) == O(b^m * (p * g^4 + 1)) == O(b^m * p * g^4), where:
        - b is the branching factor
        - m is the maximum depth of the search tree
        - p is the number of currently playable pieces
        - g is the grid size

    Space Complexity:
        O(b * m), where b is the branching factor and m is the maximum depth of the search tree.

    """

    def _execute_algorithm(self, infinite = False):
        root = TreeNode(self.current_state)  # Root node in the search tree
        stack = [root]                       # Store the nodes
        visited = set()                      # Contains states, not nodes (to avoid duplicate states reached by different paths)

        while stack:
            if self.stop_flag:  # Check stop flag
                print("Algorithm stopped early")
                return None

            node = stack.pop()
            if node.state not in visited:
                visited.add(node.state)

                if self.goal_state_func(node.state):
                    return self.order_nodes(node)

                for child_state in self.operators_func(node.state):
                    if child_state not in visited:
                        child_node = TreeNode(child_state, node, node.path_cost + 1, node.depth + 1)
                        node.add_child(child_node)

                        stack.append(child_node)

        return None  # No valid moves found


class IterDeepAlgorithm(AIAlgorithm):
    """Implements the Iterative Deepening Search algorithm (IDS) for the AI to find the next move to play.
    Since it uses DFS to visit the nodes, the code uses the iterative version of the DFS, which is more efficient than the recursive version, especially for large search trees.
    It also uses a depth limit, to limit the search of each DFS, which is better for a large search space.

    Time Complexity:
        O(b^d * (<complexity of operators_func()> + <complexity of goal_state_func()>) == O(b^d * (p * g^4 + 1)) == O(b^d * p * g^4), where:
        - b is the branching factor
        - d is the depth of the solution
        - p is the number of currently playable pieces
        - g is the grid size

    Note: b^d is a simplification of the time complexity of the algorithm, since it is actually d*b^1 + (d-1)b^2 + (d-2)b^3 + ... + 2b^(d-1) + b^d, therefore the dominant term is b^d.
          - Still, because of this, it is less efficient than DFS, since it visits the same nodes multiple times.

    Space Complexity:
        O(b * d), where b is the branching factor and d is the depth of the solution.

    """

    def _execute_algorithm(self, infinite = False):
        def depth_limited_search(start_node, limit):
            stack = [start_node]        # Store the nodes
            visited = set()             # Contains states, not nodes (to avoid duplicate states reached by different paths)
            found_new_nodes = False     # Track if new nodes were added

            while stack:
                if self.stop_flag:
                    print("Algorithm stopped early")
                    return "STOPPED"

                node = stack.pop()
                if node.state not in visited:
                    visited.add(node.state)

                    if self.goal_state_func(node.state):
                        return self.order_nodes(node)

                    if node.depth < limit:
                        for child_state in self.operators_func(node.state):
                            if child_state not in visited:
                                child_node = TreeNode(child_state, node, node.path_cost + 1, node.depth + 1)
                                node.add_child(child_node)
                                stack.append(child_node)
                                found_new_nodes = True       # We have added a node to the stack, which means that we could look forward into the graph (not the bottom of the stack)

            if found_new_nodes:
                return "NOT YET EXHAUSTED"
            else:
                # Even if we increase the depth, we wouldn't find any new nodes, as we already searched whole graph
                # End of depth_limited_search function
                "EXHAUSTED"

        depth_limit = 1
        while True:
            root = TreeNode(self.current_state)
            result = depth_limited_search(root, depth_limit)
            if result == "EXHAUSTED" or result == "STOPPED":
                # No new nodes were found, stop searching
                return None
            if result == "NOT YET EXHAUSTED":
                # When the stack was found empty since we reached the limiting depth and no further children nodes were added
                depth_limit += 1
            else:
                # an answer was found before we reached empty stack
                return result

class GreedySearchAlgorithm(AIAlgorithm):
    """Implements the Greedy Search algorithm for the AI to find the next move to play.
    It uses a heuristic function to evaluate the nodes and choose the best one to explore next.

    Time Complexity:
        O(b^m * (<complexity of operators_func()> + <complexity of goal_state_func()> + <complexity of greedy_heuristic()>) == O(b^m * (p * g^4 + 1 + p * g^2 * k)) == O(b^m * p * g^4), where:
        - b is the branching factor
        - m is the maximum depth of the search tree
        - p is the number of currently playable pieces
        - g is the grid size
        - k is the number of blocks in the piece (very small, between 1 and 4 for the current available pieces).

    Space Complexity:
        O(b^m), where b is the branching factor and m is the depth of the solution.

    Note: Due to the heuristic function, the algorithm is way more efficient than the Big-O notation suggests, as it doesn't explore nearly as many nodes as the worst case scenario.
    Of course, this depends on the quality of the heuristic function, and in this case, it is very good.

    """

    def __init__(self, level):
        super().__init__(level)
        self.heuristic_func = greedy_heuristic

    def _execute_algorithm(self, infinite = False):
        root = TreeNode(self.current_state)  # Root node in the search tree
        pqueue = q.PriorityQueue()           # Priority queue for node storing
        pqueue.put(root)                     # Add the root node to the priority queue
        visited = set()                      # Contains states, not nodes (to avoid duplicate states reached by different paths)

        inheritance = True                   # Inherit the score from the parent node

        while not pqueue.empty():
            if self.stop_flag:
                print("Algorithm stopped early")
                return None

            node = pqueue.get()

            if self.goal_state_func(node.state):
                return self.order_nodes(node)

            for child_state in self.operators_func(node.state):
                if child_state not in visited:
                    child_node = TreeNode(
                        child_state,
                        node,
                        node.path_cost + 1,
                        node.depth + 1,
                        self.heuristic_func(node, child_state, root.state.blocks_to_break, inheritance)
                    )
                    node.add_child(child_node)

                    pqueue.put(child_node)
                    visited.add(child_state)

        return None  # No valid moves found

class SingleDepthGreedyAlgorithm(AIAlgorithm):
    """Refactored to evaluate all possible moves at depth 1 and choose the best move based on the heuristic function.

    Time Complexity:
        O(b * (<complexity of operators_func()> + <complexity of heuristic_func()>)) == O(b * (p * g^4 + p * g^2 * k)),
        where:
        - b is the branching factor (number of possible moves)
        - p is the number of currently playable pieces
        - g is the grid size
        - k is the number of blocks in the piece.

    Space Complexity:
        O(b), where b is the branching factor.
    """

    def __init__(self, level):
        print(f"[AIAlgorithm] Initializing {type(self).__name__}...")
        super().__init__(level)
        self.heuristic_func = infinite_heuristic  # Use the provided heuristic function

    def _execute_algorithm(self, infinite=False):
        root = TreeNode(self.current_state)  # Root node in the search tree
        best_node = None  # Track the best node based on the heuristic score

        # Explore all child states (depth 1)
        for child_state in self.operators_func(root.state):
            # Create a child node for each possible move
            child_node = TreeNode(
                child_state,
                root,
                path_cost=1,
                depth=1,
                heuristic_score=self.heuristic_func(root, child_state)
            )
            root.add_child(child_node)

            # Update the best node if this child has a better heuristic score
            if best_node is None or child_node.heuristic_score < best_node.heuristic_score:
                best_node = child_node

        if best_node is None:
            print("Couldn't find any valid moves")
            return None

        # Return the best node found
        return self.order_nodes(best_node)

class AStarAlgorithm(AIAlgorithm):
    """Implements the A* Search algorithm for the AI to find the next move to play.
    It uses a heuristic function and the cost from the starting node to the current one to evaluate the nodes and choose the best one to explore next.

    Time Complexity:
        O(b^d * (<complexity of operators_func()> + <complexity of goal_state_func()> + <complexity of a_star_heuristic()>) == O(b^d * (p * g^4 + 1 + g^2)) == O(b^d * p * g^4), where:
        - b is the branching factor
        - d is the depth of the solution
        - p is the number of currently playable pieces
        - g is the grid size

    Space Complexity:
        O(b^d), where b is the branching factor and d is the depth of the solution.

    Note: Due to the heuristic function, this algorithm is way more efficient than the Big-O notation suggests, as it doesn't explore nearly as many nodes as the worst case scenario, due to the heuristic function.
    However, unlike the Greedy Search algorithm, this algorithm is guaranteed to find the optimal solution, if the heuristic function is admissible (which it is in this case).
    The heuristic function is admissible if it never overestimates the cost to reach the goal state from the current state.
    The quality of the heuristic function is very important for the performance of the algorithm, as it determines how many nodes are explored. And the closer it is to the actual cost, the better the performance of the algorithm.

    """

    def __init__(self, level):
        super().__init__(level)
        self.heuristic_func = a_star_heuristic

    def _execute_algorithm(self, infinite = False):
        root = TreeNode(self.current_state)  # Root node in the search tree
        pqueue = q.PriorityQueue()           # Priority queue for node storing
        pqueue.put(root)                     # Add the root node to the priority queue
        visited = set()                      # Contains states, not nodes (to avoid duplicate states reached by different paths)

        while not pqueue.empty():
            if self.stop_flag:
                print("Algorithm stopped early")
                return None

            # print("Queue size:", pqueue.qsize())
            # print("Visited size:", len(visited))
            node = pqueue.get()

            if self.goal_state_func(node.state):
                return self.order_nodes(node)

            for child_state in self.operators_func(node.state):
                if child_state not in visited:
                    child_node = TreeNode(
                        child_state,
                        node,
                        node.path_cost + 1,
                        node.depth + 1,
                        self.heuristic_func(child_state) + (node.path_cost + 1)
                    )
                    node.add_child(child_node)

                    pqueue.put(child_node)
                    visited.add(child_state)

        return None  # No valid moves found

class WeightedAStarAlgorithm(AIAlgorithm):
    """Implements the Weighted A* Search algorithm for the AI to find the next move to play.
    It uses a heuristic function and the cost from the starting node to the current one to evaluate the nodes and choose the best one to explore next.
    The heuristic function is weighted to make the algorithm more aggressive in its search (higher weight == more aggressive search).

    Time Complexity:
        O(b^d * (<complexity of operators_func()> + <complexity of goal_state_func()> + <complexity of a_star_heuristic()>) == O(b^d * (p * g^4 + 1 + g^2)) == O(b^d * p * g^4), where:
        - b is the branching factor
        - d is the depth of the solution
        - p is the number of currently playable pieces
        - g is the grid size

    Space Complexity:
        O(b^d), where b is the branching factor and d is the depth of the solution.

    Note: Due to the heuristic function, this algorithm is way more efficient than the Big-O notation suggests, as it doesn't explore nearly as many nodes as the worst case scenario, due to the heuristic function.
    Due to the weighted heuristic function, this algorithm is more aggressive than the A* Search algorithm, which means that it will explore less nodes and find the solution faster, but it is not guaranteed to find the optimal solution, but it will find a satisfactory solution in a reasonable amount of time.

    """

    def __init__(self, level):
        super().__init__(level)
        self.heuristic_func = a_star_heuristic

    def _execute_algorithm(self, infinite = False):
        root = TreeNode(self.current_state)  # Root node in the search tree
        pqueue = q.PriorityQueue()           # Priority queue for node storing
        pqueue.put(root)                     # Add the root node to the priority queue
        visited = set()                      # Contains states, not nodes (to avoid duplicate states reached by different paths)
        weight = 4                           # Weight for the heuristic function (can be adjusted)

        while not pqueue.empty():
            if self.stop_flag:
                print("Algorithm stopped early")
                return None

            node = pqueue.get()

            if self.goal_state_func(node.state):
                return self.order_nodes(node)

            for child_state in self.operators_func(node.state):
                if child_state not in visited:
                    child_node = TreeNode(
                        child_state,
                        node,
                        node.path_cost + 1,
                        node.depth + 1,
                        self.heuristic_func(child_state) * weight + (node.path_cost + 1)
                    )
                    node.add_child(child_node)

                    pqueue.put(child_node)
                    visited.add(child_state)

        return None  # No valid moves found


# Register algorithms
AIAlgorithmRegistry.register(BFS, BFSAlgorithm)
AIAlgorithmRegistry.register(DFS, DFSAlgorithm)
AIAlgorithmRegistry.register(ITER_DEEP, IterDeepAlgorithm)
AIAlgorithmRegistry.register(GREEDY, GreedySearchAlgorithm)
AIAlgorithmRegistry.register(SINGLE_DEPTH_GREEDY, SingleDepthGreedyAlgorithm)
AIAlgorithmRegistry.register(A_STAR, AStarAlgorithm)
AIAlgorithmRegistry.register(WEIGHTED_A_STAR, WeightedAStarAlgorithm)
