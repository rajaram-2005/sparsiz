# Model Fabric

```
Dense │ MoE │ Reasoning │ Multimodal │ Vision │ Audio │ SSM │ World Models │ Specialist Models │ Embedding │ Reranker │ Verifier
```

## Model Family

```
FOUNDATION MODEL
  ├── LANGUAGE, VISION, AUDIO
  └── MULTIMODAL
       ├── CODE, SCIENCE, ROBOTICS
       └── AGENT
            └── WORLD MODEL
```

## Mixture of Experts

Input → Router → Mathematics Expert, Coding Expert, Physics Expert, Vision Expert, Language Expert, Planning Expert, Safety Expert → Aggregation → Output
Expert selection: p(e_i|x) and TopK(x)

## Hardware-Aware Expert Routing

Instead of Expert=Router(x) use Expert=f(x,H,T,M,L,E) where H hardware T thermal M memory L latency E energy
Question → Expert Router → FAISANTH → Expert + Hardware → Execution

## Local Model Registry

Every installed model has: model ID, architecture, parameters, quantization, modalities, capabilities, hardware requirements, license, evaluation score, safety status, version, hash
RAJARAM selects models automatically.
