from __future__ import annotations

import copy
import logging
import math
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeVar

import pygame

from woodblock.ai.algorithm_registry import get_ai_algorithm

# Extremely important to import the AI algorithms here, otherwise they won't be registered (even though they don't seem to be used.
# This is because algorithm_registry abstracts them
from woodblock.ai.algorithms import (
    AIAlgorithm,  # noqa: F401
    AStarAlgorithm,  # noqa: F401
    BFSAlgorithm,  # noqa: F401
    DFSAlgorithm,  # noqa: F401
    GreedyAlgorithm,  # noqa: F401
    IterDeepAlgorithm,  # noqa: F401
    SingleDepthGreedyAlgorithm,  # noqa: F401
    WeightedAStarAlgorithm,  # noqa: F401
)
from woodblock.assets.assets import Assets
from woodblock.game_data import GameData
from woodblock.game_logic.constants import (
    AI_ALGO_NAMES,
    LEVELS,
    AIAlgorithmID,
    AIPiecePosition,
    AIReturn,
    BoardConfig,
    ColorConfig,
    Level,
    PathConfig,
    Piece,
    PieceListOffset,
    PiecePosition,
    PlayerType,
    ScreenConfig,
)
from woodblock.game_logic.rules import (
    clear_full_lines,
    is_valid_position,
    no_more_valid_moves,
    place_piece,
)
from woodblock.utils.file import get_recent_files
from woodblock.utils.misc import QuitGameException
from woodblock.utils.ui import draw_board, draw_piece, draw_score

if TYPE_CHECKING:
    from pathlib import Path

    from woodblock.game import Game

LOGGER = logging.getLogger(__name__)

T = TypeVar("T", bound="GameState")


class GameStateManager:
    """Manages the game states' stack.

    Attributes:
        state_stack (list[GameState]): The stack of game states

    """

    def __init__(self) -> None:
        self.state_stack: list[GameState] = []

    def safe_enter(self, *, raise_error: bool = False) -> bool:
        """Enter the current state safely. Handling when it cannot be entered (is None).

        Args:
            raise_error (bool): Whether to raise an error if the state cannot be entered

        Returns:
            bool: True if the state was entered, False otherwise

        """
        if self.current_state is not None:
            self.current_state.enter()
            return True

        if raise_error:
            raise ValueError("Failed to enter state")
        return False

    def safe_exit(self, *, raise_error: bool = False) -> bool:
        """Exit the current state safely. Handling when it cannot be exited (is None).

        Args:
            raise_error (bool): Whether to raise an error if the state cannot be exited

        Returns:
            bool: True if the state was exited, False otherwise

        """
        if self.current_state is not None:
            self.current_state.exit()
            return True

        if raise_error:
            raise ValueError("Failed to exit state")
        return False

    def has_states(self) -> bool:
        """Check if there are any states in the stack.

        Returns:
            bool: True if there are states in the stack, False otherwise

        """
        return bool(self.state_stack)

    def switch_to_base_state(self, new_state: GameState) -> None:
        """Switch to a new state and remove all previous states.

        Args:
            new_state (GameState): The new state to switch to

        """
        self.clear_states()
        self.state_stack = [new_state]
        self.safe_enter()

    def push_state(self, new_state: GameState, *, exit_current: bool = True) -> None:
        """Push a new state to the stack.

        Args:
            new_state (GameState): The new state to push
            exit_current (bool): Whether to exit the current state

        """
        if exit_current:
            self.safe_exit()
        self.state_stack.append(new_state)
        self.safe_enter()

    def pop_state(self, times: int = 1, *, enter_current: bool = True) -> bool:
        """Pop the current state.

        Args:
            times (int): The number of times to pop the state
            enter_current (bool): Whether to enter the current state after popping

        Returns:
            bool: True if the state was popped, False otherwise

        """
        popped = False
        for _ in range(times):
            if self.current_state is not None:
                self.safe_exit()
                self.state_stack.pop()
                popped = True
            else:
                break

        if enter_current:
            self.safe_enter()

        return popped

    def subst_below_switch_to(self, new_state: GameState) -> bool:
        """Remove the current state and substitute the one below it with a new state.

        Args:
            new_state (GameState): The new state to switch to

        Returns:
            bool: True if the state was switched, False otherwise

        """
        if len(self.state_stack) > 1:
            self.pop_state(2, enter_current=False)
            self.push_state(new_state, exit_current=False)
            return True
        return False

    def _pop_until_with_offset(self, state: type[T], additional_pops: int) -> T:
        """Pop until target state, then pop additional times (helper method).

        Args:
            state (Type[T]): The target state to find
            additional_pops (int): Additional pops to perform after finding target

        Returns:
            T: The current state after all pops

        Raises:
            ValueError: If the target state is not found

        """
        while self.current_state is not None and not isinstance(self.current_state, state):
            self.pop_state(enter_current=False)

        if self.current_state is None:
            raise ValueError("Failed to pop until target state")

        if additional_pops > 0:
            self.pop_state(additional_pops)

        if self.current_state is None:
            raise ValueError("Failed to pop until target state")

        self.safe_enter(raise_error=True)
        return self.current_state

    def pop_until(self, state: type[T]) -> T:
        """Pop states until the target state is reached.

        Args:
            state (Type[T]): The target state to pop until
                Upper-bounded by GameState: it can only be a GameState or its subclasses

        Returns:
            T: The state that was reached

        Raises:
            ValueError: If the target state is not found

        """
        return self._pop_until_with_offset(state, 0)

    def pop_beyond(self, state: type[T], times: int) -> T:
        """Pop states beyond the target state.

        Args:
            state (Type[T]): The target state to find first.
                Upper-bounded by GameState: it can only be a GameState or its subclasses
            times (int): The number of times to pop beyond the target state

        Returns:
            T | None: The current state after popping, or None if stack is empty

        Raises:
            ValueError: If the target state is not found

        """
        return self._pop_until_with_offset(state, times)

    def clear_states(self) -> None:
        """Clear all states."""
        self.pop_state(len(self.state_stack))

    @property
    def current_state(self) -> GameState | None:
        """Get the current state.

        Returns:
            GameState | None: The current state, or None if there are no states in the stack

        """
        return self.state_stack[-1] if self.state_stack else None


class GameState(ABC):
    """Abstract base class for all game states."""

    # Each subclass stores its Model

    @abstractmethod
    def enter(self) -> None:
        """Call when the game state is entered.

        Used for debugging, possible transition effects and other initializations separate from the constructor

        """

    @abstractmethod
    def update(self, game: Game, events: list[pygame.event.Event]) -> None:
        """Update the game state.

        Args:
            game (Game): The Game object
            events (list[pygame.event.Event]): The events that have occurred

        Raises:
            QuitGameException: If the game is quit

        """

    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """View that renders the game state.

        Args:
            screen (pygame.Surface): The screen to render on

        """

    @abstractmethod
    def exit(self) -> None:
        """Call when the game state is exited.

        Used for debugging, possible transition effects and other clean-up operations.

        """


# ========================================
# Concrete Game States
# ========================================
class MainMenuState(GameState):
    """Main menu of the game."""

    def enter(self) -> None:  # noqa: D102
        LOGGER.debug("Entering Main Menu")

    def update(self, game: Game, events: list[pygame.event.Event]) -> None:  # noqa: D102
        if not game.state_manager.has_states():
            raise ValueError("Unexpected divergence in game state stack")

        for event in events:
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and (event.key in {pygame.K_ESCAPE, pygame.K_q})
            ):
                raise QuitGameException
            if event.type == pygame.MOUSEBUTTONDOWN or (
                event.type == pygame.KEYDOWN and event.key != pygame.K_ESCAPE
            ):
                game.state_manager.push_state(SelectPlayerState())

    def render(self, screen: pygame.Surface) -> None:  # noqa: D102
        title_text_back = Assets.fonts["title"].render("Wood Block", True, ColorConfig.BROWN)
        title_text_middle = Assets.fonts["title"].render("Wood Block", True, ColorConfig.ORANGE)
        title_text_front = Assets.fonts["title"].render("Wood Block", True, ColorConfig.WHITE)
        start_text = Assets.fonts["text"].render(
            "* Click Anywhere to Start *",
            True,
            ColorConfig.WHITE,
        )

        # Non-interactable rectangles
        title_rect_back = title_text_back.get_rect(
            center=((screen.get_width() // 2) + 5, (screen.get_height() // 4) - 5),
        )
        title_rect_middle = title_text_middle.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 4),
        )
        title_rect_front = title_text_front.get_rect(
            center=((screen.get_width() // 2) - 5, (screen.get_height() // 4) + 5),
        )
        start_rect = start_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 1.35),
        )

        screen.blit(Assets.backgrounds["menu"], (0, 0))
        screen.blit(
            Assets.icons["menu_game"], (ScreenConfig.WIDTH / 2 - 100, ScreenConfig.HEIGHT / 2 - 100)
        )
        screen.blit(title_text_back, title_rect_back)
        screen.blit(title_text_middle, title_rect_middle)
        screen.blit(title_text_front, title_rect_front)
        screen.blit(start_text, start_rect)
        pygame.display.flip()

    def exit(self) -> None:  # noqa: D102
        LOGGER.debug("Exiting Main Menu")


class SelectPlayerState(GameState):
    """Menu to select either player mode or AI mode."""

    def __init__(self) -> None:
        self.keyboard_active = False
        self.selected_option: int | None = None
        self.player_rect: pygame.Rect | None = None
        self.ai_rect: pygame.Rect | None = None
        self.back_rect: pygame.Rect | None = None

    def enter(self) -> None:  # noqa: D102
        LOGGER.debug("Entering Select Player Menu")
        self.keyboard_active = False
        self.selected_option = None

    def update(self, game: Game, events: list[pygame.event.Event]) -> None:  # noqa: D102
        assert self.player_rect is not None
        assert self.ai_rect is not None
        assert self.back_rect is not None

        if not game.state_manager.has_states():
            raise ValueError("Unexpected divergence in game state stack")

        for event in events:
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                raise QuitGameException
            # Mouse click events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.player_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectAIAlgorithmState(PlayerType.HUMAN))
                elif self.ai_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectAIAlgorithmState(PlayerType.AI))
                elif self.back_rect.collidepoint(event.pos):
                    game.state_manager.pop_state()
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key in [
                    pygame.K_UP,
                    pygame.K_w,
                    pygame.K_DOWN,
                    pygame.K_s,
                    pygame.K_RETURN,
                    pygame.K_SPACE,
                ]:
                    self.keyboard_active = True

                if event.key == pygame.K_ESCAPE:
                    game.state_manager.pop_state()
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option - 1) % 3
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option + 1) % 3
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_option == 0:
                        game.state_manager.push_state(SelectAIAlgorithmState(PlayerType.HUMAN))
                    elif self.selected_option == 1:
                        game.state_manager.push_state(SelectAIAlgorithmState(PlayerType.AI))
                    elif self.selected_option == 2:
                        game.state_manager.pop_state()

        # Update selected option based on mouse position
        # Must be after the keyboard events to avoid overriding the selected option (mouse has priority)
        mouse_pos = pygame.mouse.get_pos()
        if self.player_rect.collidepoint(mouse_pos):
            self.selected_option = 0
        elif self.ai_rect.collidepoint(mouse_pos):
            self.selected_option = 1
        elif self.back_rect.collidepoint(mouse_pos):
            self.selected_option = 2
        elif not self.keyboard_active:
            self.selected_option = None

    def render(self, screen: pygame.Surface) -> None:  # noqa: D102
        title_text_back = Assets.fonts["title"].render("Wood Block", True, ColorConfig.BROWN)
        title_text_middle = Assets.fonts["title"].render("Wood Block", True, ColorConfig.ORANGE)
        title_text_front = Assets.fonts["title"].render("Wood Block", True, ColorConfig.WHITE)
        subtitle_text = Assets.fonts["subtitle"].render(
            "Select The Player",
            True,
            ColorConfig.BROWN,
        )
        player_text = Assets.fonts["subtitle"].render(
            "Human",
            True,
            ColorConfig.ORANGE if self.selected_option == 0 else ColorConfig.WHITE,
        )
        ai_text = Assets.fonts["subtitle"].render(
            "AI",
            True,
            ColorConfig.ORANGE if self.selected_option == 1 else ColorConfig.WHITE,
        )
        back_text = Assets.fonts["subtitle"].render(
            "Go Back",
            True,
            ColorConfig.ORANGE if self.selected_option == 2 else ColorConfig.WHITE,
        )

        # Non-interactable rectangles
        title_rect_back = title_text_back.get_rect(
            center=((screen.get_width() // 2) + 5, (screen.get_height() // 4) - 5),
        )
        title_rect_middle = title_text_middle.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 4),
        )
        title_rect_front = title_text_front.get_rect(
            center=((screen.get_width() // 2) - 5, (screen.get_height() // 4) + 5),
        )
        subtitle_rect = subtitle_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2.65),
        )

        # Interactable rectangles
        self.player_rect = player_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2.1),
        )
        self.ai_rect = ai_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 1.7),
        )
        self.back_rect = back_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 1.20),
        )

        screen.blit(Assets.backgrounds["menu"], (0, 0))
        screen.blit(title_text_back, title_rect_back)
        screen.blit(title_text_middle, title_rect_middle)
        screen.blit(title_text_front, title_rect_front)
        screen.blit(subtitle_text, subtitle_rect)
        screen.blit(player_text, self.player_rect)
        screen.blit(ai_text, self.ai_rect)
        screen.blit(back_text, self.back_rect)
        pygame.display.flip()

    def exit(self) -> None:  # noqa: D102
        LOGGER.debug("Exiting Select Player Menu")


class SelectAIAlgorithmState(GameState):
    """Menu to select the AI algorithm (for player mode's hints or for AI mode)."""

    def __init__(self, player: PlayerType) -> None:
        self.player = player

        self.keyboard_active = False
        self.selected_option: int | None = None
        self.bfs_rect: pygame.Rect | None = None
        self.dfs_rect: pygame.Rect | None = None
        self.iter_deep_rect: pygame.Rect | None = None
        self.greedy_rect: pygame.Rect | None = None
        self.a_star_rect: pygame.Rect | None = None
        self.weighted_a_star_rect: pygame.Rect | None = None
        self.back_rect: pygame.Rect | None = None

    def enter(self) -> None:  # noqa: D102
        LOGGER.debug("Entering Select AI Algorithm Menu")
        self.keyboard_active = False
        self.selected_option = None

    def update(self, game: Game, events: list[pygame.event.Event]) -> None:  # noqa: D102
        assert self.bfs_rect is not None
        assert self.dfs_rect is not None
        assert self.iter_deep_rect is not None
        assert self.greedy_rect is not None
        assert self.a_star_rect is not None
        assert self.weighted_a_star_rect is not None
        assert self.back_rect is not None

        if not game.state_manager.has_states():
            raise ValueError("Unexpected divergence in game state stack")

        for event in events:
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                raise QuitGameException
            # Mouse click events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.bfs_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectModeState(self.player, AIAlgorithmID.BFS))
                elif self.dfs_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectModeState(self.player, AIAlgorithmID.DFS))
                elif self.iter_deep_rect.collidepoint(event.pos):
                    game.state_manager.push_state(
                        SelectModeState(self.player, AIAlgorithmID.ITER_DEEP),
                    )
                elif self.greedy_rect.collidepoint(event.pos):
                    game.state_manager.push_state(
                        SelectModeState(self.player, AIAlgorithmID.GREEDY),
                    )
                elif self.a_star_rect.collidepoint(event.pos):
                    game.state_manager.push_state(
                        SelectModeState(self.player, AIAlgorithmID.A_STAR),
                    )
                elif self.weighted_a_star_rect.collidepoint(event.pos):
                    game.state_manager.push_state(
                        SelectModeState(self.player, AIAlgorithmID.WEIGHTED_A_STAR),
                    )
                elif self.back_rect.collidepoint(event.pos):
                    game.state_manager.pop_state()
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key in [
                    pygame.K_UP,
                    pygame.K_w,
                    pygame.K_DOWN,
                    pygame.K_s,
                    pygame.K_RETURN,
                    pygame.K_SPACE,
                ]:
                    self.keyboard_active = True

                if event.key == pygame.K_ESCAPE:
                    game.state_manager.pop_state()
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option - 1) % 7
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option + 1) % 7
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_option == 0:
                        game.state_manager.push_state(
                            SelectModeState(self.player, AIAlgorithmID.BFS),
                        )
                    elif self.selected_option == 1:
                        game.state_manager.push_state(
                            SelectModeState(self.player, AIAlgorithmID.DFS),
                        )
                    elif self.selected_option == 2:
                        game.state_manager.push_state(
                            SelectModeState(self.player, AIAlgorithmID.ITER_DEEP),
                        )
                    elif self.selected_option == 3:
                        game.state_manager.push_state(
                            SelectModeState(self.player, AIAlgorithmID.GREEDY),
                        )
                    elif self.selected_option == 4:
                        game.state_manager.push_state(
                            SelectModeState(self.player, AIAlgorithmID.A_STAR),
                        )
                    elif self.selected_option == 5:
                        game.state_manager.push_state(
                            SelectModeState(self.player, AIAlgorithmID.WEIGHTED_A_STAR),
                        )
                    elif self.selected_option == 6:
                        game.state_manager.pop_state()

        # Update selected option based on mouse position
        # Must be after the keyboard events to avoid overriding the selected option (mouse has priority)
        mouse_pos = pygame.mouse.get_pos()
        if self.bfs_rect.collidepoint(mouse_pos):
            self.selected_option = 0
        elif self.dfs_rect.collidepoint(mouse_pos):
            self.selected_option = 1
        elif self.iter_deep_rect.collidepoint(mouse_pos):
            self.selected_option = 2
        elif self.greedy_rect.collidepoint(mouse_pos):
            self.selected_option = 3
        elif self.a_star_rect.collidepoint(mouse_pos):
            self.selected_option = 4
        elif self.weighted_a_star_rect.collidepoint(mouse_pos):
            self.selected_option = 5
        elif self.back_rect.collidepoint(mouse_pos):
            self.selected_option = 6
        elif not self.keyboard_active:
            self.selected_option = None

    def render(self, screen: pygame.Surface) -> None:  # noqa: D102
        title_text_back = Assets.fonts["title"].render("Wood Block", True, ColorConfig.BROWN)
        title_text_middle = Assets.fonts["title"].render("Wood Block", True, ColorConfig.ORANGE)
        title_text_front = Assets.fonts["title"].render("Wood Block", True, ColorConfig.WHITE)
        subtitle_text = Assets.fonts["subtitle"].render(
            "Select The AI Algorithm",
            True,
            ColorConfig.BROWN,
        )
        bfs_text = Assets.fonts["text"].render(
            "Breadth First Search",
            True,
            ColorConfig.ORANGE if self.selected_option == 0 else ColorConfig.WHITE,
        )
        dfs_text = Assets.fonts["text"].render(
            "Depth First Search",
            True,
            ColorConfig.ORANGE if self.selected_option == 1 else ColorConfig.WHITE,
        )
        iter_deep_text = Assets.fonts["text"].render(
            "Iterative Deepening",
            True,
            ColorConfig.ORANGE if self.selected_option == 2 else ColorConfig.WHITE,
        )
        greedy_text = Assets.fonts["text"].render(
            "Greedy Search",
            True,
            ColorConfig.ORANGE if self.selected_option == 3 else ColorConfig.WHITE,
        )
        a_star_text = Assets.fonts["text"].render(
            "A*",
            True,
            ColorConfig.ORANGE if self.selected_option == 4 else ColorConfig.WHITE,
        )
        weighted_a_star_text = Assets.fonts["text"].render(
            "Weighted A*",
            True,
            ColorConfig.ORANGE if self.selected_option == 5 else ColorConfig.WHITE,
        )
        back_text = Assets.fonts["subtitle"].render(
            "Go Back",
            True,
            ColorConfig.ORANGE if self.selected_option == 6 else ColorConfig.WHITE,
        )

        # Non-interactable rectangles
        title_rect_back = title_text_back.get_rect(
            center=((screen.get_width() // 2) + 5, (screen.get_height() // 4) - 5),
        )
        title_rect_middle = title_text_middle.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 4),
        )
        title_rect_front = title_text_front.get_rect(
            center=((screen.get_width() // 2) - 5, (screen.get_height() // 4) + 5),
        )
        subtitle_rect = subtitle_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2.65),
        )

        # Interactable rectangles
        self.bfs_rect = bfs_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2.1),
        )
        self.dfs_rect = dfs_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 1.85),
        )
        self.iter_deep_rect = iter_deep_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 1.67),
        )
        self.greedy_rect = greedy_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 1.52),
        )
        self.a_star_rect = a_star_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 1.4),
        )
        self.weighted_a_star_rect = weighted_a_star_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 1.3),
        )
        self.back_rect = back_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 1.17),
        )

        screen.blit(Assets.backgrounds["menu"], (0, 0))
        screen.blit(title_text_back, title_rect_back)
        screen.blit(title_text_middle, title_rect_middle)
        screen.blit(title_text_front, title_rect_front)
        screen.blit(subtitle_text, subtitle_rect)
        screen.blit(bfs_text, self.bfs_rect)
        screen.blit(dfs_text, self.dfs_rect)
        screen.blit(iter_deep_text, self.iter_deep_rect)
        screen.blit(greedy_text, self.greedy_rect)
        screen.blit(a_star_text, self.a_star_rect)
        screen.blit(weighted_a_star_text, self.weighted_a_star_rect)
        screen.blit(back_text, self.back_rect)
        pygame.display.flip()

    def exit(self) -> None:  # noqa: D102
        LOGGER.debug("Exiting Select AI Algorithm Menu")


class SelectModeState(GameState):
    """Menu to select the game mode (Levels or Infinite)."""

    def __init__(self, player: PlayerType, ai_algorithm: AIAlgorithmID) -> None:
        self.player = player
        self.ai_algorithm = ai_algorithm

        self.keyboard_active = False
        self.selected_option: int | None = None
        self.levels_rect: pygame.Rect | None = None
        self.infinite_rect: pygame.Rect | None = None
        self.quit_rect: pygame.Rect | None = None

    def enter(self) -> None:  # noqa: D102
        LOGGER.debug("Entering Select Mode Menu")
        self.keyboard_active = False
        self.selected_option = None

    def update(self, game: Game, events: list[pygame.event.Event]) -> None:  # noqa: D102
        assert self.levels_rect is not None
        assert self.infinite_rect is not None
        assert self.quit_rect is not None

        if not game.state_manager.has_states():
            raise ValueError("Unexpected divergence in game state stack")

        for event in events:
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                raise QuitGameException
            # Mouse click events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.levels_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectLevelState(self.player, self.ai_algorithm))
                elif self.infinite_rect.collidepoint(event.pos):
                    game.state_manager.push_state(
                        GameplayState(self.player, self.ai_algorithm, Level.INFINITE),
                    )
                elif self.quit_rect.collidepoint(event.pos):
                    game.state_manager.pop_state()
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key in [
                    pygame.K_UP,
                    pygame.K_w,
                    pygame.K_DOWN,
                    pygame.K_s,
                    pygame.K_RETURN,
                    pygame.K_SPACE,
                ]:
                    self.keyboard_active = True

                if event.key == pygame.K_ESCAPE:
                    game.state_manager.pop_state()
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option - 1) % 3
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option + 1) % 3
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_option == 0:
                        game.state_manager.push_state(
                            SelectLevelState(self.player, self.ai_algorithm),
                        )
                    elif self.selected_option == 1:
                        game.state_manager.push_state(
                            GameplayState(self.player, self.ai_algorithm, Level.INFINITE),
                        )
                    elif self.selected_option == 2:
                        game.state_manager.pop_state()

        # Update selected option based on mouse position
        # Must be after the keyboard events to avoid overriding the selected option (mouse has priority)
        mouse_pos = pygame.mouse.get_pos()
        if self.levels_rect.collidepoint(mouse_pos):
            self.selected_option = 0
        elif self.infinite_rect.collidepoint(mouse_pos):
            self.selected_option = 1
        elif self.quit_rect.collidepoint(mouse_pos):
            self.selected_option = 2
        elif not self.keyboard_active:
            self.selected_option = None

    def render(self, screen: pygame.Surface) -> None:  # noqa: D102
        title_text_back = Assets.fonts["title"].render(
            "Wood Block",
            True,
            ColorConfig.BROWN,
        )
        title_text_middle = Assets.fonts["title"].render(
            "Wood Block",
            True,
            ColorConfig.ORANGE,
        )
        title_text_front = Assets.fonts["title"].render(
            "Wood Block",
            True,
            ColorConfig.WHITE,
        )
        subtitle_text = Assets.fonts["subtitle"].render(
            "Select The Game Mode",
            True,
            ColorConfig.BROWN,
        )
        levels_text = Assets.fonts["text"].render(
            "Levels",
            True,
            ColorConfig.ORANGE if self.selected_option == 0 else ColorConfig.WHITE,
        )
        infinite_text = Assets.fonts["text"].render(
            "Infinite",
            True,
            ColorConfig.ORANGE if self.selected_option == 1 else ColorConfig.WHITE,
        )
        back_text = Assets.fonts["subtitle"].render(
            "Go Back",
            True,
            ColorConfig.ORANGE if self.selected_option == 2 else ColorConfig.WHITE,
        )

        # Non-interactable rectangles
        title_rect_back = title_text_back.get_rect(
            center=((screen.get_width() // 2) + 5, (screen.get_height() // 4) - 5),
        )
        title_rect_middle = title_text_middle.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 4),
        )
        title_rect_front = title_text_front.get_rect(
            center=((screen.get_width() // 2) - 5, (screen.get_height() // 4) + 5),
        )
        subtitle_rect = subtitle_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2.65),
        )

        # Interactable rectangles
        self.levels_rect = levels_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2.1),
        )
        self.infinite_rect = infinite_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 1.7),
        )
        self.quit_rect = back_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 1.20),
        )

        screen.blit(Assets.backgrounds["menu"], (0, 0))
        screen.blit(title_text_back, title_rect_back)
        screen.blit(title_text_middle, title_rect_middle)
        screen.blit(title_text_front, title_rect_front)
        screen.blit(subtitle_text, subtitle_rect)
        screen.blit(levels_text, self.levels_rect)
        screen.blit(infinite_text, self.infinite_rect)
        screen.blit(back_text, self.quit_rect)
        pygame.display.flip()

    def exit(self) -> None:  # noqa: D102
        LOGGER.debug("Exiting Select Mode Menu")


class SelectLevelState(GameState):
    """Menu to select the game level for the Levels mode."""

    def __init__(self, player: PlayerType, ai_algorithm: AIAlgorithmID) -> None:
        self.player = player
        self.ai_algorithm = ai_algorithm

        self.keyboard_active = False
        self.selected_option: int | None = None
        self.level_1_rect: pygame.Rect | None = None
        self.level_2_rect: pygame.Rect | None = None
        self.level_3_rect: pygame.Rect | None = None
        self.custom_rect: pygame.Rect | None = None
        self.back_rect: pygame.Rect | None = None

    def enter(self) -> None:  # noqa: D102
        LOGGER.debug("Entering Select Level")
        self.keyboard_active = False
        self.selected_option = None

    def update(self, game: Game, events: list[pygame.event.Event]) -> None:  # noqa: D102
        assert self.level_1_rect is not None
        assert self.level_2_rect is not None
        assert self.level_3_rect is not None
        assert self.custom_rect is not None
        assert self.back_rect is not None

        if not game.state_manager.has_states():
            raise ValueError("Unexpected divergence in game state stack")

        for event in events:
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                raise QuitGameException
            # Mouse click events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.level_1_rect.collidepoint(event.pos):
                    game.state_manager.push_state(
                        GameplayState(self.player, self.ai_algorithm, Level.LEVEL_1),
                    )
                elif self.level_2_rect.collidepoint(event.pos):
                    game.state_manager.push_state(
                        GameplayState(self.player, self.ai_algorithm, Level.LEVEL_2),
                    )
                elif self.level_3_rect.collidepoint(event.pos):
                    game.state_manager.push_state(
                        GameplayState(self.player, self.ai_algorithm, Level.LEVEL_3),
                    )
                elif self.custom_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectCustomState(self.player, self.ai_algorithm))
                elif self.back_rect.collidepoint(event.pos):
                    game.state_manager.pop_state()
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key in [
                    pygame.K_UP,
                    pygame.K_w,
                    pygame.K_DOWN,
                    pygame.K_s,
                    pygame.K_RETURN,
                    pygame.K_SPACE,
                ]:
                    self.keyboard_active = True

                if event.key == pygame.K_ESCAPE:
                    game.state_manager.pop_state()
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option - 1) % 5
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option + 1) % 5
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_option == 0:
                        game.state_manager.push_state(
                            GameplayState(self.player, self.ai_algorithm, Level.LEVEL_1),
                        )
                    elif self.selected_option == 1:
                        game.state_manager.push_state(
                            GameplayState(self.player, self.ai_algorithm, Level.LEVEL_2),
                        )
                    elif self.selected_option == 2:
                        game.state_manager.push_state(
                            GameplayState(self.player, self.ai_algorithm, Level.LEVEL_3),
                        )
                    elif self.selected_option == 3:
                        game.state_manager.push_state(
                            SelectCustomState(self.player, self.ai_algorithm),
                        )
                    elif self.selected_option == 4:
                        game.state_manager.pop_state()

        # Update selected option based on mouse position
        # Must be after the keyboard events to avoid overriding the selected option (mouse has priority)
        mouse_pos = pygame.mouse.get_pos()
        if self.level_1_rect.collidepoint(mouse_pos):
            self.selected_option = 0
        elif self.level_2_rect.collidepoint(mouse_pos):
            self.selected_option = 1
        elif self.level_3_rect.collidepoint(mouse_pos):
            self.selected_option = 2
        elif self.custom_rect.collidepoint(mouse_pos):
            self.selected_option = 3
        elif self.back_rect.collidepoint(mouse_pos):
            self.selected_option = 4
        elif not self.keyboard_active:
            self.selected_option = None

    def render(self, screen: pygame.Surface) -> None:  # noqa: D102
        title_text_back = Assets.fonts["title"].render("Wood Block", True, ColorConfig.BROWN)
        title_text_middle = Assets.fonts["title"].render("Wood Block", True, ColorConfig.ORANGE)
        title_text_front = Assets.fonts["title"].render("Wood Block", True, ColorConfig.WHITE)
        subtitle_text = Assets.fonts["subtitle"].render(
            "Select The Game Level",
            True,
            ColorConfig.BROWN,
        )
        level_1_text = Assets.fonts["text"].render(
            "Level 1",
            True,
            ColorConfig.ORANGE if self.selected_option == 0 else ColorConfig.WHITE,
        )
        level_2_text = Assets.fonts["text"].render(
            "Level 2",
            True,
            ColorConfig.ORANGE if self.selected_option == 1 else ColorConfig.WHITE,
        )
        level_3_text = Assets.fonts["text"].render(
            "Level 3",
            True,
            ColorConfig.ORANGE if self.selected_option == 2 else ColorConfig.WHITE,
        )
        custom_text = Assets.fonts["text"].render(
            "Custom",
            True,
            ColorConfig.ORANGE if self.selected_option == 3 else ColorConfig.WHITE,
        )
        back_text = Assets.fonts["subtitle"].render(
            "Go Back",
            True,
            ColorConfig.ORANGE if self.selected_option == 4 else ColorConfig.WHITE,
        )

        # Non-interactable rectangles
        title_rect_back = title_text_back.get_rect(
            center=((screen.get_width() // 2) + 5, (screen.get_height() // 4) - 5),
        )
        title_rect_middle = title_text_middle.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 4),
        )
        title_rect_front = title_text_front.get_rect(
            center=((screen.get_width() // 2) - 5, (screen.get_height() // 4) + 5),
        )
        subtitle_rect = subtitle_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2.65),
        )

        # Interactable rectangles
        self.level_1_rect = level_1_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2.05),
        )
        self.level_2_rect = level_2_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 1.8),
        )
        self.level_3_rect = level_3_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 1.6),
        )
        self.custom_rect = custom_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 1.4),
        )
        self.back_rect = back_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 1.2),
        )

        screen.blit(Assets.backgrounds["menu"], (0, 0))
        screen.blit(title_text_back, title_rect_back)
        screen.blit(title_text_middle, title_rect_middle)
        screen.blit(title_text_front, title_rect_front)
        screen.blit(subtitle_text, subtitle_rect)
        screen.blit(level_1_text, self.level_1_rect)
        screen.blit(level_2_text, self.level_2_rect)
        screen.blit(level_3_text, self.level_3_rect)
        screen.blit(custom_text, self.custom_rect)
        screen.blit(back_text, self.back_rect)
        pygame.display.flip()

    def exit(self) -> None:  # noqa: D102
        LOGGER.debug("Exiting Select Level")


class SelectCustomState(GameState):
    """Menu to select a custom game state from the most recent files in the custom folder."""

    def __init__(self, player: PlayerType, algorithm: AIAlgorithmID) -> None:
        self.player = player
        self.algorithm = algorithm

        self.keyboard_active = False
        self.selected_option: int | None = None
        self.file_rects: list[pygame.Rect] = []
        self.back_rect: pygame.Rect | None = None
        self.custom_files: list[Path] = []

    def enter(self) -> None:  # noqa: D102
        LOGGER.debug("Entering Select Custom Menu")
        self.keyboard_active = False
        self.selected_option = None
        self.custom_files = get_recent_files(PathConfig.CUSTOM, 4)

    def update(self, game: Game, events: list[pygame.event.Event]) -> None:  # noqa: D102
        assert self.back_rect is not None

        if not game.state_manager.has_states():
            raise ValueError("Unexpected divergence in game state stack")

        for event in events:
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                raise QuitGameException
            # Mouse click events
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(self.file_rects):
                    if rect.collidepoint(event.pos):
                        game.state_manager.push_state(
                            GameplayState(
                                self.player,
                                self.algorithm,
                                Level.CUSTOM,
                                self.custom_files[i],
                            ),
                        )
                if self.back_rect.collidepoint(event.pos):
                    game.state_manager.pop_state()
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key in [
                    pygame.K_UP,
                    pygame.K_w,
                    pygame.K_DOWN,
                    pygame.K_s,
                    pygame.K_RETURN,
                    pygame.K_SPACE,
                ]:
                    self.keyboard_active = True

                if event.key == pygame.K_ESCAPE:
                    game.state_manager.pop_state()
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option - 1) % (
                            len(self.custom_files) + 1
                        )
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option + 1) % (
                            len(self.custom_files) + 1
                        )
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_option is None:
                        pass
                    elif self.selected_option < len(self.custom_files):
                        game.state_manager.push_state(
                            GameplayState(
                                self.player,
                                self.algorithm,
                                Level.CUSTOM,
                                self.custom_files[self.selected_option],
                            ),
                        )
                    else:
                        # Only option beyond custom files is "Go Back"
                        game.state_manager.pop_state()

        # Update selected option based on mouse position
        # Must be after the keyboard events to avoid overriding the selected option (mouse has priority)
        mouse_pos = pygame.mouse.get_pos()
        for i, rect in enumerate(self.file_rects):
            if rect.collidepoint(mouse_pos):
                self.selected_option = i
                # Avoid falling into the keyboard_active condition
                return
        if self.back_rect.collidepoint(mouse_pos):
            self.selected_option = len(self.custom_files)
            # Avoid falling into the keyboard_active condition
            return

        if not self.keyboard_active:
            self.selected_option = None
            return

    def render(self, screen: pygame.Surface) -> None:  # noqa: D102
        title_text_back = Assets.fonts["title"].render("Wood Block", True, ColorConfig.BROWN)
        title_text_middle = Assets.fonts["title"].render("Wood Block", True, ColorConfig.ORANGE)
        title_text_front = Assets.fonts["title"].render("Wood Block", True, ColorConfig.WHITE)
        subtitle_text = Assets.fonts["subtitle"].render(
            "Select Custom (JSON) File",
            True,
            ColorConfig.BROWN,
        )
        back_text = Assets.fonts["text"].render(
            "Go Back",
            True,
            ColorConfig.ORANGE
            if self.selected_option == len(self.custom_files)
            else ColorConfig.WHITE,
        )

        # Non-interactable rectangles
        title_rect_back = title_text_back.get_rect(
            center=((screen.get_width() // 2) + 5, (screen.get_height() // 4) - 5),
        )
        title_rect_middle = title_text_middle.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 4),
        )
        title_rect_front = title_text_front.get_rect(
            center=((screen.get_width() // 2) - 5, (screen.get_height() // 4) + 5),
        )
        subtitle_rect = subtitle_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2.65),
        )

        # Interactable rectangles
        # - File rects are included (in the loop below)
        self.back_rect = back_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 1.2),
        )

        screen.blit(Assets.backgrounds["menu"], (0, 0))
        screen.blit(title_text_back, title_rect_back)
        screen.blit(title_text_middle, title_rect_middle)
        screen.blit(title_text_front, title_rect_front)
        screen.blit(subtitle_text, subtitle_rect)

        self.file_rects = []
        if self.custom_files:
            for i, file in enumerate(self.custom_files):
                file_text = Assets.fonts["text"].render(
                    file.name[:30] + "..." if len(file.name) > 30 else file.name,
                    True,
                    ColorConfig.ORANGE if self.selected_option == i else ColorConfig.WHITE,
                )
                file_rect = file_text.get_rect(
                    center=(screen.get_width() // 2, screen.get_height() // 2.1 + i * 50),
                )
                self.file_rects.append(file_rect)
                screen.blit(file_text, file_rect)
        else:
            no_files_text = Assets.fonts["text"].render(
                "No custom files found",
                True,
                ColorConfig.WHITE,
            )
            no_files_rect = no_files_text.get_rect(
                center=(screen.get_width() // 2, screen.get_height() // 2.1),
            )
            screen.blit(no_files_text, no_files_rect)

        screen.blit(back_text, self.back_rect)
        pygame.display.flip()

    def exit(self) -> None:  # noqa: D102
        LOGGER.debug("Exiting Select Custom Menu")


class GameplayState(GameState):
    """Gameplay state of the game."""

    def __init__(
        self,
        player: PlayerType,
        ai_algorithm: AIAlgorithmID,
        level: Level = Level.INFINITE,
        file_path: Path | None = None,
    ) -> None:
        self.player = player
        # TODO: Currently algorithm for Infinite level is set to SINGLE_DEPTH_GREEDY, consider adding more options
        self.ai_algorithm_id = (
            ai_algorithm if level != Level.INFINITE else AIAlgorithmID.SINGLE_DEPTH_GREEDY
        )
        self.ai_algorithm = (
            get_ai_algorithm(self.ai_algorithm_id, level)
            if level != Level.INFINITE
            else get_ai_algorithm(AIAlgorithmID.SINGLE_DEPTH_GREEDY, level)
        )
        self.level = level

        self.file_path = file_path
        self.game_data = GameData(level, file_path)
        self.score = 0

        # For both gamemodes
        self.selected_index: int | None = None
        self.selected_piece: Piece | None = None

        # For Human gamemode
        self.hint_button: pygame.Rect | None = None
        self.hint_pressed: bool = False
        self.ai_hint_index: int | None = None
        self.ai_hint_position: PiecePosition | None = None

        # For AI gamemode
        self.ai_running_start_time: float | None = None
        self.ai_initial_pos: AIPiecePosition | None = None
        self.ai_current_pos: AIPiecePosition | None = None
        self.ai_target_pos: AIPiecePosition | None = None

        self.finished_game_message: str | None = None

    def _toggle_ai_running_time(self) -> None:
        """Start or stop the AI running time timer."""
        if self.ai_running_start_time is None:
            self.ai_running_start_time = time.time()
        else:
            self.ai_running_start_time = None

    def _on_ai_algo_done(
        self,
        status: AIReturn,
        piece_index: int | None,
        piece_position: PiecePosition | None,
    ) -> None:
        """Notify or update state when AI algorithm has finished.

        Args:
            status (AIReturn): Status of the AI algorithm (AI_FOUND or AI_NOT_FOUND)
            piece_index (int | None): Index of the piece in the game_data.pieces list
            piece_position (PiecePosition | None): Position where the piece should be placed

        """
        if status == AIReturn.FOUND and piece_index is not None and piece_position is not None:
            LOGGER.debug("AI found a move")

            if self.player == PlayerType.HUMAN:
                self.ai_hint_index = piece_index
                self.ai_hint_position = piece_position
            elif self.player == PlayerType.AI:
                self.selected_index = piece_index
                self.selected_piece = self.game_data.pieces[self.selected_index]
                self.ai_target_pos = (
                    BoardConfig.GRID_OFFSET_X + piece_position[0] * BoardConfig.CELL_SIZE,
                    (BoardConfig.GRID_OFFSET_Y + piece_position[1]) * BoardConfig.CELL_SIZE,
                )

                for i, piece in enumerate(self.game_data.pieces):
                    if piece == self.selected_piece:
                        # Convert from board (cell-based) coordinates to screen-based coordinates
                        self.ai_initial_pos = (
                            (i * PieceListOffset.BETWEEN_X_CELLS + PieceListOffset.X_CELLS)
                            * BoardConfig.CELL_SIZE,
                            PieceListOffset.Y_CELLS * BoardConfig.CELL_SIZE,
                        )
                        self.ai_current_pos = self.ai_initial_pos
                        break

                self.game_data.pieces[self.selected_index] = None
            else:
                raise ValueError(f"Invalid player type: {self.player}")

        elif status == AIReturn.NOT_FOUND:
            LOGGER.debug("AI didn't find a move")
        elif status == AIReturn.STOPPED_EARLY:
            LOGGER.debug("AI stopped early")

    def _finish_game(self, game: Game, next_state: GameState, message: str) -> None:
        """Handle the completion of the game state.

        Clean the gameplay-related variables for the last render() call.
        This last call displays the end state and message.
        """
        self.selected_index = None
        self.selected_piece = None
        self.hint_button = None
        self.hint_pressed = False
        self.ai_hint_index = None
        self.ai_hint_position = None
        self.ai_running_start_time = None
        self.ai_initial_pos = None
        self.ai_current_pos = None
        self.ai_target_pos = None

        self.ai_algorithm.stop()
        self.finished_game_message = message
        self.render(game.screen)
        time.sleep(2)
        game.state_manager.push_state(next_state)

    def enter(self) -> None:  # noqa: D102
        LOGGER.debug("Starting Gameplay")

        # Start running the AI algorithm AS SOON AS WE ENTER THE GAMEPLAY STATE (but avoid recomputing if there are results already)
        if (
            self.player == PlayerType.HUMAN
            and (not self.ai_hint_index or not self.ai_hint_position)
        ) or (
            self.player == PlayerType.AI
            and (not self.ai_initial_pos or not self.ai_current_pos or not self.ai_target_pos)
        ):
            self.ai_algorithm.get_next_move(
                game_data=self.game_data,
                res_callback_func=self._on_ai_algo_done,
                time_callback_func=self._toggle_ai_running_time,
            )

    def update(self, game: Game, events: list[pygame.event.Event]) -> None:  # noqa: D102
        if not game.state_manager.has_states():
            raise ValueError("Unexpected divergence in game state stack")

        if self.player == PlayerType.HUMAN:
            self.update_player(game, events)
        else:
            self.update_ai(game, events)

    def update_player(self, game: Game, events: list[pygame.event.Event]) -> None:  # noqa: D102
        for event in events:
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                self.ai_algorithm.stop()
                raise QuitGameException
            # Keyboard events
            if event.type == pygame.KEYDOWN:
                if event.key in {pygame.K_ESCAPE, pygame.K_p}:
                    # Stop the AI algorithm running in the background (if it is)
                    game.state_manager.push_state(PauseState())

                if (
                    event.key == pygame.K_h
                    and self.ai_hint_index is not None
                    and self.ai_hint_position is not None
                ):
                    # Callback function will handle assigning the AI's move to the corresponding variables
                    # Check how those variables are used in the events above
                    self.hint_pressed = True
            # Mouse click events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.selected_piece is None:
                    mx, my = pygame.mouse.get_pos()
                    for i, piece in enumerate(self.game_data.pieces):
                        if piece is not None:
                            min_x = min(block[0] for block in piece)
                            max_x = max(block[0] for block in piece)
                            min_y = min(block[1] for block in piece)
                            max_y = max(block[1] for block in piece)

                            piece_x_start = (
                                i * PieceListOffset.BETWEEN_X_CELLS + PieceListOffset.X_CELLS
                            ) * BoardConfig.CELL_SIZE
                            piece_y_start = PieceListOffset.Y_CELLS * BoardConfig.CELL_SIZE
                            piece_x_end = (
                                piece_x_start + (max_x - min_x + 1) * BoardConfig.CELL_SIZE
                            )
                            piece_y_end = (
                                piece_y_start + (max_y - min_y + 1) * BoardConfig.CELL_SIZE
                            )

                            if (
                                piece_x_start <= mx <= piece_x_end
                                and piece_y_start <= my <= piece_y_end
                            ):
                                self.selected_index = i
                                self.selected_piece = piece
                                self.game_data.pieces[i] = None
                                break

                    # Mouse wasn't on any piece (still not selected), check if hint button was pressed with the mouse
                    if (
                        self.selected_piece is None
                        and self.hint_button is not None
                        and self.hint_button.collidepoint(mx, my)
                    ):
                        self.hint_pressed = True

                else:
                    # Piece is already selected, so pressing down again won't do anything
                    # Not technically possible to press down again while a piece is selected
                    pass

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.selected_piece is None:
                    # Mouse button was released but no piece was selected
                    pass
                else:
                    mx, my = pygame.mouse.get_pos()
                    px, py = (
                        mx // BoardConfig.CELL_SIZE,
                        (my // BoardConfig.CELL_SIZE) - BoardConfig.GRID_OFFSET_Y,
                    )
                    if is_valid_position(self.game_data.board, self.selected_piece, (px - 4, py)):
                        place_piece(self.game_data, self.selected_piece, (px - 4, py))
                        lines_cols_cleared, target_blocks_cleared = clear_full_lines(
                            self.game_data.board,
                        )
                        if self.level == Level.INFINITE:
                            self.score += lines_cols_cleared
                        else:
                            self.game_data.blocks_to_break -= target_blocks_cleared
                            self.score += target_blocks_cleared
                            if self.game_data.blocks_to_break <= 0:
                                self._finish_game(
                                    game=game,
                                    next_state=LevelCompleteState(
                                        self.score,
                                        self.player,
                                        self.ai_algorithm_id,
                                        self.level,
                                        self.file_path,
                                    ),
                                    message=f"{'Custom Level completed!' if self.level == Level.CUSTOM else f'Level {self.level} completed!'}",
                                )
                                return

                        # All pieces placed (all None), generate new ones
                        if not any(self.game_data.pieces):
                            _are_there_more = self.game_data.get_more_playable_pieces()

                        # Now that pieces are guaranteed to be available (if they exist), check for valid moves
                        if no_more_valid_moves(self.game_data.board, self.game_data.pieces):
                            self._finish_game(
                                game=game,
                                next_state=GameOverState(
                                    self.score,
                                    self.player,
                                    self.ai_algorithm_id,
                                    self.level,
                                    self.file_path,
                                ),
                                message="Game Over! No more valid moves!",
                            )
                            return

                        # Player made move, so state changed, then prepare next hint
                        if (
                            self.ai_running_start_time is None
                            and self.ai_hint_index is not None
                            and self.ai_hint_position is not None
                        ):
                            hinted_piece_placed = (
                                self.selected_index == self.ai_hint_index
                                and px - 4 == self.ai_hint_position[0]
                                and py == self.ai_hint_position[1]
                            )

                            if hinted_piece_placed:
                                # Get the next hint
                                self.ai_algorithm.get_next_move(
                                    game_data=self.game_data,
                                    res_callback_func=self._on_ai_algo_done,
                                    time_callback_func=self._toggle_ai_running_time,
                                )
                            else:
                                # Don't show old hint anymore
                                self.ai_hint_index = None
                                self.ai_hint_position = None

                                # Need to get a new hint, because the game state has changed
                                # To a different configuration that the previously run algorithm might not account for
                                # Hence calling stop() and get_next_move()
                                if self.ai_algorithm.is_running():
                                    self.ai_algorithm.stop()
                                else:
                                    self.ai_algorithm.get_next_move(
                                        game_data=self.game_data,
                                        res_callback_func=self._on_ai_algo_done,
                                        time_callback_func=self._toggle_ai_running_time,
                                        reset=True,
                                    )
                        else:
                            # Even if the algorithm didn't finish, player made a move,
                            # so reset the hint
                            # Don't show old hint anymore
                            self.ai_hint_index = None
                            self.ai_hint_position = None

                            # Need to get a new hint, because the game state has changed
                            # To a different configuration that the previously run algorithm might not account for
                            # Hence calling stop() and get_next_move()
                            if self.ai_algorithm.is_running():
                                self.ai_algorithm.stop()
                            else:
                                self.ai_algorithm.get_next_move(
                                    game_data=self.game_data,
                                    res_callback_func=self._on_ai_algo_done,
                                    time_callback_func=self._toggle_ai_running_time,
                                    reset=True,
                                )

                        # After placing a piece, reset the hint
                        self.hint_pressed = False

                    else:
                        # Restore visibility if not placed
                        for i, piece in enumerate(self.game_data.pieces):
                            if self.selected_index == i and piece is None:
                                self.game_data.pieces[i] = self.selected_piece

                    # Piece has been placed, reset selection
                    self.selected_index = None
                    self.selected_piece = None

    def update_ai(self, game: Game, events: list[pygame.event.Event]) -> None:  # noqa: D102
        for event in events:
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                self.ai_algorithm.stop()
                raise QuitGameException

        # Callback function will handle assigning the AI's move to the corresponding variables

        if self.ai_running_start_time is not None:
            # AI algorithm still running, do nothing
            return

        if self.selected_piece is None:
            # No move was found by AI, finish the game
            self._finish_game(
                game=game,
                next_state=GameOverState(
                    self.score,
                    self.player,
                    self.ai_algorithm_id,
                    self.level,
                    self.file_path,
                ),
                message="Game Over! AI didn't find a move!",
            )
            return

        if (
            self.ai_current_pos is not None
            and self.ai_target_pos is not None
            and self.ai_current_pos == self.ai_target_pos
        ):
            # AI move animation complete, place the piece
            px = round((self.ai_target_pos[0] - BoardConfig.GRID_OFFSET_X) // BoardConfig.CELL_SIZE)
            py = round((self.ai_target_pos[1] // BoardConfig.CELL_SIZE) - BoardConfig.GRID_OFFSET_Y)
            place_piece(self.game_data, self.selected_piece, (px, py))
            lines_cols_cleared, target_blocks_cleared = clear_full_lines(self.game_data.board)

            # Handle scoring and level progression
            if self.level == Level.INFINITE:
                self.score += lines_cols_cleared
            else:
                self.game_data.blocks_to_break -= target_blocks_cleared
                self.score += target_blocks_cleared
                if self.game_data.blocks_to_break <= 0:
                    self._finish_game(
                        game=game,
                        next_state=LevelCompleteState(
                            self.score,
                            self.player,
                            self.ai_algorithm_id,
                            self.level,
                            self.file_path,
                        ),
                        message=f"{'Custom Level completed!' if self.level == Level.CUSTOM else f'Level {self.level} completed!'}",
                    )
                    return

            # All pieces placed (all None), generate new ones
            if not any(self.game_data.pieces):
                _are_there_more = self.game_data.get_more_playable_pieces()

            # Now that pieces are guaranteed to be available (if they exist), check for valid moves
            if no_more_valid_moves(self.game_data.board, self.game_data.pieces):
                self._finish_game(
                    game=game,
                    next_state=GameOverState(
                        self.score,
                        self.player,
                        self.ai_algorithm_id,
                        self.level,
                        self.file_path,
                    ),
                    message="Game Over! No more valid moves!",
                )
                return

            # Reset AI move state and request next move
            self.selected_piece = None
            self.ai_initial_pos = None
            self.ai_current_pos = None
            self.ai_target_pos = None
            self.ai_algorithm.get_next_move(
                game_data=self.game_data,
                res_callback_func=self._on_ai_algo_done,
                time_callback_func=self._toggle_ai_running_time,
            )

    def _render_finished_game_message(self, screen: pygame.Surface, message: str) -> None:
        """Render the finished game message overlay on the screen."""
        message_text = Assets.fonts["text"].render(
            message,
            True,
            ColorConfig.WHITE,
        )
        message_rect = message_text.get_rect(
            center=(ScreenConfig.WIDTH // 2, ScreenConfig.HEIGHT // 2)
        )

        overlay = pygame.Surface((ScreenConfig.WIDTH, ScreenConfig.HEIGHT))
        overlay.set_alpha(64)  # Set transparency level (0-255)
        overlay.fill(ColorConfig.BLACK)
        screen.blit(overlay, (0, 0))
        screen.blit(message_text, message_rect)

    def render(self, screen: pygame.Surface) -> None:  # noqa: D102
        if self.player == PlayerType.HUMAN:
            self.render_player(screen)
        else:
            self.render_ai(screen)

    def render_player(self, screen: pygame.Surface) -> None:  # noqa: D102
        hint_text = Assets.fonts["hint"].render("H", True, ColorConfig.WHITE)
        hint_icon = pygame.transform.scale(Assets.icons["hint"], (60, 60))  # Resize the hint icon

        screen.blit(Assets.backgrounds["game"], (0, 0))

        # Draw the hint piece
        if (
            self.hint_pressed
            and self.ai_hint_index is not None
            and self.ai_hint_position is not None
        ):
            game_data = copy.deepcopy(self.game_data)
            piece = (
                self.game_data.pieces[self.ai_hint_index]
                if self.game_data.pieces[self.ai_hint_index] is not None
                else self.selected_piece
            )
            assert piece is not None
            place_piece(
                game_data=game_data,
                piece=piece,
                position=self.ai_hint_position,
                is_hint=True,
            )
            draw_board(screen, game_data.board)
        else:
            draw_board(screen, self.game_data.board)

        mx, my = pygame.mouse.get_pos()
        px, py = (
            mx // BoardConfig.CELL_SIZE,
            (my // BoardConfig.CELL_SIZE) - BoardConfig.GRID_OFFSET_Y,
        )

        # Draw the list of pieces
        for i, piece in enumerate(self.game_data.pieces):
            if piece is not None:
                draw_piece(
                    screen=screen,
                    piece=piece,
                    position=(
                        i * PieceListOffset.BETWEEN_X_CELLS + PieceListOffset.X_CELLS,
                        PieceListOffset.Y_CELLS,
                    ),
                )

        # Draw the selected piece
        if self.selected_piece is not None:
            draw_piece(
                screen=screen,
                piece=self.selected_piece,
                position=(px, py),
                offset_y=BoardConfig.GRID_OFFSET_Y,
                is_selected=True,
            )

        # Draw AI hint button (orange indicates hint availability)
        # (orange even if no hint is available, it will get overridden if no hint)
        self.hint_button = pygame.draw.circle(
            surface=screen,
            color=ColorConfig.ORANGE,
            center=(ScreenConfig.WIDTH - 50, 50),
            radius=30,
        )
        screen.blit(hint_icon, self.hint_button.topleft)
        screen.blit(hint_text, (self.hint_button.right - 18, self.hint_button.bottom - 18))
        if self.ai_hint_index is None or self.ai_hint_position is None:
            # If no hint is available, grey out the hint button
            self.hint_button = pygame.draw.circle(
                surface=screen,
                color=ColorConfig.DARK_GRAY,
                center=(ScreenConfig.WIDTH - 50, 50),
                radius=30,
            )
            greyed_hint_icon = hint_icon.copy()
            greyed_hint_icon.fill(color=ColorConfig.GRAY, special_flags=pygame.BLEND_RGBA_MULT)
            greyed_hint_text = Assets.fonts["hint"].render("H", True, ColorConfig.GRAY)
            screen.blit(greyed_hint_icon, self.hint_button.topleft)
            screen.blit(
                greyed_hint_text,
                (self.hint_button.right - 18, self.hint_button.bottom - 18),
            )
        elif self.hint_button.collidepoint(mx, my):
            # Highlight the hint button if the mouse is over it
            self.hint_button = pygame.draw.circle(
                surface=screen,
                color=ColorConfig.BROWN,
                center=(ScreenConfig.WIDTH - 50, 50),
                radius=30,
            )
            screen.blit(hint_icon, self.hint_button.topleft)
            screen.blit(hint_text, (self.hint_button.right - 18, self.hint_button.bottom - 18))

        draw_score(screen, self.score)

        if self.finished_game_message:
            self._render_finished_game_message(screen, self.finished_game_message)

        pygame.display.flip()

    def render_ai(self, screen: pygame.Surface) -> None:  # noqa: D102
        screen.blit(Assets.backgrounds["game"], (0, 0))

        draw_board(screen, self.game_data.board)

        # Draw the list of pieces
        for i, piece in enumerate(self.game_data.pieces):
            if piece is not None:
                draw_piece(
                    screen=screen,
                    piece=piece,
                    position=(
                        i * PieceListOffset.BETWEEN_X_CELLS + PieceListOffset.X_CELLS,
                        PieceListOffset.Y_CELLS,
                    ),
                )

        # Draw the selected piece (AI movement)
        # Moving in a straight line from initial (hand) to target (board) position
        if (
            self.selected_piece is not None
            and self.ai_initial_pos is not None
            and self.ai_current_pos is not None
            and self.ai_target_pos is not None
            and self.ai_current_pos != self.ai_target_pos
        ):
            px, py = (
                self.ai_current_pos[0] / BoardConfig.CELL_SIZE,
                self.ai_current_pos[1] / BoardConfig.CELL_SIZE,
            )
            draw_piece(
                screen=screen,
                piece=self.selected_piece,
                position=(px, py),
                is_selected=True,
            )

            cx, cy = self.ai_current_pos
            tx, ty = self.ai_target_pos
            distance = math.sqrt((tx - cx) ** 2 + (ty - cy) ** 2)
            speed = 20
            if distance < speed:
                self.ai_current_pos = self.ai_target_pos
            else:
                # Calculate the normalized direction vector
                direction_x: float = tx - self.ai_initial_pos[0]
                direction_y: float = ty - self.ai_initial_pos[1]

                norm = math.sqrt(direction_x**2 + direction_y**2)
                direction_x /= norm
                direction_y /= norm

                step_x = speed * direction_x
                step_y = speed * direction_y

                self.ai_current_pos = (cx + step_x, cy + step_y)

        draw_score(screen, self.score)

        # The AI is running, show the time elapsed
        if self.ai_running_start_time is not None:
            algorithm_text = Assets.fonts["text"].render(
                f"{AI_ALGO_NAMES.get(self.ai_algorithm_id)} is running...",
                True,
                ColorConfig.WHITE,
            )
            elapsed_time = time.time() - self.ai_running_start_time
            elapsed_time_text = Assets.fonts["text"].render(
                f"Time Elapsed: {elapsed_time:.3f} seconds",
                True,
                ColorConfig.WHITE,
            )

            algorithm_time_rect = algorithm_text.get_rect(
                center=(ScreenConfig.WIDTH // 2, ScreenConfig.HEIGHT // 2.8),
            )
            elapsed_time_rect = elapsed_time_text.get_rect(
                center=(ScreenConfig.WIDTH // 2, ScreenConfig.HEIGHT // 2),
            )

            overlay = pygame.Surface((ScreenConfig.WIDTH, ScreenConfig.HEIGHT))
            overlay.set_alpha(128)  # Set transparency level (0-255)
            overlay.fill(ColorConfig.BLACK)  # Black color
            screen.blit(overlay, (0, 0))
            screen.blit(algorithm_text, algorithm_time_rect)
            screen.blit(elapsed_time_text, elapsed_time_rect)

        # If the game is finished, the message is set, display it
        if self.finished_game_message is not None:
            self._render_finished_game_message(screen, self.finished_game_message)

        pygame.display.flip()

    def exit(self) -> None:  # noqa: D102
        LOGGER.debug("Exiting Gameplay")


class PauseState(GameState):
    """Pause menu."""

    def __init__(self) -> None:
        self.keyboard_active = False
        self.selected_option = None
        self.resume_rect = None
        self.exit_rect = None

    def enter(self) -> None:  # noqa: D102
        LOGGER.debug("Game Paused")
        self.keyboard_active = False
        self.selected_option = None

    def update(self, game: Game, events: list[pygame.event.Event]) -> None:  # noqa: D102
        assert self.resume_rect is not None
        assert self.exit_rect is not None

        if not game.state_manager.has_states():
            raise ValueError("Unexpected divergence in game state stack")

        for event in events:
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                # Get the GameplayState and stop the AI algorithm
                gameplay_state = game.state_manager.pop_until(GameplayState)
                assert gameplay_state is not None
                gameplay_state.ai_algorithm.stop()
                raise QuitGameException
            # Mouse click events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.resume_rect.collidepoint(event.pos):
                    game.state_manager.pop_until(GameplayState)
                elif self.exit_rect.collidepoint(event.pos):
                    gameplay_state = game.state_manager.pop_until(GameplayState)
                    gameplay_state.ai_algorithm.stop()
                    game.state_manager.switch_to_base_state(MainMenuState())
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key in [
                    pygame.K_UP,
                    pygame.K_w,
                    pygame.K_DOWN,
                    pygame.K_s,
                    pygame.K_RETURN,
                    pygame.K_SPACE,
                ]:
                    self.keyboard_active = True

                if event.key in [pygame.K_r, pygame.K_ESCAPE, pygame.K_p]:
                    game.state_manager.pop_until(GameplayState)
                elif event.key == pygame.K_ESCAPE:
                    gameplay_state = game.state_manager.pop_until(GameplayState)
                    gameplay_state.ai_algorithm.stop()
                    game.state_manager.switch_to_base_state(MainMenuState())
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option - 1) % 2
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option + 1) % 2
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_option == 0:
                        game.state_manager.pop_until(GameplayState)
                    elif self.selected_option == 1:
                        gameplay_state = game.state_manager.pop_until(GameplayState)
                        gameplay_state.ai_algorithm.stop()
                        game.state_manager.switch_to_base_state(MainMenuState())

        # Update selected option based on mouse position
        # Must be after the keyboard events to avoid overriding the selected option (mouse has priority)
        mouse_pos = pygame.mouse.get_pos()
        if self.resume_rect.collidepoint(mouse_pos):
            self.selected_option = 0
        elif self.exit_rect.collidepoint(mouse_pos):
            self.selected_option = 1
        elif not self.keyboard_active:
            self.selected_option = None

    def render(self, screen: pygame.Surface) -> None:  # noqa: D102
        pause_text = Assets.fonts["title"].render("Pause", True, ColorConfig.WHITE)
        resume_text = Assets.fonts["text"].render(
            "Resume",
            True,
            ColorConfig.ORANGE if self.selected_option == 0 else ColorConfig.WHITE,
        )
        exit_text = Assets.fonts["text"].render(
            "Quit",
            True,
            ColorConfig.ORANGE if self.selected_option == 1 else ColorConfig.WHITE,
        )

        # Non-interactable rectangles
        pause_rect = pause_text.get_rect(center=(ScreenConfig.WIDTH // 2, ScreenConfig.HEIGHT // 4))

        # Interactable rectangles
        self.resume_rect = resume_text.get_rect(
            center=(ScreenConfig.WIDTH // 2, ScreenConfig.HEIGHT // 2.5)
        )
        self.exit_rect = exit_text.get_rect(
            center=(ScreenConfig.WIDTH // 2, ScreenConfig.HEIGHT // 2)
        )

        screen.fill(ColorConfig.BROWN)
        screen.blit(pause_text, pause_rect)
        screen.blit(resume_text, self.resume_rect)
        screen.blit(exit_text, self.exit_rect)
        pygame.display.flip()

    def exit(self) -> None:  # noqa: D102
        LOGGER.debug("Exiting Pause")


class GameOverState(GameState):
    """Game Over menu."""

    def __init__(
        self,
        score: int,
        player: PlayerType,
        ai_algorithm: AIAlgorithmID,
        level: Level,
        file_path: Path | None = None,
    ) -> None:
        self.score = score
        self.player = player
        self.ai_algorithm = ai_algorithm
        self.level = level
        self.file_path = file_path

        self.keyboard_active = False
        self.selected_option: int | None = None
        self.retry_level_rect: pygame.Rect | None = None
        self.back_rect: pygame.Rect | None = None

    def enter(self) -> None:  # noqa: D102
        LOGGER.debug("Entering Game Over")
        self.keyboard_active = False
        self.selected_option = None

    def update(self, game: Game, events: list[pygame.event.Event]) -> None:  # noqa: D102
        if not game.state_manager.has_states():
            raise ValueError("Unexpected divergence in game state stack")

        for event in events:
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                raise QuitGameException
            # Mouse click events
            if event.type == pygame.MOUSEBUTTONDOWN:
                assert self.retry_level_rect is not None
                assert self.back_rect is not None

                if self.retry_level_rect.collidepoint(event.pos):
                    game.state_manager.subst_below_switch_to(
                        GameplayState(self.player, self.ai_algorithm, self.level, self.file_path),
                    )
                elif self.back_rect.collidepoint(event.pos):
                    # Pop the GameOverState and the GameplayState
                    game.state_manager.pop_beyond(GameplayState, 1)
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key in [
                    pygame.K_UP,
                    pygame.K_w,
                    pygame.K_DOWN,
                    pygame.K_s,
                    pygame.K_RETURN,
                    pygame.K_SPACE,
                ]:
                    self.keyboard_active = True

                if event.key == pygame.K_ESCAPE:
                    game.state_manager.pop_beyond(GameplayState, 1)
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option - 1) % 2
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option + 1) % 2
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_option == 0:
                        game.state_manager.subst_below_switch_to(
                            GameplayState(
                                self.player,
                                self.ai_algorithm,
                                self.level,
                                self.file_path,
                            ),
                        )
                    elif self.selected_option == 1:
                        game.state_manager.pop_beyond(GameplayState, 1)

        assert self.retry_level_rect is not None
        assert self.back_rect is not None
        # Update selected option based on mouse position
        # Must be after the keyboard events to avoid overriding the selected option (mouse has priority)
        mouse_pos = pygame.mouse.get_pos()
        if self.retry_level_rect.collidepoint(mouse_pos):
            self.selected_option = 0
        elif self.back_rect.collidepoint(mouse_pos):
            self.selected_option = 1
        elif not self.keyboard_active:
            self.selected_option = None

    def render(self, screen: pygame.Surface) -> None:  # noqa: D102
        game_over_text = Assets.fonts["title"].render("Game Over", True, ColorConfig.WHITE)
        score_text = Assets.fonts["subtitle"].render(
            f"Score: {self.score}",
            True,
            ColorConfig.ORANGE,
        )
        retry_level_text = Assets.fonts["text"].render(
            "Retry Level",
            True,
            ColorConfig.ORANGE if self.selected_option == 0 else ColorConfig.WHITE,
        )
        back_text = Assets.fonts["text"].render(
            "Go Back",
            True,
            ColorConfig.ORANGE if self.selected_option == 1 else ColorConfig.WHITE,
        )

        # Non-interactable rectangles
        game_over_rect = game_over_text.get_rect(
            center=(ScreenConfig.WIDTH // 2, ScreenConfig.HEIGHT // 4)
        )
        score_rect = score_text.get_rect(
            center=(ScreenConfig.WIDTH // 2, ScreenConfig.HEIGHT // 2.5)
        )

        # Interactable rectangles
        self.retry_level_rect = retry_level_text.get_rect(
            center=(ScreenConfig.WIDTH // 2, ScreenConfig.HEIGHT // 1.7),
        )
        self.back_rect = back_text.get_rect(
            center=(ScreenConfig.WIDTH // 2, ScreenConfig.HEIGHT // 1.4)
        )

        screen.fill(ColorConfig.BROWN)
        screen.blit(game_over_text, game_over_rect)
        screen.blit(score_text, score_rect)
        screen.blit(retry_level_text, self.retry_level_rect)
        screen.blit(back_text, self.back_rect)
        pygame.display.flip()

    def exit(self) -> None:  # noqa: D102
        LOGGER.debug("Exiting Game Over")


class LevelCompleteState(GameState):
    """Level Complete menu."""

    def __init__(
        self,
        score: int,
        player: PlayerType,
        ai_algorithm: AIAlgorithmID,
        level: Level,
        file_path: Path | None = None,
    ) -> None:
        self.score = score
        self.player = player
        self.ai_algorithm = ai_algorithm
        self.level = level
        self.file_path = file_path

        self.keyboard_active = False
        self.selected_option: int | None = None
        self.next_level_rect: pygame.Rect | None = None
        self.play_next_rect: pygame.Rect | None = None
        self.back_rect: pygame.Rect | None = None

    def _get_level_flags(self) -> tuple[bool, bool, bool]:
        """Return boolean flags used in update() and render().

        Returns:
        - is_last_level: True if the level is the last one
        - is_custom_level_with_file: True if the level is CUSTOM and a file path is provided
        - has_next_level_option: True if the level is not the last one and not a custom level with a file path

        """
        is_last_level = self.level == LEVELS[-1]
        is_custom_level_with_file = self.level == Level.CUSTOM and self.file_path is not None
        has_next_level_option = not is_last_level and not is_custom_level_with_file
        return is_last_level, is_custom_level_with_file, has_next_level_option

    def enter(self) -> None:  # noqa: D102
        LOGGER.debug("Entering Level Complete")
        self.keyboard_active = False
        self.selected_option = None

    def update(self, game: Game, events: list[pygame.event.Event]) -> None:  # noqa: D102
        if not game.state_manager.has_states():
            raise ValueError("Unexpected divergence in game state stack")

        _, _, has_next_level_option = self._get_level_flags()

        for event in events:
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                raise QuitGameException
            # Mouse click events
            if event.type == pygame.MOUSEBUTTONDOWN:
                assert self.play_next_rect is not None
                assert self.next_level_rect is not None
                assert self.back_rect is not None

                if has_next_level_option and self.next_level_rect.collidepoint(event.pos):
                    try:
                        current_index = LEVELS.index(self.level)
                        next_level = LEVELS[current_index + 1]
                    except (ValueError, IndexError):
                        # No next level
                        next_level = None

                    if next_level is not None:
                        game.state_manager.subst_below_switch_to(
                            GameplayState(
                                self.player,
                                self.ai_algorithm,
                                next_level,
                                self.file_path,
                            ),
                        )
                elif self.play_next_rect.collidepoint(event.pos):
                    game.state_manager.subst_below_switch_to(
                        GameplayState(self.player, self.ai_algorithm, self.level, self.file_path),
                    )
                elif self.back_rect.collidepoint(event.pos):
                    game.state_manager.pop_beyond(GameplayState, 1)
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key in [
                    pygame.K_UP,
                    pygame.K_w,
                    pygame.K_DOWN,
                    pygame.K_s,
                    pygame.K_RETURN,
                    pygame.K_SPACE,
                ]:
                    self.keyboard_active = True

                if event.key == pygame.K_ESCAPE:
                    game.state_manager.pop_beyond(GameplayState, 1)
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option - 1) % (
                            3 if has_next_level_option else 2
                        )
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option + 1) % (
                            3 if has_next_level_option else 2
                        )
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_option == 0 and has_next_level_option:
                        try:
                            current_index = LEVELS.index(self.level)
                            next_level = LEVELS[current_index + 1]
                        except (ValueError, IndexError):
                            # No next level
                            next_level = None

                        if next_level is not None:
                            game.state_manager.subst_below_switch_to(
                                GameplayState(
                                    self.player,
                                    self.ai_algorithm,
                                    next_level,
                                    self.file_path,
                                ),
                            )
                    elif (has_next_level_option and self.selected_option == 1) or (
                        not has_next_level_option and self.selected_option == 0
                    ):
                        game.state_manager.subst_below_switch_to(
                            GameplayState(
                                self.player,
                                self.ai_algorithm,
                                self.level,
                                self.file_path,
                            ),
                        )
                    elif (has_next_level_option and self.selected_option == 2) or (
                        not has_next_level_option and self.selected_option == 1
                    ):
                        game.state_manager.pop_beyond(GameplayState, 1)

        if has_next_level_option:
            assert self.next_level_rect is not None
        else:
            assert self.next_level_rect is None
        assert self.play_next_rect is not None
        assert self.back_rect is not None
        # Update selected option based on mouse position
        # Must be after the keyboard events to avoid overriding the selected option (mouse has priority)
        mouse_pos = pygame.mouse.get_pos()
        if (
            has_next_level_option
            and self.next_level_rect is not None
            and self.next_level_rect.collidepoint(mouse_pos)
        ):
            # not None check to satisfy mypy even though conditional assert guarantees it
            self.selected_option = 0
        elif self.play_next_rect.collidepoint(mouse_pos):
            self.selected_option = 1 if has_next_level_option else 0
        elif self.back_rect.collidepoint(mouse_pos):
            self.selected_option = 2 if has_next_level_option else 1
        elif not self.keyboard_active:
            self.selected_option = None

    def render(self, screen: pygame.Surface) -> None:  # noqa: D102
        level_complete_text = Assets.fonts["title"].render(
            "Level Complete",
            True,
            ColorConfig.WHITE,
        )
        score_text = Assets.fonts["text"].render(
            f"Score: {self.score}",
            True,
            ColorConfig.ORANGE,
        )

        _, _, has_next_level_option = self._get_level_flags()

        if has_next_level_option:
            next_level_text = Assets.fonts["text"].render(
                "Next Level",
                True,
                ColorConfig.ORANGE if self.selected_option == 0 else ColorConfig.WHITE,
            )
            play_next_text = Assets.fonts["text"].render(
                "Play Again",
                True,
                ColorConfig.ORANGE if self.selected_option == 1 else ColorConfig.WHITE,
            )
            back_text = Assets.fonts["text"].render(
                "Go Back",
                True,
                ColorConfig.ORANGE if self.selected_option == 2 else ColorConfig.WHITE,
            )
        else:
            play_next_text = Assets.fonts["text"].render(
                "Play Again",
                True,
                ColorConfig.ORANGE if self.selected_option == 0 else ColorConfig.WHITE,
            )
            back_text = Assets.fonts["text"].render(
                "Go Back",
                True,
                ColorConfig.ORANGE if self.selected_option == 1 else ColorConfig.WHITE,
            )

        # Non-interactable rectangles
        level_complete_rect = level_complete_text.get_rect(
            center=(ScreenConfig.WIDTH // 2, ScreenConfig.HEIGHT // 4),
        )
        score_rect = score_text.get_rect(
            center=(ScreenConfig.WIDTH // 2, ScreenConfig.HEIGHT // 2.5)
        )

        # Interactable rectangles
        if has_next_level_option:
            self.next_level_rect = next_level_text.get_rect(
                center=(ScreenConfig.WIDTH // 2, ScreenConfig.HEIGHT // 1.7),
            )
        self.play_next_rect = play_next_text.get_rect(
            center=(ScreenConfig.WIDTH // 2, ScreenConfig.HEIGHT // 1.5),
        )
        self.back_rect = back_text.get_rect(
            center=(ScreenConfig.WIDTH // 2, ScreenConfig.HEIGHT // 1.3)
        )

        screen.fill(ColorConfig.BROWN)
        screen.blit(level_complete_text, level_complete_rect)
        screen.blit(score_text, score_rect)
        if has_next_level_option:
            screen.blit(next_level_text, self.next_level_rect)
        screen.blit(play_next_text, self.play_next_rect)
        screen.blit(back_text, self.back_rect)
        pygame.display.flip()

    def exit(self) -> None:  # noqa: D102
        LOGGER.debug("Exiting Level Complete")
