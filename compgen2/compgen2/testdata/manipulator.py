from typing import Callable

class Manipulator:
    def __init__(self, m: Callable, type: str, chance: float) -> None:
        self.m = m
        self.type = self.set_type(type)
        self.chance = self.set_chance(chance)
    
    def set_type(self, type: str) -> str:
        """Read in a type and check on its correctness
        Args:
          type (str): Can be any of "char", "word". Other values will produce a ValueError
        Returns:
          type (str): If valid, it passes the input value.
        """
        if type in ["char", "word"]:
            return type
        else:
            raise ValueError("Invalid type provided.")
            
    def set_chance(self, chance: float) -> float:
        """Read in a probability and check on its correctness
        Args:
          chance (float): Should be a float between 0. and 1. However, any float can be provided
        Returns:
          chance (float): If valid, it passes the input value.
        """
        if type(chance) == float:
            return chance
        else:
            raise ValueError("Invalid value for chance provided. Must be of type float.")
