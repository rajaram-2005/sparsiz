# BCI Integration

## Isolated as data-ingestion subsystem

```
EEG / BCI
    ↓
Acquisition
    ↓
Filtering
    ↓
Artifact removal
    ↓
Feature extraction
    ↓
SARAM
    ↓
Latent representation
    ↓
AI agents
```

Do not allow raw BCI signals to directly trigger actuators.

## Phases

- Offline EEG dataset
- Real-time EEG
- SARAM streaming
- Real-time inference

Do not start with invasive neural interfaces.

## Data Types

- EEG
- ECoG
- Neural spikes
- Biopotential signals

## Safety

BCI must go through SARAM → FAISANTH → Agents → PREMSOTH → Safety gate → RAJARAM

Never direct BCI → actuator.
