from src.research.context_notes import ContextNote, ContextNoteStore


def test_context_notes_round_trip_and_search(tmp_path):
    store = ContextNoteStore(tmp_path / "notes.jsonl")
    store.add(ContextNote("n1", "Use ClinicalTrials.gov for current MS registry status", "decision"))
    store.add(ContextNote("n2", "Review the evidence date before synthesis", "question"))

    results = store.search("clinicaltrials current")

    assert [note.note_id for note in results] == ["n1"]
