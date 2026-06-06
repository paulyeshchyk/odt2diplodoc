# diplodoc_converter/strategies/pipeline.py
from typing import List
from .base import TransformationStrategy

class Pipeline:
    """Последовательно применяет список стратегий."""
    
    def __init__(self, strategies: List[TransformationStrategy]):
        self.strategies = strategies
    
    def run(self, content: str) -> str:
        for strategy in self.strategies:
            content = strategy.transform(content)
        return content