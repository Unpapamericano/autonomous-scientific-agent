import httpx

from src.research.clinical_trials import (
    ClinicalTrialsClient,
    TrialRecord,
    render_ms_trials_page,
    summarize_trials,
)


def test_client_parses_clinicaltrials_response():
    payload = {
        "studies": [{
            "protocolSection": {
                "identificationModule": {"nctId": "NCT0001", "briefTitle": "MS study"},
                "statusModule": {"overallStatus": "RECRUITING", "lastUpdatePostDateStruct": {"date": "2026-01-01"}},
                "designModule": {"phases": ["PHASE2"], "studyType": "INTERVENTIONAL"},
                "sponsorCollaboratorsModule": {"leadSponsor": {"name": "Example University"}},
                "eligibilityModule": {"eligibilityCriteria": "Adults with MS"},
                "contactsLocationsModule": {"locations": [{"city": "Berlin", "country": "Germany"}]},
                "armsInterventionsModule": {"interventions": [{"type": "DRUG"}]},
            }
        }]
    }
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    client = ClinicalTrialsClient(client=httpx.Client(transport=transport))
    try:
        trials = client.search_ms_trials()
    finally:
        client.close()

    assert trials[0].nct_id == "NCT0001"
    assert trials[0].locations == ["Berlin, Germany"]
    assert trials[0].intervention_types == ["DRUG"]


def test_summary_and_page_disclose_non_causal_interpretation():
    trial = TrialRecord(
        "NCT1", "MS intervention", "RECRUITING", "PHASE1", "INTERVENTIONAL",
        "Sponsor", "Adults", ["London, UK"], ["BIOLOGICAL"], "2026-01-01",
        "https://clinicaltrials.gov/study/NCT1",
    )
    summary = summarize_trials([trial])
    page = render_ms_trials_page([trial])

    assert summary["total"] == 1
    assert "not evidence of treatment effectiveness" in summary["interpretation"]
    assert "Information only" in page
    assert "ClinicalTrials.gov" in page
