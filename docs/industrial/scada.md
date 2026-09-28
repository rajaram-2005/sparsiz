# Industrial SCADA Integration

## Recommended Flow

```
PLC
 ├── Modbus TCP
 ├── OPC UA
 └── MQTT gateway
        ↓
    SARAM
        ↓
    FAISANTH
        ↓
    AI agents
        ↓
   PREMSOTH
        ↓
 Safety layer
        ↓
 PLC / HMI
```

For safety-critical industrial control, keep deterministic control logic independent from AI system.

## Safety Layer

```
AI recommendation
       ↓
PREMSOTH
       ↓
Safety policy engine
       ↓
Range checking (Vmin≤V≤Vmax, I≤Imax, T<Tcritical)
       ↓
Interlock checking
       ↓
Human/authorized controller
       ↓
PLC
```

## Testbed

Laboratory testbed:

```
Sensor
  ↓
Raspberry Pi / industrial PC
  ↓
MQTT / OPC UA
  ↓
The Last Dance
  ↓
Simulation
```

Use simulated PLC before connecting physical machinery.
