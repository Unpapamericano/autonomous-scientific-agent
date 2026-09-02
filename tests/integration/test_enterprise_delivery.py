from src.research.enterprise_delivery import (
    DeliveryStage,
    default_delivery_gates,
    next_ready_stage,
)


def test_default_workflow_starts_with_discovery():
    gates = default_delivery_gates()

    assert next_ready_stage(gates) == DeliveryStage.DISCOVER
    assert gates[0].passed is False


def test_gates_advance_only_after_required_evidence():
    gates = default_delivery_gates()
    for check in gates[0].required_checks:
        gates[0].complete(check)

    assert gates[0].passed is True
    assert next_ready_stage(gates) == DeliveryStage.DESIGN


def test_unknown_gate_check_is_rejected():
    gate = default_delivery_gates()[0]

    try:
        gate.complete("deploy_without_review")
    except ValueError as exc:
        assert "Unknown check" in str(exc)
    else:
        raise AssertionError("Expected unknown checks to fail")
