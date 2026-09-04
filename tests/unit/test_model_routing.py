from src.core.model_routing import ModelProfile, TaskKind, choose_model


def test_bulk_tasks_prefer_low_cost_profile():
    decision = choose_model(
        TaskKind.BULK_EXTRACTION,
        [
            ModelProfile("local", 0.7, 1.0, 0.8),
            ModelProfile("frontier", 1.0, 10.0, 0.9, True),
        ],
    )
    assert decision.model == "local"


def test_cybersecurity_requires_confirmation():
    decision = choose_model(
        TaskKind.CYBERSECURITY,
        [ModelProfile("defensive", 0.9, 5.0, 0.8, True)],
    )
    assert decision.requires_confirmation is True
