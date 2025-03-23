from collections import deque
from concurrent.futures import ThreadPoolExecutor
import time
from AI.algorithm_registry import AIAlgorithmRegistry
from game_logic.constants import A_STAR, AI_FOUND, AI_NOT_FOUND, AI_RUNNING, BFS, DFS, GREEDY, GRID_SIZE, INFINITE, ITER_DEEP, UNIFORM_COST, WEIGHTED_A_STAR
from utils.ai import child_states, goal_state
from utils.measuring import save_to_file


# For running AI algorithms in parallel
executor = ThreadPoolExecutor(max_workers=1)

def measure_time(func):
    """Decorator to measure the elapsed time of a function.

    """

    def wrapper(self, *args, **kwargs):
        print(f"Called {func.__name__} from the class: {self.__class__.__name__} and we're measuring the elapsed time")
        start_time = time.time()

        result = func(self, *args, **kwargs)

        elapsed_time = time.time() - start_time
        print(f"Elapsed time for {func.__name__}: {elapsed_time:.4f} seconds")

        save_to_file(f"{self.__class__.__name__}_elapsed_time.csv", elapsed_time)

        print(f"Finished {func.__name__} from the class: {self.__class__.__name__}")
        return result
    return wrapper


class TreeNode:
    def __init__(self, state, parent=None):
        """Initializes a new TreeNode object.
        Args:
            state (GameData): The state of the game (NOT TO BE CONFUSED WITH THE STATES FROM THE STATE MACHINE). This is the data that the AI will use to make its decision while actually playing the game on the board.
            parent (TreeNode, optional): The parent node of the current node. Defaults to None.
        """

        self.state = state
        self.parent = parent
        self.children = []

    def add_child(self, child_node):
        """Adds a child node to the current node. Also sets the parent of the child node to the current node.

        Args:
            child_node (TreeNode): The child node to add.
        """

        self.children.append(child_node)
        child_node.parent = self

class AIAlgorithm:
    def __init__(self, level):
        self.current_state = None
        self.next_state = None

        self.goal_state_func = goal_state if level != INFINITE else None # TODO: Implement goal state function for infinite level (EXTRA FEATURE)
        self.operators_func = child_states

        self.stop_flag = False
        self.future = None
        self.result = None
        print("Called constructor of the base class AIAlgorithm")
        print("The type of the constructed object is:", type(self))

    def stop(self):
        """Stop the AI algorithm execution.

        """

        self.stop_flag = True

    def get_next_move(self, game_data):
        """Get the next move or the goal move for the AI.

        Args:
            game_data (GameData): The current game state (NOT TO BE CONFUSED WITH THE STATES FROM THE STATE MACHINE). This is the data that the AI will use to make its decision while actually playing the game on the board.

        Returns:
            tuple: The index of the piece to play and the position to play it at. If the move is not ready yet, return None
        """

        def get_next_piece():
            played_piece = None

            # Find the piece that was played
            for piece in self.current_state.pieces:
                if piece not in self.next_state.pieces:
                    played_piece = piece
                    break
            if not played_piece:
                return None, None # No piece found

            # Search top-left to bottom-right for position of played piece
            # (matches the way the pieces are stored/interpreted/displayed - top-left square is (0, 0))
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    if self.current_state.board[i][j] != self.next_state.board[i][j]:
                        return played_piece, (i, j)
            return None, None # No position found

        # Needed in run_algorithm() when the algorithm is run (not every time get_next_move() is called)
        self.current_state = game_data

        # No results yet/anymore, so run the algorithm (again)
        if self.result is None:
            if self.future is None:
                print("Running the algorithm")
                self.future = executor.submit(self.run_algorithm)
                return AI_RUNNING, (None, None)  # Indicate that the move is not ready yet
            elif not self.future.done():
                print("Algorithm is still running")
                return AI_RUNNING, (None, None)  # Indicate that the move is not ready yet
            else:
                print("Algorithm has finished running")
                self.result = self.future.result()
                self.future = None

        self.next_state = self.result[0]
        piece_index, piece_position = get_next_piece()

        # Remove the state that is being played from the result (to avoid playing the same move again in the next call)
        self.result = self.result[1:] if len(self.result) > 1 else None

        if piece_index is None or piece_position is None:
            return AI_NOT_FOUND, (None, None)
        else:
            return AI_FOUND, (piece_index, piece_position)

    @measure_time
    def run_algorithm(self):
        """Run the AI algorithm

        Returns:
            TreeNode: The node containing the next state of the game.
        """

        return NotImplementedError("This method should be overridden by subclasses")

    def order_nodes(self, node):
        """Order the resulting nodes from the search tree in a way that the first node is the one next state to reach that leads to the goal state.

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
    @measure_time
    def run_algorithm(self):
        root = TreeNode(self.current_state)  # Root node in the search tree
        queue = deque([root])                # Store the nodes
        visited = set()                      # Contains states, not nodes (to avoid duplicate states reached by different paths)

        while queue:
            if self.stop_flag:  # Check stop flag
                print("Algorithm stopped early")
                self.result = None
                return

            node = queue.popleft()

            if self.goal_state_func(node.state):
                self.result = self.order_nodes(node)
                return

            for child_state in self.operators_func(node.state):
                if child_state not in visited:
                    child_node = TreeNode(child_state, node) # Already assigns the parent, so add_child is partially redundant but that's okay
                    node.add_child(child_node)
                    queue.append(child_node)

        self.result = None  # No valid moves found
        return self.result

class DFSAlgorithm(AIAlgorithm):
    @measure_time
    def run_algorithm(self):

        raise NotImplementedError("Not implemented yet")

class IterDeepAlgorithm(AIAlgorithm):
    @measure_time
    def run_algorithm(self):

        raise NotImplementedError("Not implemented yet")

class UniformCostAlgorithm(AIAlgorithm):
    @measure_time
    def run_algorithm(self):

        raise NotImplementedError("Not implemented yet")

class GreedySearchAlgorithm(AIAlgorithm):
    @measure_time
    def run_algorithm(self):

        raise NotImplementedError("Not implemented yet")

class AStarAlgorithm(AIAlgorithm):
    @measure_time
    def run_algorithm(self):

        raise NotImplementedError("Not implemented yet")

class WeightedAStarAlgorithm(AIAlgorithm):
    @measure_time
    def run_algorithm(self):

        raise NotImplementedError("Not implemented yet")

# Register algorithms
AIAlgorithmRegistry.register(BFS, BFSAlgorithm)
AIAlgorithmRegistry.register(DFS, DFSAlgorithm)
AIAlgorithmRegistry.register(ITER_DEEP, IterDeepAlgorithm)
AIAlgorithmRegistry.register(UNIFORM_COST, UniformCostAlgorithm)
AIAlgorithmRegistry.register(GREEDY, GreedySearchAlgorithm)
AIAlgorithmRegistry.register(A_STAR, AStarAlgorithm)
AIAlgorithmRegistry.register(WEIGHTED_A_STAR, WeightedAStarAlgorithm)
