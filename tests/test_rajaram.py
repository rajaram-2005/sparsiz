import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sparsiz.rajaram import RajaramCore, SystemState, PermissionMatrix

def test_state_machine():
    core = RajaramCore()
    assert core.state_machine.current == SystemState.BOOT
    core.state_machine.transition(SystemState.SELF_TEST)
    core.state_machine.transition(SystemState.INITIALIZE)
    core.state_machine.transition(SystemState.READY)
    assert core.state_machine.is_ready()
    # Fault from any
    core.state_machine.transition(SystemState.FAULT)
    assert core.state_machine.current == SystemState.FAULT
    core.state_machine.transition(SystemState.ISOLATE)
    core.state_machine.transition(SystemState.DIAGNOSE)
    core.state_machine.transition(SystemState.READY)
    print("test_state_machine PASSED")

def test_permission_matrix():
    pm = PermissionMatrix()
    assert pm.is_authorized("SARAM","CPU")
    assert pm.is_authorized("SARAM","BCI")
    assert not pm.is_authorized("SARAM","PLC")
    assert not pm.is_authorized("SARAM","Actuator")
    assert pm.is_authorized("PREMSOTH","Actuator")
    print("test_permission_matrix PASSED")

def test_pipeline():
    core = RajaramCore()
    core.initialize()
    task = {"task_id":"T001","module":"SARAM","resource":"CPU"}
    result = core.execute_pipeline(task)
    assert result["authorized"]
    assert "token" in result
    print("test_pipeline PASSED")

if __name__ == "__main__":
    test_state_machine()
    test_permission_matrix()
    test_pipeline()
    print("All RAJARAM tests passed")
