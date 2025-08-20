from __future__ import annotations

import logging
import time
import tracemalloc
from collections import deque
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from queue import PriorityQueue
from typing import Callable, TypeAlias

from woodblock.ai.algorithm_registry import AIAlgorithmRegistry
from woodblock.ai.heuristics import a_star_heuristic, greedy_heuristic, infinite_heuristic
from woodblock.game_data import GameData
from woodblock.game_logic.constants import (
    LEVELS_NAMES,
    AIAlgorithmID,
    AIReturn,
    Level,
    PiecePosition,
)
from woodblock.utils.ai import (
    StateCounter,
    child_states,
    goal_state,
)
from woodblock.utils.file import moves_to_file, stats_to_file

GoalStateFunc: TypeAlias = Callable[[GameData], bool] | None
OperatorsFunc: TypeAlias = Callable[[GameData], list[GameData]]
TimeCallbackFunc: TypeAlias = Callable[[], None]
ResCallbackFunc: TypeAlias = Callable[[AIReturn, int | None, PiecePosition | None], None]

LOGGER = logging.getLogger(__name__)

# For running AI algorithms in parallel
executor = ThreadPoolExecutor(max_workers=1)


class TreeNode:
    """Represents a node in the search tree for AI algorithms.

    Attributes:
        state (GameData): The state of the game (NOT TO BE CONFUSED WITH THE STATES FROM THE STATE MACHINE).
            This is the data that the AI will use to make its decision while actually playing the game on the board.
        parent (TreeNode | None): The parent node of the current node.
        children (list[TreeNode]): The children of the current node.
        path_cost (int): The cost to reach the current node from the root node.
        depth (int): The depth of the current node in the search tree.
        heuristic_score (float): The score of the node based on the heuristic function.

    """

    def __init__(
        self,
        state: GameData,
        parent: TreeNode | None = None,
        path_cost: int = 0,
        depth: int = 0,
        heuristic_score: float = 0,
    ) -> None:
        self.state = state
        self.parent = parent
        self.children: list[TreeNode] = []
        self.path_cost = path_cost
        self.depth = depth
        self.heuristic_score = heuristic_score

    def add_child(self, child_node: TreeNode) -> None:
        """Add a child node to the current node. Also set the parent of the child node to the current node.

        Args:
            child_node (TreeNode): The child node to add.

        """
        self.children.append(child_node)
        # TreeNode constructor can already do this, so it's partially redundant but that's okay
        child_node.parent = self

    def __lt__(self, other: TreeNode) -> bool:
        """Define the less-than comparison for TreeNode objects.

        This is used by the priority queue to compare nodes.

        Args:
            other (TreeNode): The other TreeNode to compare with.

        Returns:
            bool: True if this node is less than the other node, False otherwise.

        """
        if self.heuristic_score == other.heuristic_score:
            return self.path_cost < other.path_cost
        return self.heuristic_score < other.heuristic_score


class AIAlgorithm:
    """Base class for AI algorithms used in the game.

    Attributes:
        level (Level): The difficulty level of the game (used to define the goal state).
        current_state (GameData | None): The current state of the game.
        next_state (GameData | None): The next state of the game.
        goal_state_func (GoalStateFunc | None): The function to check if the goal state is reached.
        operators_func (OperatorsFunc): The function to get the child states.
        time_callback_func (TimeCallbackFunc | None): The function to call when the algorithm starts and ends.
        res_callback_func (ResCallbackFunc | None): The function to call with the result when the algorithm is done.
        stop_flag (bool): A flag to indicate if the algorithm should stop mid-execution.
        future (Future | None): The future object representing the possible result of the algorithm execution.
            This is due to the algorithm running in a separate thread, in the background.
        result (list[TreeNode] | None): The result of the algorithm.

    """

    def __init__(self, level: Level) -> None:
        self.level = level

        self.current_state: GameData | None = None
        self.next_state: GameData | None = None

        # No goal state function for infinite level
        self.goal_state_func: GoalStateFunc = goal_state if level != Level.INFINITE else None
        self.operators_func: OperatorsFunc = child_states
        self.time_callback_func: TimeCallbackFunc | None = None
        self.res_callback_func: ResCallbackFunc | None = None

        self.stop_flag = False
        self.future: Future[list[TreeNode] | None] | None = None
        self.result: list[TreeNode] | None = None

        LOGGER.debug(f"[AIAlgorithm] Initialized: {type(self).__name__}")

    def is_running(self) -> bool:
        """Check if the AI algorithm is currently running.

        Returns:
            bool: True if the algorithm is running, False otherwise.

        """
        return not self.stop_flag and self.future is not None and self.future.running()

    def stop(self) -> None:
        """Stop the AI algorithm execution.

        Resets everything related to the algorithm running in the background.

        """
        self.stop_flag = True
        if self.future is not None:
            self.future.cancel()
            self.future = None
        self.result = None

    def get_next_move(
        self,
        game_data: GameData,
        res_callback_func: ResCallbackFunc | None = None,
        time_callback_func: TimeCallbackFunc | None = None,
        *,
        reset: bool = False,
    ) -> None:
        """Start running the AI algorithm in the background (separate thread).

        - If a result has been computed, it will be used. No function calls will be made to the AI algorithm.
        - If it is already running, do nothing.
        - If the reset flag is set, the algorithm will be reset and re-evaluated regardless of its current state.

        Calls the callback function with the result when it's done.
        Calls the time callback function when it starts and when it ends.

        ALWAYS CALL THE TIME CALLBACK FUNCTION AFTER THE RESULT CALLBACK FUNCTION,
        SO THAT THE GAME DOESN'T INTERPRET A PREVIOUS RESULT AS THE ONE RETURNED BY THE CURRENT CALL.
        (this is because the game relies on the timer being on or off to determine if the algorithm is still running)

        Args:
            game_data (GameData): The current game state (NOT TO BE CONFUSED WITH THE STATES FROM THE STATE MACHINE).
                This is the data that the AI will use to make its decision while actually playing the game on the board.
            res_callback_func (function, optional): The function to call when the algorithm is done. Defaults to None.
            time_callback_func (function, optional): The function to call when the algorithm starts and when it ends. Defaults to None.
            reset (bool, optional): Whether to reset the stored algorithm results. Defaults to False.

        """
        # After stopping, the algorithm sets the stop_flag to False, and get_next_move() can be called
        if self.stop_flag:
            return
        self.res_callback_func = res_callback_func
        self.time_callback_func = time_callback_func

        # Reset the AI algorithm results (when current state of the game doesn't match state expected for result of the algorithm to be used)
        if reset:
            self.next_state = None
            self.future = None
            self.result = None

        # Needed in _execute_algorithm() when the algorithm is actually run (not every time get_next_move() is called)
        self.current_state = game_data

        # No results yet/anymore, so run the algorithm (again)
        if self.result is None or self.result == []:
            if self.future is None or self.future.done():
                # Run the algorithm in a separate thread
                LOGGER.info(f"[{type(self).__name__}] Submitting algorithm...")
                self.future = executor.submit(
                    self.run_algorithm,
                    infinite=(self.level == Level.INFINITE),
                )
                self.future.add_done_callback(self._on_algorithm_done)

                if self.time_callback_func is not None:
                    # Start time tracking
                    self.time_callback_func()
            else:
                LOGGER.info(f"[{type(self).__name__}] Algorithm already running.")
        else:
            LOGGER.info(f"[{type(self).__name__}] Using stored result.")
            piece_index, piece_position = self._process_result()
            status = (
                AIReturn.FOUND
                if piece_index is not None and piece_position is not None
                else AIReturn.NOT_FOUND
            )
            if self.res_callback_func is not None:
                self.res_callback_func(status, piece_index, piece_position)

    def _on_algorithm_done(self, future: Future[list[TreeNode] | None]) -> None:
        """Handle completion of the algorithm when it has finished running.

        Calls the defined callback functions if they exists.

        Args:
            future (Future): The future object that contains the result of the algorithm.

        """
        LOGGER.info(f"[{type(self).__name__}] Algorithm done.")

        self.result = future.result()

        if self.result is None:
            if self.res_callback_func is not None:
                if self.stop_flag:
                    self.res_callback_func(AIReturn.STOPPED_EARLY, None, None)
                    self.stop_flag = False
                else:
                    self.res_callback_func(AIReturn.NOT_FOUND, None, None)
            if self.time_callback_func is not None:
                # Stop time tracking
                self.time_callback_func()
            return

        piece_index, piece_position = self._process_result()
        status = (
            AIReturn.FOUND
            if piece_index is not None and piece_position is not None
            else AIReturn.NOT_FOUND
        )

        if self.res_callback_func is not None:
            LOGGER.debug(f"[{type(self).__name__}] Calling result callback function...")
            self.res_callback_func(status, piece_index, piece_position)
        else:
            LOGGER.debug(f"[{type(self).__name__}] No result callback function defined.")

        if self.time_callback_func is not None:
            # Stop time tracking
            self.time_callback_func()

    def _process_result(self) -> tuple[int | None, PiecePosition | None]:
        """Process the result of the algorithm to get the next piece index and position."""
        # Always true, given the conditions on which this function is called
        assert self.result is not None

        self.next_state = self.result[0].state
        # Remove the state that is being played from the result (to avoid playing the same move again in the next call)
        self.result = self.result[1:] if len(self.result) > 1 else None

        # Always true, given when this function is called
        assert self.current_state is not None
        assert self.next_state.recent_piece is not None
        for i, piece in enumerate(self.current_state.pieces):
            if self.next_state.recent_piece[0] and self.next_state.recent_piece[0] == piece:
                return i, self.next_state.recent_piece[1]
        return (None, None)

    def run_algorithm(self, *, infinite: bool = False) -> list[TreeNode] | None:
        """Run the AI algorithm and measure its performance (time, memory, states visited).

        Similar to a decorator, this function wraps the actual implementation of the algorithm
        and adds performance measurement.

        Calls the actual implementation of the algorithm.

        Args:
            infinite (bool): Whether to run the algorithm in infinite mode.

        Returns:
            list[TreeNode]: The list of nodes from the root (exclusive) to the goal state (inclusive).

        """
        StateCounter.reset_num_states()

        LOGGER.info(f"[{type(self).__name__}] Running algorithm...")

        tracemalloc.start()
        snapshot_before = tracemalloc.take_snapshot()

        start_time = time.time()
        result = self._execute_algorithm(infinite=infinite)  # Call the actual implementation
        elapsed_time = time.time() - start_time

        snapshot_after = tracemalloc.take_snapshot()
        tracemalloc.stop()

        stats = snapshot_after.compare_to(snapshot_before, "lineno")
        peak_mem = sum(stat.size_diff for stat in stats)

        num_states = StateCounter.get_num_states()

        if result is not None:
            LOGGER.info(f"[{type(self).__name__}] Algorithm completed successfully.")
        else:
            LOGGER.info(
                f"[{type(self).__name__}] Algorithm did not complete successfully. No valid moves found.",
            )

        # Time of storage (to match records between stats and moves)
        irl_timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        if self.level != Level.INFINITE:
            stats_to_file(
                filename=Path(f"{self.__class__.__name__}_stats.csv"),
                irl_timestamp=irl_timestamp,
                level_name=LEVELS_NAMES[self.level],
                elapsed_time=elapsed_time,
                memory_used=peak_mem,
                states_generated=num_states,
                num_moves=len(result) if result else 0,
                finished=bool(result),
            )

            if result is not None:
                moves_to_file(
                    filename=Path(f"{self.__class__.__name__}_moves.csv"),
                    irl_timestamp=irl_timestamp,
                    level_name=LEVELS_NAMES[self.level],
                    elapsed_time=elapsed_time,
                    num_moves=len(result),
                    moves=[
                        (node.state.recent_piece[0], node.state.recent_piece[1])
                        for node in result
                        if node.state.recent_piece is not None
                    ],
                )

        return result

    def _execute_algorithm(self, *, infinite: bool = False) -> list[TreeNode] | None:
        """Run the actual AI algorithm.

        Args:
            infinite (bool): Whether to run the algorithm in infinite mode.

        Returns:
            list[TreeNode]: The list of nodes from the root (exclusive) to the goal state (inclusive).

        """
        raise NotImplementedError(f"{type(self).__name__} must override _execute_algorithm()")

    def order_nodes(self, node: TreeNode) -> list[TreeNode]:
        """Sort nodes to trace the path from root to goal.

        Traverses from the goal state back to the root state. Reverses that order and returns the result.

        Args:
            node (TreeNode): The node containing the goal state or the next state, depending on the algorithm.

        Returns:
            list: The list of nodes from the root (exclusive) to the goal state (inclusive).

        """
        curr_node: TreeNode | None = node

        nodes: list[TreeNode] = []
        while curr_node and curr_node.state != self.current_state:
            nodes.append(curr_node)
            curr_node = curr_node.parent

        # Get the path from the root to the goal state
        nodes.reverse()

        return nodes


class BFSAlgorithm(AIAlgorithm):
    """Implements the Breadth-First Search algorithm (BFS) for the AI to find the next move to play.

    Time Complexity:
        O(b^d * (<complexity of operators_func()> + <complexity of goal_state_func()>) ==
        O(b^d * (p * g^4 + 1)) ==
        O(b^d * p * g^4),
        where:
        - b is the branching factor
        - d is the depth of the solution
        - p is the number of currently playable pieces
        - g is the grid size
    Space Complexity:
        O(b^d), where b is the branching factor and d is the depth of the solution.

    """

    def _execute_algorithm(self, *, infinite: bool = False) -> list[TreeNode] | None:  # noqa: ARG002
        assert self.current_state is not None
        # TODO: If this algorithm is running in infinite mode, we need to handle it differently
        assert self.goal_state_func is not None
        assert self.operators_func is not None

        root = TreeNode(self.current_state)
        queue = deque([root])
        # Contains states, not nodes (to avoid duplicate states reached by different paths)
        visited: set[GameData] = set()

        while queue:
            if self.stop_flag:
                LOGGER.info(f"[{type(self).__name__}] Algorithm stopped early")
                return None

            node = queue.popleft()

            if self.goal_state_func(node.state):
                return self.order_nodes(node)

            for child_state in self.operators_func(node.state):
                if child_state not in visited:
                    child_node = TreeNode(
                        state=child_state,
                        parent=node,
                        path_cost=node.path_cost + 1,
                        depth=node.depth + 1,
                    )
                    node.add_child(child_node)

                    queue.append(child_node)
                    visited.add(child_state)

        return None  # No valid moves found


class DFSAlgorithm(AIAlgorithm):
    """Implements the Depth-First Search algorithm (DFS) for the AI to find the next move to play.

    It uses the iterative version of the algorithm,
    which is more efficient than the recursive version,
    especially for large search trees.

    Time Complexity:
        O(b^m * (<complexity of operators_func()> + <complexity of goal_state_func()>) ==
        O(b^m * (p * g^4 + 1)) ==
        O(b^m * p * g^4),
        where:
        - b is the branching factor
        - m is the maximum depth of the search tree
        - p is the number of currently playable pieces
        - g is the grid size

    Space Complexity:
        O(b * m), where b is the branching factor and m is the maximum depth of the search tree.

    """

    def _execute_algorithm(self, *, infinite: bool = False) -> list[TreeNode] | None:  # noqa: ARG002
        assert self.current_state is not None
        # TODO: If this algorithm is running in infinite mode, we need to handle it differently
        assert self.goal_state_func is not None
        assert self.operators_func is not None

        root = TreeNode(self.current_state)
        stack = [root]
        # Contains states, not nodes (to avoid duplicate states reached by different paths)
        visited: set[GameData] = set()

        while stack:
            if self.stop_flag:  # Check stop flag
                LOGGER.info(f"[{type(self).__name__}] Algorithm stopped early")
                return None

            node = stack.pop()
            if node.state not in visited:
                visited.add(node.state)

                if self.goal_state_func(node.state):
                    return self.order_nodes(node)

                for child_state in self.operators_func(node.state):
                    if child_state not in visited:
                        child_node = TreeNode(
                            state=child_state,
                            parent=node,
                            path_cost=node.path_cost + 1,
                            depth=node.depth + 1,
                        )
                        node.add_child(child_node)

                        stack.append(child_node)

        return None  # No valid moves found


class IterDeepAlgorithm(AIAlgorithm):
    """Implements the Iterative Deepening Search algorithm (IDS) for the AI to find the next move to play.

    Since it uses DFS to visit the nodes, the code uses the iterative version of the DFS,
    which is more efficient than the recursive version,
    especially for large search trees.
    It also uses a depth limit, to limit the search of each DFS, which is better for a large search space.

    Time Complexity:
        O(b^d * (<complexity of operators_func()> + <complexity of goal_state_func()>)
        == O(b^d * (p * g^4 + 1))
        == O(b^d * p * g^4),
        where:
        - b is the branching factor
        - d is the depth of the solution
        - p is the number of currently playable pieces
        - g is the grid size

    Note: b^d is a simplification of the time complexity of the algorithm,
    since it is actually d*b^1 + (d-1)b^2 + (d-2)b^3 + ... + 2b^(d-1) + b^d, therefore the dominant term is b^d.
    Still, because of this, it is less efficient than DFS, since it visits the same nodes multiple times.

    Space Complexity:
        O(b * d), where b is the branching factor and d is the depth of the solution.

    """

    def _execute_algorithm(self, *, infinite: bool = False) -> list[TreeNode] | None:  # noqa: ARG002
        assert self.current_state is not None
        # TODO: If this algorithm is running in infinite mode, we need to handle it differently
        assert self.goal_state_func is not None
        assert self.operators_func is not None

        def depth_limited_search(start_node: TreeNode, limit: int) -> list[TreeNode] | str | None:
            """Perform a depth-limited search."""
            assert self.goal_state_func is not None
            assert self.operators_func is not None

            stack = [start_node]
            # Contains states, not nodes (to avoid duplicate states reached by different paths)
            visited: set[GameData] = set()
            # Track if new nodes were added
            found_new_nodes = False

            while stack:
                if self.stop_flag:
                    LOGGER.info(f"[{type(self).__name__}] Algorithm stopped early")
                    return "STOPPED"

                node = stack.pop()
                if node.state not in visited:
                    visited.add(node.state)

                    if self.goal_state_func(node.state):
                        return self.order_nodes(node)

                    if node.depth < limit:
                        for child_state in self.operators_func(node.state):
                            if child_state not in visited:
                                child_node = TreeNode(
                                    state=child_state,
                                    parent=node,
                                    path_cost=node.path_cost + 1,
                                    depth=node.depth + 1,
                                )
                                node.add_child(child_node)
                                stack.append(child_node)
                                found_new_nodes = True  # We have added a node to the stack, which means that we could look forward into the graph (not the bottom of the stack)

            if found_new_nodes:
                return "NOT YET EXHAUSTED"
            # Even if we increase the depth, we wouldn't find any new nodes, as we already searched whole graph
            # End of depth_limited_search function
            "EXHAUSTED"
            return None

        depth_limit = 1
        while True:
            root = TreeNode(self.current_state)
            result = depth_limited_search(root, depth_limit)
            if isinstance(result, str) and result in {"EXHAUSTED", "STOPPED"}:
                # No new nodes were found, stop searching
                return None
            if isinstance(result, str) and result == "NOT YET EXHAUSTED":
                # When the stack was found empty since we reached the limiting depth and no further children nodes were added
                depth_limit += 1
            else:
                # an answer was found before we reached empty stack
                # can only be a list, but to satisfy mypy
                assert isinstance(result, list)
                return result


class GreedyAlgorithm(AIAlgorithm):
    """Implements the Greedy Search algorithm for the AI to find the next move to play.

    It uses a heuristic function to evaluate the nodes and choose the best one to explore next.

    Time Complexity:
        O(b^m * (<complexity of operators_func()> + <complexity of goal_state_func()> + <complexity of greedy_heuristic()>) ==
        O(b^m * (p * g^4 + 1 + p * g^2 * k)) ==
        O(b^m * p * g^4),
        where:
        - b is the branching factor
        - m is the maximum depth of the search tree
        - p is the number of currently playable pieces
        - g is the grid size
        - k is the number of blocks in the piece (very small, between 1 and 4 for the current available pieces).

    Space Complexity:
        O(b^m), where b is the branching factor and m is the depth of the solution.

    Note: Due to the heuristic function, the algorithm is way more efficient than the Big-O notation suggests,
    as it doesn't explore nearly as many nodes as the worst case scenario.
    Of course, this depends on the quality of the heuristic function, and in this case, it is very good.

    """

    def _execute_algorithm(self, *, infinite: bool = False) -> list[TreeNode] | None:  # noqa: ARG002
        assert self.current_state is not None
        # TODO: If this algorithm is running in infinite mode, we need to handle it differently
        assert self.goal_state_func is not None
        assert self.operators_func is not None

        root = TreeNode(self.current_state)
        pq: PriorityQueue[TreeNode] = PriorityQueue()
        pq.put(root)
        # Contains states, not nodes (to avoid duplicate states reached by different paths)
        visited: set[GameData] = set()

        # Inherit the score from the parent node
        inheritance = True

        while not pq.empty():
            if self.stop_flag:
                LOGGER.info(f"[{type(self).__name__}] Algorithm stopped early")
                return None

            node = pq.get()

            if self.goal_state_func(node.state):
                return self.order_nodes(node)

            for child_state in self.operators_func(node.state):
                if child_state not in visited:
                    child_node = TreeNode(
                        state=child_state,
                        parent=node,
                        path_cost=node.path_cost + 1,
                        depth=node.depth + 1,
                        heuristic_score=greedy_heuristic(
                            parent=node,
                            current=child_state,
                            total_blocks=root.state.blocks_to_break,
                            inheritance=inheritance,
                        ),
                    )
                    node.add_child(child_node)

                    pq.put(child_node)
                    visited.add(child_state)

        return None  # No valid moves found


class SingleDepthGreedyAlgorithm(AIAlgorithm):
    """Implements the Single Depth Greedy Search algorithm for the AI to find the next move to play among only the first level of children nodes.

    It uses a heuristic function to evaluate the nodes and choose the best one to explore next.
    It is a simplified version of the Greedy Search algorithm, which only explores the first level of children nodes.

    Time Complexity:
        O(b * (<complexity of operators_func()> + <complexity of heuristic_func()>)) ==
        O(b * (p * g^4 + p * g^2 * k)),
        where:
        - b is the branching factor (number of possible moves)
        - p is the number of currently playable pieces
        - g is the grid size
        - k is the number of blocks in the piece.

    Space Complexity:
        O(b), where b is the branching factor.

    """

    def _execute_algorithm(self, *, infinite: bool = False) -> list[TreeNode] | None:  # noqa: ARG002
        assert self.current_state is not None
        # TODO: If this algorithm is not running in infinite mode, we need to handle it differently
        assert self.goal_state_func is None
        assert self.operators_func is not None

        root = TreeNode(self.current_state)
        best_node = None  # Track the best node based on the heuristic score

        # Explore all child states (depth 1)
        for child_state in self.operators_func(root.state):
            # Create a child node for each possible move
            child_node = TreeNode(
                state=child_state,
                parent=root,
                path_cost=1,
                depth=1,
                heuristic_score=infinite_heuristic(parent=root, current=child_state),
            )
            root.add_child(child_node)

            # Update the best node if this child has a better heuristic score
            if best_node is None or child_node.heuristic_score < best_node.heuristic_score:
                best_node = child_node

        if best_node is None:
            LOGGER.info("Couldn't find any valid moves")
            return None

        # Return the best node found
        return self.order_nodes(best_node)


class AStarAlgorithm(AIAlgorithm):
    """Implements the A* Search algorithm for the AI to find the next move to play.

    It uses a heuristic function and the cost from the starting node to the current one to evaluate the nodes and choose the best one to explore next.

    Time Complexity:
        O(b^d * (<complexity of operators_func()> + <complexity of goal_state_func()> + <complexity of a_star_heuristic()>) ==
        O(b^d * (p * g^4 + 1 + g^2)) ==
        O(b^d * p * g^4),
        where:
        - b is the branching factor
        - d is the depth of the solution
        - p is the number of currently playable pieces
        - g is the grid size

    Space Complexity:
        O(b^d), where b is the branching factor and d is the depth of the solution.

    Note: Due to the heuristic function, this algorithm is way more efficient than the Big-O notation suggests,
    as it doesn't explore nearly as many nodes as the worst case scenario, due to the heuristic function.
    However, unlike the Greedy Search algorithm, this algorithm is guaranteed to find the optimal solution,
    if the heuristic function is admissible - WHICH IT IS, in this case.
    The heuristic function is admissible if it never overestimates the cost to reach the goal state from the current state.
    The quality of the heuristic function is very important for the performance of the algorithm, as it determines how many nodes are explored.
    And the closer it is to the actual cost, the better the performance of the algorithm.

    """

    def _execute_algorithm(self, *, infinite: bool = False) -> list[TreeNode] | None:  # noqa: ARG002
        assert self.current_state is not None
        # TODO: If this algorithm is running in infinite mode, we need to handle it differently
        assert self.goal_state_func is not None
        assert self.operators_func is not None

        root = TreeNode(self.current_state)
        pq: PriorityQueue[TreeNode] = PriorityQueue()
        pq.put(root)
        # Contains states, not nodes (to avoid duplicate states reached by different paths)
        visited: set[GameData] = set()

        while not pq.empty():
            if self.stop_flag:
                LOGGER.info(f"[{type(self).__name__}] Algorithm stopped early")
                return None

            node = pq.get()

            if self.goal_state_func(node.state):
                return self.order_nodes(node)

            for child_state in self.operators_func(node.state):
                if child_state not in visited:
                    child_node = TreeNode(
                        state=child_state,
                        parent=node,
                        path_cost=node.path_cost + 1,
                        depth=node.depth + 1,
                        heuristic_score=a_star_heuristic(child_state) + (node.path_cost + 1),
                    )
                    node.add_child(child_node)

                    pq.put(child_node)
                    visited.add(child_state)

        # No valid moves found
        return None


class WeightedAStarAlgorithm(AIAlgorithm):
    """Implements the Weighted A* Search algorithm for the AI to find the next move to play.

    It uses a heuristic function and the cost from the starting node to the current one to evaluate the nodes and choose the best one to explore next.
    The heuristic function is weighted to make the algorithm more aggressive in its search (higher weight == more aggressive search).

    Time Complexity:
        O(b^d * (<complexity of operators_func()> + <complexity of goal_state_func()> + <complexity of a_star_heuristic()>) ==
        O(b^d * (p * g^4 + 1 + g^2)) == O(b^d * p * g^4), where:
        - b is the branching factor
        - d is the depth of the solution
        - p is the number of currently playable pieces
        - g is the grid size

    Space Complexity:
        O(b^d), where b is the branching factor and d is the depth of the solution.

    Note: Due to the heuristic function, this algorithm is way more efficient than the Big-O notation suggests, as it doesn't explore nearly as many nodes as the worst case scenario, due to the heuristic function.
    Due to the weighted heuristic function, this algorithm is more aggressive than the A* Search algorithm, which means that it will explore less nodes and find the solution faster, but it is not guaranteed to find the optimal solution, but it will find a satisfactory solution in a reasonable amount of time.

    """

    def _execute_algorithm(self, *, infinite: bool = False) -> list[TreeNode] | None:  # noqa: ARG002
        assert self.current_state is not None
        # TODO: If this algorithm is running in infinite mode, we need to handle it differently
        assert self.goal_state_func is not None
        assert self.operators_func is not None

        root = TreeNode(self.current_state)
        pq: PriorityQueue[TreeNode] = PriorityQueue()
        pq.put(root)
        # Contains states, not nodes (to avoid duplicate states reached by different paths)
        visited: set[GameData] = set()
        weight = 4

        while not pq.empty():
            if self.stop_flag:
                LOGGER.info(f"[{type(self).__name__}] Algorithm stopped early")
                return None

            node = pq.get()

            if self.goal_state_func(node.state):
                return self.order_nodes(node)

            for child_state in self.operators_func(node.state):
                if child_state not in visited:
                    child_node = TreeNode(
                        state=child_state,
                        parent=node,
                        path_cost=node.path_cost + 1,
                        depth=node.depth + 1,
                        heuristic_score=a_star_heuristic(child_state) * weight
                        + (node.path_cost + 1),
                    )
                    node.add_child(child_node)

                    pq.put(child_node)
                    visited.add(child_state)

        return None  # No valid moves found


def _register_algorithms() -> None:
    """Automatically register all AIAlgorithm subclasses with the registry using AIAlgorithmID."""
    for subclass in AIAlgorithm.__subclasses__():
        # Normalize class name: remove 'algorithm', lowercase, remove underscores
        class_key = subclass.__name__.replace("Algorithm", "").replace("_", "").lower()
        for algo_type in AIAlgorithmID:
            # Normalize enum name: lowercase, remove underscores
            enum_key = algo_type.name.replace("_", "").lower()
            if class_key == enum_key:
                AIAlgorithmRegistry.register(algo_type, subclass)
                break


_register_algorithms()
