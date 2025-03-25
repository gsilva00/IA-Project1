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
        if self.future:
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
            print(f"[{type(self).__name__}] Algorithm already ran, so the callback function should have been called already and the result should be stored and ready to be used")

    def _on_algorithm_done(self, future):
        """Callback function for when the algorithm has finished running.
        Calls the defined callback function if it exists.

        Args:
            future (Future): The future object that contains the result of the algorithm.
        """

        self.result = future.result()

        if self.result is None:
            if self.callback:
                self.callback(AI_NOT_FOUND, None, None)
            return

        self.next_state = self.result[0].state
        piece_index, piece_position = self._get_next_piece()
        # Remove the state that is being played from the result (to avoid playing the same move again in the next call)
        self.result = self.result[1:] if len(self.result) > 1 else None

        if piece_index is None or piece_position is None:
            if self.callback:
                self.callback(AI_NOT_FOUND, None, None)
        else:
            if self.callback:
                self.callback(AI_FOUND, piece_index, piece_position)

    def _get_next_piece(self):
        """Get the piece that was played and the position it was played at.

        Returns:
            Tuple[int, Tuple[int, int]]: The index of the piece to play and the position to play it at.
        """

        played_piece = None

        # Find the piece that was played
        for piece in self.current_state.pieces:
            if piece not in self.next_state.pieces:
                played_piece = piece
                break
        if not played_piece:
            return None, None  # No piece found

        # Search top-left to bottom-right for position of played piece, stops at first difference found
        # (matches the way the pieces are stored/interpreted/displayed - top-left square is (0, 0))
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.current_state.board[i][j] != self.next_state.board[i][j]:
                    return played_piece, (i, j)
        return None, None  # No position found


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
    """Implements the Iterative Deepening Search algorithm (IDS) for the AI to find the next move to play.
    Since it uses DFS to visit the nodes, the code uses the iterative version of the DFS, which is more efficient than the recursive version, especially for large search trees.
    It also uses a depth limit, to limit the search of each DFS, which is better for a large search space.
    
    Args:
        AIAlgorithm (AIAlgorithm): Class from which IterDeepAlgorithm inherits (Base class for all AI algorithms).

    """

    def _execute_algorithm(self):
        def depth_limited_search(root, depth_limit):
            stack = [root]              # Store the nodes
            visited = set()             # Contains states, not nodes (to avoid duplicate states reached by different paths)
            found_new_nodes = False     # Track if new nodes were added

            while stack:
                if self.stop_flag:  # Check stop flag
                    print("Algorithm stopped early")
                    return "STOPPED"

                node = stack.pop()
                if node.state not in visited:
                    visited.add(node.state)
                    
                    if self.goal_state_func(node.state):
                        return self.order_nodes(node)

                    if node.depth < depth_limit:
                        for child_state in self.operators_func(node.state):
                            if child_state not in visited:
                                child_node = TreeNode(child_state, node, node.path_cost + 1, node.depth + 1)
                                node.add_child(child_node)
                                stack.append(child_node)
                                found_new_nodes = True       # We have added a node to the stack, which means that we could look forward into the graph (not the bottom of the stack).
            
            if found_new_nodes:
                return "NOT YET EXHAUSTED"
            else:
                "EXHAUSTED"   # Even if we increase the depth, we wouldn't find any new nodes, as we already searched whole graph
        #end of depth_limited_search function

        depth_limit = 1                 # normally starts at 0 but it's useless
        while True:
            root = TreeNode(self.current_state)
            result = depth_limited_search(root, depth_limit)
            if result == "EXHAUSTED" or result == "STOPPED":  # No new nodes were found, stop searching
                return None
            if result == "NOT YET EXHAUSTED":  #when the stack was found empty since we reached the limiting depth and no further children nodes were added
                depth_limit += 1
            else:                              # an answer was found before we reached empty stack
                return result  
   


        

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
