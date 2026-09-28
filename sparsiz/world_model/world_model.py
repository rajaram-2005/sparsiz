"""
WORLD MODEL

World state s_t, Action a_t, Prediction \hat{s}_{t+1}=f_θ(s_t,a_t)

Observation → World State → Predict futures → Evaluate futures → Select action

Useful for robotics, industrial systems and simulation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import random

@dataclass
class WorldState:
    t: int
    state: Dict[str, Any]

@dataclass
class Action:
    name: str
    parameters: Dict[str, Any] = field(default_factory=dict)

class WorldModel:
    """
    \hat{s}_{t+1}=f_θ(s_t,a_t)
    """
    def __init__(self):
        self.history: List[WorldState] = []

    def predict(self, s_t: WorldState, a_t: Action) -> WorldState:
        # Mock f_θ(s_t,a_t) — in production would be learned neural model
        next_state = s_t.state.copy()

        if a_t.name == "increase_voltage":
            next_state["voltage"] = next_state.get("voltage", 400) + a_t.parameters.get("delta", 10)
            next_state["power"] = next_state["voltage"] * next_state.get("current", 14.2)  # P=VI

        if a_t.name == "investigate_bearing":
            next_state["vibration"] = next_state.get("vibration", 8.3) * 0.9  # investigation reduces vibration mock
            next_state["fault_probability"] = 0.2

        if a_t.name == "motor_start":
            next_state["rpm"] = 1480
            next_state["omega"] = 155
            next_state["mech_power"] = next_state.get("torque", 50) * 155  # Tω

        predicted = WorldState(t=s_t.t+1, state=next_state)
        self.history.append(predicted)
        return predicted

    def predict_futures(self, s_t: WorldState, actions: List[Action], horizon: int = 3) -> List[List[WorldState]]:
        futures = []
        for action in actions:
            future = []
            current = s_t
            for _ in range(horizon):
                current = self.predict(current, action)
                future.append(current)
            futures.append(future)
        return futures

    def evaluate_future(self, future: List[WorldState]) -> float:
        # Evaluate future: lower vibration, temperature, energy good
        last = future[-1].state
        score = 0.0
        # Prefer low vibration
        score += max(0, 10 - last.get("vibration", 5))
        # Prefer low temperature
        score += max(0, 100 - last.get("temperature", 70)) / 10
        # Prefer low fault probability
        score += (1.0 - last.get("fault_probability", 0.5)) * 10
        return score

    def select_action(self, s_t: WorldState, actions: List[Action]) -> Action:
        futures = self.predict_futures(s_t, actions, horizon=3)
        best_action = None
        best_score = -1

        for action, future in zip(actions, futures):
            score = self.evaluate_future(future)
            print(f"Action {action.name} future score={score:.2f} final state={future[-1].state}")
            if score > best_score:
                best_score = score
                best_action = action

        print(f"Selected action: {best_action.name} with score {best_score:.2f}")
        return best_action

if __name__ == "__main__":
    wm = WorldModel()

    s0 = WorldState(t=0, state={"vibration": 8.3, "current": 14.2, "temperature": 81, "rpm": 0, "voltage": 400, "power": 5680, "fault_probability": 0.85})

    actions = [
        Action("investigate_bearing", {}),
        Action("increase_voltage", {"delta": 20}),
        Action("motor_start", {}),
        Action("normal_operation", {}),
    ]

    print("=== World Model: Observation → World State → Predict futures → Evaluate futures → Select action ===")
    print(f"Initial state s0: {s0.state}")

    selected = wm.select_action(s0, actions)

    # Simulate execution
    s1 = wm.predict(s0, selected)
    print(f"Next state s1 after {selected.name}: {s1.state}")
