"""
CURRICULUM ENGINE — Training difficulty dynamic

D(x)∈[0,1] difficulty
P(x)=f(difficulty, failure frequency, novelty, model capability)
Thus: Easy → Medium → Hard → Failure cases → Adversarial cases → Research-level cases
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import random

class DifficultyLevel(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    FAILURE = "failure"
    ADVERSARIAL = "adversarial"
    RESEARCH = "research"

@dataclass
class CurriculumSample:
    id: str
    content: str
    difficulty: float  # D(x)∈[0,1]
    failure_frequency: float = 0.0
    novelty: float = 0.5
    model_capability: float = 0.5
    level: DifficultyLevel = DifficultyLevel.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)

    def probability(self) -> float:
        """
        P(x)=f(difficulty, failure frequency, novelty, model capability)
        Higher probability for samples that address current weaknesses
        """
        # If model capability low, prefer easier; if high, prefer harder and failure cases
        # If failure frequency high, increase probability
        # If novelty high, increase
        p = (
            0.3 * (1.0 - abs(self.difficulty - self.model_capability))  # match capability
            + 0.4 * self.failure_frequency  # focus on failures
            + 0.2 * self.novelty
            + 0.1 * self.difficulty  # slight bias to harder
        )
        return max(0.0, min(1.0, p))

class CurriculumEngine:
    def __init__(self):
        self.samples: List[CurriculumSample] = []
        self.current_stage: DifficultyLevel = DifficultyLevel.EASY
        self.model_capability: float = 0.3

    def add_samples(self, samples: List[CurriculumSample]):
        self.samples.extend(samples)

    def classify_level(self, difficulty: float, failure_freq: float) -> DifficultyLevel:
        if failure_freq > 0.7:
            return DifficultyLevel.FAILURE
        if difficulty < 0.3:
            return DifficultyLevel.EASY
        elif difficulty < 0.5:
            return DifficultyLevel.MEDIUM
        elif difficulty < 0.7:
            return DifficultyLevel.HARD
        elif difficulty < 0.9:
            return DifficultyLevel.ADVERSARIAL
        else:
            return DifficultyLevel.RESEARCH

    def update_model_capability(self, eval_score: float):
        # As model improves, capability increases
        self.model_capability = eval_score
        # Advance curriculum stage
        if eval_score > 0.9:
            self.current_stage = DifficultyLevel.RESEARCH
        elif eval_score > 0.8:
            self.current_stage = DifficultyLevel.ADVERSARIAL
        elif eval_score > 0.6:
            self.current_stage = DifficultyLevel.HARD
        elif eval_score > 0.4:
            self.current_stage = DifficultyLevel.MEDIUM
        else:
            self.current_stage = DifficultyLevel.EASY

    def select_batch(self, batch_size: int = 32) -> List[CurriculumSample]:
        # Calculate P(x) for each sample with current model capability
        for s in self.samples:
            s.model_capability = self.model_capability

        # Weight by probability
        weighted = [(s, s.probability()) for s in self.samples]
        weighted.sort(key=lambda x: x[1], reverse=True)

        # Select top + some random for exploration
        top_n = int(batch_size * 0.8)
        random_n = batch_size - top_n

        selected = [s for s,_ in weighted[:top_n]]
        remaining = [s for s,_ in weighted[top_n:]]
        selected.extend(random.sample(remaining, min(random_n, len(remaining))))

        return selected

    def get_stage_distribution(self) -> Dict[str, int]:
        dist = {level.value: 0 for level in DifficultyLevel}
        for s in self.samples:
            level = self.classify_level(s.difficulty, s.failure_frequency)
            dist[level.value] += 1
        return dist

    def generate_curriculum_plan(self) -> List[Dict[str, Any]]:
        """
        Easy → Medium → Hard → Failure cases → Adversarial cases → Research-level cases
        """
        return [
            {"stage": "Easy", "difficulty_range": [0.0, 0.3], "focus": "foundational", "model_capability_needed": 0.0},
            {"stage": "Medium", "difficulty_range": [0.3, 0.5], "focus": "core skills", "model_capability_needed": 0.3},
            {"stage": "Hard", "difficulty_range": [0.5, 0.7], "focus": "advanced reasoning", "model_capability_needed": 0.5},
            {"stage": "Failure cases", "difficulty_range": [0.5, 1.0], "focus": "previous failures", "model_capability_needed": 0.6},
            {"stage": "Adversarial cases", "difficulty_range": [0.7, 0.9], "focus": "robustness", "model_capability_needed": 0.75},
            {"stage": "Research-level", "difficulty_range": [0.9, 1.0], "focus": "frontier", "model_capability_needed": 0.9},
        ]

if __name__ == "__main__":
    engine = CurriculumEngine()

    samples = [
        CurriculumSample(id=f"s{i}", content=f"Sample {i}", difficulty=random.random(), failure_frequency=random.random(), novelty=random.random())
        for i in range(100)
    ]
    engine.add_samples(samples)

    print(f"Stage distribution: {engine.get_stage_distribution()}")
    print(f"Curriculum plan: {engine.generate_curriculum_plan()}")

    for capability in [0.2, 0.5, 0.8, 0.95]:
        engine.update_model_capability(capability)
        batch = engine.select_batch(10)
        print(f"\nModel capability {capability}, stage {engine.current_stage.value}, selected batch difficulties: {[f'{s.difficulty:.2f}' for s in batch[:5]]}...")
        print(f"  P(x) examples: {[f'{s.probability():.2f}' for s in batch[:3]]}")
