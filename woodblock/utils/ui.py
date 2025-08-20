from __future__ import annotations

import pygame

from woodblock.assets.assets import Assets
from woodblock.game_logic.constants import (
    AIPiecePosition,
    Board,
    BoardConfig,
    CellType,
    ColorConfig,
    FontConfig,
    Piece,
    PiecePosition,
)


def draw_board(screen: pygame.Surface, board: Board) -> None:
    """Draw the board.

    Args:
        screen (pygame.Surface): The screen to draw on
        board (Board): The board to draw

    """
    for y in range(BoardConfig.ROW_SIZE):
        for x in range(BoardConfig.COL_SIZE):
            rect = pygame.Rect(
                BoardConfig.GRID_OFFSET_X + x * BoardConfig.CELL_SIZE,
                (y + BoardConfig.GRID_OFFSET_Y) * BoardConfig.CELL_SIZE,
                BoardConfig.CELL_SIZE,
                BoardConfig.CELL_SIZE,
            )
            block = board[y][x]
            if block.type == CellType.HINT:
                # Create a semi-transparent red surface
                red_surface = pygame.Surface(
                    (BoardConfig.CELL_SIZE, BoardConfig.CELL_SIZE),
                    pygame.SRCALPHA,
                )
                red_surface.fill((255, 0, 0, 128))  # RGBA with alpha value 128 for transparency
                screen.blit(
                    red_surface,
                    (
                        BoardConfig.GRID_OFFSET_X + x * BoardConfig.CELL_SIZE,
                        (y + BoardConfig.GRID_OFFSET_Y) * BoardConfig.CELL_SIZE,
                    ),
                )
            elif block.type == CellType.PLAYER:
                screen.blit(
                    Assets.blocks["player"],
                    (
                        BoardConfig.GRID_OFFSET_X + x * BoardConfig.CELL_SIZE,
                        (y + BoardConfig.GRID_OFFSET_Y) * BoardConfig.CELL_SIZE,
                    ),
                )
            elif block.type == CellType.TARGET:
                screen.blit(
                    Assets.blocks["target"],
                    (
                        BoardConfig.GRID_OFFSET_X + x * BoardConfig.CELL_SIZE,
                        (y + BoardConfig.GRID_OFFSET_Y) * BoardConfig.CELL_SIZE,
                    ),
                )
            # TODO: If more cell types are added, handle their drawing here
            pygame.draw.rect(screen, ColorConfig.GRAY, rect, 1)


def draw_piece(
    screen: pygame.Surface,
    piece: Piece,
    position: PiecePosition | AIPiecePosition,
    offset_y: int = 0,
    *,
    is_selected: bool = False,
) -> None:
    """Draw a piece on the screen.

    Args:
        screen (pygame.Surface): The screen to draw on
        piece (Piece): The piece to draw
        position (PiecePosition | AIPiecePosition): The position to draw the piece
        offset_y (int, optional): The vertical (y) offset to draw the piece. Defaults to 0
        is_selected (bool, optional): Whether the piece is selected. Defaults to False

    """
    px, py = position
    for x, y in piece:
        rect = pygame.Rect(
            (px + x) * BoardConfig.CELL_SIZE,
            (py + y + offset_y) * BoardConfig.CELL_SIZE,
            BoardConfig.CELL_SIZE,
            BoardConfig.CELL_SIZE,
        )
        if is_selected:
            screen.blit(
                Assets.blocks["selected"],
                ((px + x) * BoardConfig.CELL_SIZE, (py + y + offset_y) * BoardConfig.CELL_SIZE),
            )
        else:
            screen.blit(
                Assets.blocks["block"],
                ((px + x) * BoardConfig.CELL_SIZE, (py + y + offset_y) * BoardConfig.CELL_SIZE),
            )
        # Draw border around piece
        pygame.draw.rect(screen, ColorConfig.GRAY, rect, 1)


def draw_score(screen: pygame.Surface, score: int) -> None:
    """Draw the score on the screen.

    Args:
        screen (pygame.Surface): The screen to draw on
        score (int): The score to draw

    """
    font = pygame.font.Font(FontConfig.PATH, FontConfig.TEXT_SMALL_SIZE)
    text = font.render(f"Score: {score}", True, ColorConfig.WHITE)
    screen.blit(text, (10, 10))
