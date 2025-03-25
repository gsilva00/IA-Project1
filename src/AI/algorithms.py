import time
import tracemalloc
from collections import deque
from concurrent.futures import ThreadPoolExecutor

from AI.algorithm_registry import AIAlgorithmRegistry
from game_logic.constants import (A_STAR, AI_FOUND, AI_NOT_FOUND, BFS, DFS,
                                  GREEDY, GRID_SIZE, INFINITE, ITER_DEEP,
                                  UNIFORM_COST, WEIGHTED_A_STAR)
from utils.ai import child_states, goal_state, num_states
from utils.file import stats_to_file


# For running AI algorithms in parallel
executor = ThreadPoolExecutor(max_workers=1)

class TreeNode:
    def __init__(self, state, parent=None, path_cost=0, depth=0):
        """Initializes a new TreeNode object.
        Args:
            state (GameData): The state of the game (NOT TO BE CONFUSED WITH THE STATES FROM THE STATE MACHINE). This is the data that the AI will use to make its decision while actually playing the game on the board.
            parent (TreeNode, optional): The parent node of the current node. Defaults to None.
            path_cost (int, optional): The cost to reach the current node from the root node. Defaults to 0.
            depth (int, optional): The depth of the current node in the search tree. Defaults to 0.
        """

        self.state = state
        self.parent = parent
        self.children = []
        self.path_cost = path_cost
        self.depth = depth

    def add_child(self, child_node):
        """Adds a child node to the current node. Also sets the parent of the child node to the current node.

        Args:
            child_node (TreeNode): The child node to add.
        """

        self.children.append(child_node)
        child_node.parent = self    # Constructor can already do this, it's partially redundant but that's okay

class AIAlgorithm:
    def __init__(self, level):
        self.current_state = None
        self.next_state = None

        self.goal_state_func = goal_state if level != INFINITE else None # TODO: Implement goal state function for infinite level (EXTRA FEATURE)
        self.operators_func = child_states

        self.stop_flag = False
        self.future = None
        self.callback = None
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
        self.callback = None
        self.result = None

    def get_next_move(self, game_data, callback=None, reset=False):
        """Start running the AI algorithm in the background (separate thread)
        Calls the callback function with the result when it's done.

        Args:
            game_data (GameData): The current game state (NOT TO BE CONFUSED WITH THE STATES FROM THE STATE MACHINE). This is the data that the AI will use to make its decision while actually playing the game on the board.
            callback (function, optional): The function to call when the algorithm has finished running. Defaults to None.
            reset (bool, optional): Whether to reset the stored algorithm results. Defaults to False.

        """

        self.stop_flag = False
        self.callback = callback

        # Reset the AI algorithm results (when current state of the game doesn't match stat expected for result of the algorithm to be used)
        if reset:
            self.result = None
            self.future = None
            self.next_state = None

        # Needed in _execute_algorithm() - when the algorithm is actually run (not every time get_next_move() is called)
        self.current_state = game_data

        # No results yet/anymore, so run the algorithm (again)
        if self.result is None:
            if self.future is None:
                print(f"[{type(self).__name__}] Running algorithm...")
                self.future = executor.submit(self.run_algorithm)
                self.future.add_done_callback(self._on_algorithm_done)
            else:
                print(f"[{type(self).__name__}] Algorithm already running.")
        else:
            print(f"[{type(self).__name__}] Using stored result.")
            piece_index, piece_position = self._process_result()
            status = AI_FOUND if piece_index is None or piece_position is None else AI_NOT_FOUND
            if self.callback is not None:
                self.callback(status, piece_index, piece_position)

    def _on_algorithm_done(self, future):
        """Callback function for when the algorithm has finished running.
        Calls the defined callback function if it exists.

        Args:
            future (Future): The future object that contains the result of the algorithm.
        """

        self.result = future.result()

        if self.result is None:
            if self.callback is not None:
                self.callback(AI_NOT_FOUND, None, None)
            return

        piece_index, piece_position = self._process_result()
        status = AI_FOUND if piece_index is not None and piece_position is not None else AI_NOT_FOUND

        if self.callback is not None:
            self.callback(status, piece_index, piece_position)

    def _process_result(self):
        self.next_state = self.result[0].state
        # Remove the state that is being played from the result (to avoid playing the same move again in the next call)
        self.result = self.result[1:] if len(self.result) > 1 else None

        return self.next_state.recent_piece[0], self.next_state.recent_piece[1]

    def run_algorithm(self):
        """Decorator function to run the AI algorithm and measure its performance (time, memory, states visited).
        Calls the actual implementation of the algorithm.

        Returns:
            List[TreeNode]: The list of nodes from the root (exclusive) to the goal state (inclusive).

        """

        print(f"[{type(self).__name__}] Running algorithm...")
        start_time = time.time()
        tracemalloc.start()

        snapshot_before = tracemalloc.take_snapshot()

        result = self._execute_algorithm()  # Call the actual implementation

        snapshot_after = tracemalloc.take_snapshot()

        elapsed_time = time.time() - start_time
        tracemalloc.stop()

        stats = snapshot_after.compare_to(snapshot_before, 'lineno')
        peak_mem = sum(stat.size_diff for stat in stats)
        if result is not None:
            print(f"[{type(self).__name__}] Time: {elapsed_time:.4f}s")
            print(f"[{type(self).__name__}] Memory: {peak_mem / (1024 * 1024):.4f} MB")
            print(f"[{type(self).__name__}] States: {num_states}")
            stats_to_file(f"{self.__class__.__name__}_stats.csv", elapsed_time, peak_mem, num_states)
        else:
            print(f"[{type(self).__name__}] Algorithm did not complete.")

        return result

    def _execute_algorithm(self):
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
        while node and node != self.current_state:
            nodes.append(node)
            node = node.parent
        nodes.reverse() # Reverse the list to get the path from the root to the goal state
        for n in nodes:
            print(f"Node n's state: {n.state}")
        return nodes

class BFSAlgorithm(AIAlgorithm):
    """Implements the Breadth-First Search algorithm (BFS) for the AI to find the next move to play.

    Args:
        AIAlgorithm (AIAlgorithm): Class from which BFSAlgorithm inherits (Base class for all AI algorithms).

    """

    def _execute_algorithm(self):
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

    Args:
        AIAlgorithm (AIAlgorithm): Class from which DFSAlgorithm inherits (Base class for all AI algorithms).

    """

    def _execute_algorithm(self):
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
    def _execute_algorithm(self):

        raise NotImplementedError("Not implemented yet")

class UniformCostAlgorithm(AIAlgorithm):
    def _execute_algorithm(self):

        raise NotImplementedError("Not implemented yet")

class GreedySearchAlgorithm(AIAlgorithm):
    def _execute_algorithm(self):

        raise NotImplementedError("Not implemented yet")

class AStarAlgorithm(AIAlgorithm):
    def _execute_algorithm(self):

        raise NotImplementedError("Not implemented yet")

class WeightedAStarAlgorithm(AIAlgorithm):
    def _execute_algorithm(self):

        raise NotImplementedError("Not implemented yet")

# Register algorithms
AIAlgorithmRegistry.register(BFS, BFSAlgorithm)
AIAlgorithmRegistry.register(DFS, DFSAlgorithm)
AIAlgorithmRegistry.register(ITER_DEEP, IterDeepAlgorithm)
AIAlgorithmRegistry.register(UNIFORM_COST, UniformCostAlgorithm)
AIAlgorithmRegistry.register(GREEDY, GreedySearchAlgorithm)
AIAlgorithmRegistry.register(A_STAR, AStarAlgorithm)
AIAlgorithmRegistry.register(WEIGHTED_A_STAR, WeightedAStarAlgorithm)
