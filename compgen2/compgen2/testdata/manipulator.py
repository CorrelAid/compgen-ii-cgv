from typing import Callable

class Manipulator:
    def __init__(self, m: Callable, type: str, chance: float) -> None:
        self.m = m
        self.type = self.set_type(type)
        self.chance = self.set_chance(chance)
    
    def set_type(self, type: str):
        if type in ["char", "word"]:
            return type
        else:
            raise ValueError("Invalid type provided.")
            
    def set_chance(self, chance: float):
        if type(chance) == float:
            return chance
        else:
            raise ValueError("Invalid value for chance provided. Must be of type float.")
