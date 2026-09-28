# Memory & Knowledge Fabric

```
MEMORY
  ├── Context Memory
  ├── Semantic Memory
  ├── Episodic Memory
  └── Knowledge Graph → World Memory
```

Storage: Vector DB, SQL, Graph DB, Object storage, Local files, Model parameters

## Continual Learning Five Levels

- L0 Context
- L1 Working Memory
- L2 Retrieval
- L3 Adapter
- L4 Validated Weight Update

Avoids blindly modifying foundation model after every interaction.

## Test-Time Adaptation

Frozen Base → Temporary Adapter + Task State
Input → Adaptation → Inference → Validation → Discard or retain adaptation
Permanent weight modification requires separate validation pipeline.
