"""
Y-Bus Simulation: Y=G+jB, Y† pseudoinverse, topology estimation → optimization → route
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from sparsiz.faisanth import Faisanth, ComputeGraph, YBus

def simulate_ybus():
    print("=== Y-Bus Power Grid Simulation for Compute Network ===")
    graph = ComputeGraph.default_10_nodes()
    ybus = YBus(graph)

    print(ybus.display())
    print(ybus.topology_estimation())

    print("\n--- Admittance Examples ---")
    for edge in graph.edges[:3]:
        adm = ybus.get_admittance(edge.from_id, edge.to_id)
        print(f"{edge.from_id} -> {edge.to_id}: G={adm['G']:.3f}, B={adm['B']:.3f}, |Y|={adm['mag']:.3f} (G=bandwidth/latency, B=reliability)")

    print("\n--- Y† Moore-Penrose Pseudoinverse ---")
    print("Do NOT claim Y† automatically produces exact optimal computational route")
    print("Flow: Compute topology → Admittance representation → Y matrix → Network-state estimation → Optimization → Selected route")
    print("This turns EEE/power-system concept into genuine research direction")

    try:
        import numpy as np
        Y = np.array(ybus.Y)
        print(f"\nY matrix shape: {Y.shape}")
        print(f"Y matrix (real part):\n{np.real(Y)[:3,:3]}")
        print(f"Y matrix (imag part):\n{np.imag(Y)[:3,:3]}")

        # Regularization for invertibility
        Y_reg = Y + np.eye(ybus.n) * complex(0.001, 0.001)
        Y_pinv = np.linalg.pinv(Y_reg)
        print(f"\nY† pseudoinverse shape: {Y_pinv.shape}")
        print(f"Y† (real part):\n{np.real(Y_pinv)[:3,:3]}")

        # Example: network-state estimation via Y * V = I (power flow analogy)
        # For compute network, V could be node load, I could be task demand
        # Solve for V = Y† * I
        I = np.random.rand(ybus.n) + 1j*np.random.rand(ybus.n)
        V = Y_pinv @ I
        print(f"\nExample state estimation: I (demand) -> V (load) via V=Y†*I")
        print(f"I: {I[:3]}")
        print(f"V: {V[:3]}")

    except ImportError:
        print("Numpy not available, showing placeholder logic")
        print(f"Y matrix {ybus.n}x{ybus.n} would be inverted via SVD in production")

    print("\n--- Optimization Algorithm using Y-Bus ---")
    print("1. Compute topology from Y-Bus")
    print("2. Admittance representation G+jB")
    print("3. Y matrix")
    print("4. Network-state estimation")
    print("5. Optimization algorithm (constrained: Capacity>=Demand, Temp<Tmax, Memory>=M_req)")
    print("6. Selected route")

if __name__ == "__main__":
    simulate_ybus()
