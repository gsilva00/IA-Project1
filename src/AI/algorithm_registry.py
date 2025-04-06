class AIAlgorithmRegistry:
    """Registry for AI algorithms. (Registry Pattern)
    This class is used to register and retrieve AI algorithms.

    """

    _registry = {}

    @classmethod
    def register(cls, identifier, algorithm):
        """Register an AI algorithm with the registry.

        """

        cls._registry[identifier] = algorithm

    @classmethod
    def get_algorithm(cls, identifier):
        """Get an AI algorithm from the registry.

        Args:
            identifier (int): The identifier of the AI algorithm.

        Raises:
            ValueError: If the identifier is not found in the registry.

        Returns:
            AIAlgorithm: An instance of the requested AI algorithm.

        """

        if identifier not in cls._registry:
            raise ValueError(f"Unknown AI algorithm: {identifier}")
        return cls._registry[identifier]

    @classmethod
    def get_algorithm_id(cls, algorithm):
        """Get the identifier of an AI algorithm from the registry.

        Args:
            algorithm (AIAlgorithm): The AI algorithm instance.

        Raises:
            ValueError: If the AI algorithm is not found in the registry.

        Returns:
            int: The identifier of the requested AI algorithm.

        """

        print("Entering get_algorithm_id")
        print("Looking for algorithm:", algorithm)
        for identifier, alg in cls._registry.items():
            if isinstance(algorithm, alg):
                return identifier
        raise ValueError(f"Unknown AI algorithm: {algorithm}")

def get_ai_algorithm(ai_algorithm, level):
    """Wrapper function to get the AI algorithm instance based on the identifier.
    Abstracts the implementation details of the storage of AI algorithms (e.g., registry).

    Args:
        ai_algorithm (int): The identifier of the AI algorithm.
        level (int): The game level.

    Returns:
        AIAlgorithm: An instance of the requested AI algorithm.

    """

    print("Entering get_ai_algorithm")
    print("Getting class for algorithm:", ai_algorithm)

    return AIAlgorithmRegistry.get_algorithm(ai_algorithm)(level)

def get_ai_algorithm_id(ai_algorithm):
    """Wrapper function to get the identifier of an AI algorithm instance.
    Abstracts the implementation details of the storage of AI algorithms (e.g., registry).

    Args:
        ai_algorithm (AIAlgorithm): The AI algorithm instance.

    Returns:
        int: The identifier of the requested AI algorithm.

    """

    return AIAlgorithmRegistry.get_algorithm_id(ai_algorithm)
