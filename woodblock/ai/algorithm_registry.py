from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from woodblock.ai.algorithms import AIAlgorithm
    from woodblock.game_logic.constants import AIAlgorithmID, Level

LOGGER = logging.getLogger(__name__)


class AIAlgorithmRegistry:
    """Registry for AI algorithms.

    Follows the Registry Pattern.
    This class is used to register and retrieve AI algorithms.

    """

    _registry: ClassVar[dict[AIAlgorithmID, type[AIAlgorithm]]] = {}

    @classmethod
    def register(cls, identifier: AIAlgorithmID, algorithm: type[AIAlgorithm]) -> None:
        """Register an AI algorithm with the registry."""
        cls._registry[identifier] = algorithm

    @classmethod
    def get_algorithm(cls, identifier: AIAlgorithmID) -> type[AIAlgorithm]:
        """Get an AI algorithm from the registry.

        Args:
            identifier (AIAlgorithmID): The identifier of the AI algorithm.

        Raises:
            ValueError: If the identifier is not found in the registry.

        Returns:
            type[AIAlgorithm]: The requested AI algorithm class.

        """
        if identifier not in cls._registry:
            raise ValueError(f"Unknown AI algorithm: {identifier}")
        return cls._registry[identifier]

    @classmethod
    def get_algorithm_id(cls, algorithm: AIAlgorithm) -> AIAlgorithmID:
        """Get the identifier of an AI algorithm from the registry.

        Args:
            algorithm (AIAlgorithm): The AI algorithm instance.

        Raises:
            ValueError: If the AI algorithm is not found in the registry.

        Returns:
            AIAlgorithmID: The identifier of the requested AI algorithm.

        """
        LOGGER.debug(f"Looking for algorithm: {algorithm}")
        for identifier, alg in cls._registry.items():
            if isinstance(algorithm, alg):
                return identifier
        raise ValueError(f"Unknown AI algorithm: {algorithm}")


def get_ai_algorithm(ai_algorithm: AIAlgorithmID, level: Level) -> AIAlgorithm:
    """Get the AI algorithm instance based on the identifier.

    It fetches the AI algorithm class and instantiates it with the provided level.

    Abstracts the implementation details of storage of AI algorithms, in this case, the registry pattern.

    Args:
        ai_algorithm (AIAlgorithmID): The identifier of the AI algorithm.
        level (Level): The game level.

    Returns:
        AIAlgorithm: An instance of the requested AI algorithm.

    """
    LOGGER.debug(f"Getting class for algorithm: {ai_algorithm}")

    return AIAlgorithmRegistry.get_algorithm(ai_algorithm)(level)


def get_ai_algorithm_id(ai_algorithm: AIAlgorithm) -> AIAlgorithmID:
    """Get the identifier of an AI algorithm instance.

    Wrapper function to retrieve the identifier of an AI algorithm class,
    abstracting the implementation details of the storage of AI algorithms (in this case, the registry pattern).

    Args:
        ai_algorithm (AIAlgorithm): The AI algorithm instance.

    Returns:
        AIAlgorithmID: The identifier of the requested AI algorithm.

    """
    return AIAlgorithmRegistry.get_algorithm_id(ai_algorithm)
