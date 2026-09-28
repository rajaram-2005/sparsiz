# Y-Bus Mathematics

## Construct Y = G + jB

For compute network, Y matrix represents relationships between computational nodes.

- G (conductance) proxy: bandwidth / latency, capacity
- B (susceptance) proxy: reliability, specialization

## Matrix Construction

For edge i,j:
- Y_ii += y_ij + y_self
- Y_ij -= y_ij
- Y_jj += y_ij + y_self
- Y_ji -= y_ij

where y_ij = G_ij + jB_ij

## Pseudoinverse Y†

Investigate Y† Moore-Penrose pseudoinverse where Y† is defined via SVD.

But: Do NOT state that Y† automatically produces exact optimal computational route.

Correct flow:

```
Compute topology
       ↓
Admittance representation
       ↓
Y matrix
       ↓
Network-state estimation (e.g., Y*V=I, solve V=Y†*I)
       ↓
Optimization algorithm (constrained)
       ↓
Selected route
```

## Optimization

Cost: C_ij = α L_ij + β E_ij + γ T_ij + δ B_ij^{-1} + ε R_ij

Route: P* = argmin C(P) s.t. Capacity_i >= Demand_i, Temperature_i < T_max, Memory_i >= M_required

Y-Bus provides topology estimation that informs optimization, not replaces it.

## Example

```python
Y = [[G11+jB11, -G12-jB12, ...],
     [-G21-jB21, G22+jB22, ...],
     ...]
Y† = pinv(Y) via SVD
V = Y† * I  # state estimation
```

## Research Direction

Turns EEE/power-system concept into genuine research direction for compute routing.
