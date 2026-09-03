"""Live ClinicalTrials.gov integration for the multiple-sclerosis use case."""

from __future__ import annotations

import html
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx


ACTIVE_STATUSES = (
    "RECRUITING",
    "NOT_YET_RECRUITING",
    "ENROLLING_BY_INVITATION",
    "ACTIVE_NOT_RECRUITING",
)


@dataclass(frozen=True)
class TrialRecord:
    nct_id: str
    title: str
    status: str
    phase: str
    study_type: str
    sponsor: str
    eligibility: str
    locations: List[str]
    intervention_types: List[str]
    last_update: str
    url: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ClinicalTrialsClient:
    """Fetch currently available MS studies from the public CT.gov API v2."""

    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

    def __init__(self, timeout: float = 20.0, client: Optional[httpx.Client] = None):
        self.timeout = timeout
        self.client = client or httpx.Client(timeout=timeout)

    def close(self) -> None:
        self.client.close()

    def search_ms_trials(self, page_size: int = 100) -> List[TrialRecord]:
        params = {
            "query.cond": "Multiple Sclerosis",
            "filter.overallStatus": "|".join(ACTIVE_STATUSES),
            "pageSize": min(max(page_size, 1), 1000),
            "format": "json",
        }
        response = self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        payload = response.json()
        studies = payload.get("studies", [])
        if not isinstance(studies, list):
            raise ValueError("ClinicalTrials.gov response has an invalid studies field")
        return [self._parse_study(study) for study in studies]

    @staticmethod
    def _parse_study(study: Dict[str, Any]) -> TrialRecord:
        protocol = study.get("protocolSection", {})
        identification = protocol.get("identificationModule", {})
        status_module = protocol.get("statusModule", {})
        design = protocol.get("designModule", {})
        sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
        eligibility_module = protocol.get("eligibilityModule", {})
        contacts_module = protocol.get("contactsLocationsModule", {})
        arms_module = protocol.get("armsInterventionsModule", {})

        nct_id = str(identification.get("nctId", "unknown"))
        locations = [
            ", ".join(filter(None, [location.get("city"), location.get("country")]))
            for location in contacts_module.get("locations", [])
            if isinstance(location, dict)
        ]
        interventions = [
            intervention.get("type", "Not reported")
            for intervention in arms_module.get("interventions", [])
            if isinstance(intervention, dict)
        ]
        return TrialRecord(
            nct_id=nct_id,
            title=str(identification.get("briefTitle", "Untitled study")),
            status=str(status_module.get("overallStatus", "UNKNOWN")),
            phase=", ".join(design.get("phases", [])) or "Not applicable",
            study_type=str(design.get("studyType", "Not reported")),
            sponsor=str(sponsor_module.get("leadSponsor", {}).get("name", "Not reported")),
            eligibility=str(eligibility_module.get("eligibilityCriteria", "Not reported")),
            locations=locations,
            intervention_types=sorted(set(interventions)),
            last_update=str(status_module.get("lastUpdatePostDateStruct", {}).get("date", "Not reported")),
            url=f"https://clinicaltrials.gov/study/{nct_id}",
        )


def summarize_trials(trials: List[TrialRecord]) -> Dict[str, Any]:
    """Create descriptive, non-causal activity summaries for the dashboard."""

    return {
        "total": len(trials),
        "status_counts": dict(Counter(trial.status for trial in trials)),
        "phase_counts": dict(Counter(trial.phase for trial in trials)),
        "intervention_counts": dict(
            Counter(kind for trial in trials for kind in trial.intervention_types)
        ),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "interpretation": (
            "Counts describe registered study activity. They are not evidence "
            "of treatment effectiveness, causation, or participant suitability."
        ),
    }


def render_ms_trials_page(trials: List[TrialRecord]) -> str:
    """Render an accessible standalone HTML page with live trial data."""

    summary = summarize_trials(trials)
    cards = []
    for trial in trials:
        locations = ", ".join(trial.locations[:4]) or "Locations not reported"
        interventions = ", ".join(trial.intervention_types) or "Not reported"
        cards.append(
            f"""
            <article class="trial-card">
              <div class="eyebrow">{html.escape(trial.status)} · {html.escape(trial.phase)}</div>
              <h2><a href="{html.escape(trial.url)}" target="_blank" rel="noreferrer">{html.escape(trial.title)}</a></h2>
              <p class="muted">{html.escape(trial.nct_id)} · {html.escape(trial.study_type)} · Sponsor: {html.escape(trial.sponsor)}</p>
              <div class="details"><span><b>Intervention:</b> {html.escape(interventions)}</span><span><b>Locations:</b> {html.escape(locations)}</span></div>
              <p><b>Eligibility:</b> {html.escape(trial.eligibility[:500])}</p>
              <p class="muted">Last registry update: {html.escape(trial.last_update)}</p>
            </article>
            """
        )
    status_items = "".join(
        f"<li><b>{html.escape(key)}</b><span>{value}</span></li>"
        for key, value in sorted(summary["status_counts"].items())
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Current active multiple sclerosis clinical trials from ClinicalTrials.gov.">
<meta name="theme-color" content="#102a43"><meta name="robots" content="index,follow">
<title>Multiple Sclerosis Clinical Trials Monitor | Trial Compass</title>
<style>
:root {{ --ink:#132238; --muted:#60748d; --line:#dce7f2; --blue:#2167e8; --mint:#0e9f8c; --navy:#102a43; --bg:#f5f8fc; }}
* {{ box-sizing:border-box; }} body {{ margin:0; font-family:Inter,Segoe UI,Arial,sans-serif; color:var(--ink); background:radial-gradient(circle at 88% 8%,#dceaff 0,transparent 30%),var(--bg); }}
.shell {{ max-width:1220px; margin:auto; padding:36px 22px 60px; }} .hero {{ display:flex; justify-content:space-between; gap:24px; align-items:end; margin-bottom:24px; padding:28px; color:white; background:linear-gradient(135deg,var(--navy),#2167e8); border-radius:24px; box-shadow:0 18px 42px #102a4326; }}
h1 {{ font-size:clamp(2rem,4vw,3.5rem); margin:8px 0; letter-spacing:-.04em; }} h2 {{ font-size:1.15rem; line-height:1.35; margin:10px 0; }}
.kicker,.eyebrow {{ color:var(--blue); font-size:.76rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }}
.note {{ background:#fff6dc; border:1px solid #f1d58a; border-radius:14px; padding:14px 16px; color:#684d0d; }}
.dashboard {{ display:grid; grid-template-columns:1fr 2fr; gap:18px; margin:20px 0; }} .panel,.trial-card {{ background:white; border:1px solid var(--line); border-radius:18px; box-shadow:0 14px 34px #102a4310; }}
.panel {{ padding:20px; }} .total {{ font-size:3rem; font-weight:800; color:var(--blue); }} ul {{ list-style:none; padding:0; margin:12px 0 0; }}
li {{ display:flex; justify-content:space-between; padding:9px 0; border-bottom:1px solid var(--line); }} .muted {{ color:var(--muted); font-size:.9rem; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(330px,1fr)); gap:16px; }} .trial-card {{ padding:20px; transition:transform .2s,box-shadow .2s; }} .trial-card:hover {{ transform:translateY(-3px); box-shadow:0 18px 42px #102a431d; }}
a {{ color:var(--blue); text-decoration:none; }} a:hover {{ text-decoration:underline; }} .details {{ display:grid; gap:8px; font-size:.92rem; margin:16px 0; }}
footer {{ margin-top:28px; color:var(--muted); font-size:.86rem; }} @media(max-width:750px) {{ .hero,.dashboard {{ display:block; }} .hero .note {{ margin-top:18px; }} .panel {{ margin-bottom:16px; }} }}
</style></head><body><main class="shell">
<div class="hero"><div><div class="kicker">Scientific activity monitor</div><h1>Multiple sclerosis clinical trials</h1><p class="muted">Live registry view of studies currently open or active in ClinicalTrials.gov.</p></div>
<div class="note"><b>Information only.</b><br>Eligibility must be confirmed with the study team and a qualified clinician.</div></div>
<section class="dashboard"><div class="panel"><div class="kicker">Current studies</div><div class="total">{summary["total"]}</div><div class="muted">Retrieved {html.escape(summary["updated_at"])}</div></div>
<div class="panel"><div class="kicker">Activity by registry status</div><ul>{status_items or "<li>No active studies returned</li>"}</ul></div></section>
<section class="grid">{"".join(cards) or '<div class="panel">No studies returned. Try refreshing later.</div>'}</section>
<footer>Source: <a href="https://clinicaltrials.gov/" target="_blank" rel="noreferrer">ClinicalTrials.gov</a>. Registry counts are descriptive correlations of study activity, not clinical outcomes or proof of effectiveness. This page is a work in progress.</footer>
</main></body></html>"""
