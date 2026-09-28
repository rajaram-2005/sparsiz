import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sparsiz.saram import Saram, SaramConfig, PhysicsConstraints, IndustrialDataset

def test_compression():
    saram = Saram(SaramConfig(raw_dim=128, latent_dim=16))
    raw = IndustrialDataset.motor_example()
    latent, meta = saram.encode(raw)
    assert meta["compression_ratio"] == 8.0
    assert meta["latent_dim"] == 16
    assert meta["raw_dim"] == 128
    assert meta["physics_consistency"] > 0
    print(f"Compression {meta['raw_dim']}->{meta['latent_dim']} ratio={meta['compression_ratio']} PASSED")

def test_physics():
    sample = {"voltage":400,"current":14.2,"power":400*14.2,"torque":50,"omega":155,"mech_power":50*155}
    score = PhysicsConstraints.check_consistency(sample)
    assert score > 0.9
    print(f"Physics consistency {score:.2f} PASSED")

    # Test P=VI
    assert PhysicsConstraints.power_vi(400,14.2) == 5680.0
    # Test S=P+jQ
    s = PhysicsConstraints.apparent_power(100,50)
    assert s == complex(100,50)
    # Test P_mech=Tω
    assert PhysicsConstraints.mechanical_power(50,155) == 7750
    print("Physics formulas PASSED")

if __name__ == "__main__":
    test_compression()
    test_physics()
    print("All SARAM tests passed")
