from src.research.loop_engineering import LoopEngineer


def test_loop_engineer_runs_until_review_stops():
    seen = []

    loop = LoopEngineer(
        "Improve evidence coverage",
        define=lambda objective, iteration: {"objective": objective},
        build=lambda definition, iteration: {"artifact": iteration},
        measure=lambda artifact, iteration: {"coverage": artifact["artifact"] / 2},
        review=lambda metrics, artifact, iteration: metrics,
        iterate=lambda review, iteration: seen.append(review["coverage"]) or (
            "stop" if review["coverage"] >= 1 else "continue"
        ),
    )

    history = loop.run(max_iterations=3)

    assert len(history) == 2
    assert history[-1].decision == "stop"
    assert seen == [0.5, 1.0]


def test_loop_engineer_rejects_unbounded_invalid_configuration():
    loop = LoopEngineer(
        "Objective",
        define=lambda objective, iteration: objective,
        build=lambda definition, iteration: definition,
        measure=lambda artifact, iteration: artifact,
        review=lambda metrics, artifact, iteration: metrics,
        iterate=lambda review, iteration: "stop",
    )

    try:
        loop.run(max_iterations=0)
    except ValueError as exc:
        assert "at least 1" in str(exc)
    else:
        raise AssertionError("Expected invalid iteration count to fail")
