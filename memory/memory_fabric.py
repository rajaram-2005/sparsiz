"""
MEMORY FABRIC
MEMORY
  ├── Context Memory
  ├── Semantic Memory
  ├── Episodic Memory
  └── Knowledge Graph → World Memory

Storage: Vector DB, SQL, Graph DB, Object storage, Local files, Model parameters

Five levels continual learning:
L0 Context
L1 Working Memory
L2 Retrieval
L3 Adapter
L4 Validated Weight Update

Avoids blindly modifying foundation model after every interaction
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import time
import hashlib

class MemoryLevel(Enum):
    L0_CONTEXT = "L0_context"
    L1_WORKING = "L1_working"
    L2_RETRIEVAL = "L2_retrieval"
    L3_ADAPTER = "L3_adapter"
    L4_VALIDATED = "L4_validated"

class MemoryType(Enum):
    CONTEXT = "context"
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    VECTOR = "vector"
    GRAPH = "graph"
    WORLD = "world"

@dataclass
class MemoryEntry:
    id: str
    type: MemoryType
    content: Any
    level: MemoryLevel
    timestamp: int = field(default_factory=lambda: int(time.time()))
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            self.hash = hashlib.sha256(str(self.content).encode()).hexdigest()[:16]

class ContextMemory:
    def __init__(self, max_size: int = 100):
        self.entries: List[MemoryEntry] = []
        self.max_size = max_size

    def add(self, content: Any) -> MemoryEntry:
        entry = MemoryEntry(id=f"ctx_{len(self.entries)}", type=MemoryType.CONTEXT, content=content, level=MemoryLevel.L0_CONTEXT)
        self.entries.append(entry)
        if len(self.entries) > self.max_size:
            self.entries.pop(0)
        return entry

    def get_recent(self, n: int = 10) -> List[MemoryEntry]:
        return self.entries[-n:]

class WorkingMemory:
    def __init__(self):
        self.entries: List[MemoryEntry] = []

    def add(self, content: Any) -> MemoryEntry:
        entry = MemoryEntry(id=f"work_{len(self.entries)}", type=MemoryType.CONTEXT, content=content, level=MemoryLevel.L1_WORKING)
        self.entries.append(entry)
        return entry

    def clear(self):
        self.entries.clear()

class EpisodicMemory:
    def __init__(self):
        self.entries: List[MemoryEntry] = []

    def add_episode(self, episode: Dict[str, Any]) -> MemoryEntry:
        entry = MemoryEntry(id=f"epi_{len(self.entries)}", type=MemoryType.EPISODIC, content=episode, level=MemoryLevel.L2_RETRIEVAL)
        self.entries.append(entry)
        return entry

    def recall(self, query: str) -> List[MemoryEntry]:
        # Mock recall — in production use vector search
        return [e for e in self.entries if query.lower() in str(e.content).lower()][:5]

class SemanticMemory:
    def __init__(self):
        self.entries: List[MemoryEntry] = []
        self.knowledge_graph: Dict[str, List[str]] = {}

    def add_fact(self, fact: str, entities: List[str]) -> MemoryEntry:
        entry = MemoryEntry(id=f"sem_{len(self.entries)}", type=MemoryType.SEMANTIC, content=fact, level=MemoryLevel.L2_RETRIEVAL, metadata={"entities": entities})
        self.entries.append(entry)
        for ent in entities:
            if ent not in self.knowledge_graph:
                self.knowledge_graph[ent] = []
            self.knowledge_graph[ent].append(fact)
        return entry

    def query(self, entity: str) -> List[str]:
        return self.knowledge_graph.get(entity, [])

class VectorMemory:
    def __init__(self, dim: int = 128):
        self.dim = dim
        self.entries: List[MemoryEntry] = []

    def add(self, content: Any, embedding: List[float]) -> MemoryEntry:
        entry = MemoryEntry(id=f"vec_{len(self.entries)}", type=MemoryType.VECTOR, content=content, level=MemoryLevel.L2_RETRIEVAL, embedding=embedding)
        self.entries.append(entry)
        return entry

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[MemoryEntry]:
        # Mock cosine similarity
        import math
        def cosine(a,b):
            dot = sum(x*y for x,y in zip(a,b))
            norm_a = math.sqrt(sum(x*x for x in a))
            norm_b = math.sqrt(sum(y*y for y in b))
            return dot / (norm_a*norm_b+1e-6)

        scored = [(e, cosine(query_embedding, e.embedding)) for e in self.entries if e.embedding]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [e for e,_ in scored[:top_k]]

class GraphMemory:
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, str]] = []

    def add_node(self, id: str, data: Dict[str, Any]):
        self.nodes[id] = data

    def add_edge(self, from_id: str, to_id: str, relation: str):
        self.edges.append({"from": from_id, "to": to_id, "relation": relation})

    def traverse(self, start_id: str, relation: Optional[str] = None) -> List[str]:
        result = []
        for edge in self.edges:
            if edge["from"] == start_id and (relation is None or edge["relation"] == relation):
                result.append(edge["to"])
        return result

class WorldMemory:
    def __init__(self):
        self.state: Dict[str, Any] = {}

    def update(self, key: str, value: Any):
        self.state[key] = value

    def get(self, key: str) -> Any:
        return self.state.get(key)

class MemoryFabric:
    def __init__(self):
        self.context = ContextMemory()
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.vector = VectorMemory()
        self.graph = GraphMemory()
        self.world = WorldMemory()

    def continual_learning_level(self, content: Any, level: MemoryLevel) -> str:
        """
        Five levels:
        L0 Context
        L1 Working Memory
        L2 Retrieval
        L3 Adapter
        L4 Validated Weight Update
        Avoids blindly modifying foundation model after every interaction
        """
        if level == MemoryLevel.L0_CONTEXT:
            self.context.add(content)
            return "Added to L0 Context (temporary, not persisted)"
        elif level == MemoryLevel.L1_WORKING:
            self.working.add(content)
            return "Added to L1 Working Memory (session)"
        elif level == MemoryLevel.L2_RETRIEVAL:
            self.episodic.add_episode({"content": content})
            return "Added to L2 Retrieval (vector/graph searchable)"
        elif level == MemoryLevel.L3_ADAPTER:
            return "Added to L3 Adapter (temporary adapter, task state, discarded or retained after validation)"
        elif level == MemoryLevel.L4_VALIDATED:
            return "Added to L4 Validated Weight Update (requires separate validation pipeline, permanent)"
        return "Unknown level"

if __name__ == "__main__":
    fabric = MemoryFabric()

    # Context
    fabric.context.add("User: What is bearing fault detection?")
    fabric.context.add("Assistant: Bearing fault detection uses vibration and current...")

    # Semantic
    fabric.semantic.add_fact("P=VI", ["power","voltage","current"])
    fabric.semantic.add_fact("S=P+jQ", ["apparent power","real power","reactive power"])
    fabric.semantic.add_fact("P_mech=Tω", ["mechanical power","torque","omega"])

    print(f"Semantic query power: {fabric.semantic.query('power')}")
    print(f"Context recent: {[e.content for e in fabric.context.get_recent(2)]}")

    # Episodic
    fabric.episodic.add_episode({"task": "motor fault", "vibration": 8.3, "result": "bearing fault 0.88"})
    print(f"Episodic recall motor: {fabric.episodic.recall('motor')}")

    # Graph
    fabric.graph.add_node("motor", {"type": "machine"})
    fabric.graph.add_node("bearing", {"type": "component"})
    fabric.graph.add_edge("motor", "bearing", "has_component")
    print(f"Graph traverse motor has_component: {fabric.graph.traverse('motor', 'has_component')}")

    # World
    fabric.world.update("motor_temperature", 81)
    print(f"World memory motor_temperature: {fabric.world.get('motor_temperature')}")

    # Continual learning levels
    for level in MemoryLevel:
        print(f"{level.value}: {fabric.continual_learning_level('test content', level)}")
