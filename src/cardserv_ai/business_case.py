from __future__ import annotations
import pandas as pd


def calculate_business_case(
    contacts: pd.DataFrame,
    target_intents: list[str] | None = None,
    days_observed: int = 180,
    containment_rate: float = 0.30,
    loaded_hourly_cost: float = 34.0,
    ai_cost_per_interaction: float = 0.10,
    annual_platform_cost: float = 50000.0,
    one_time_build_cost: float = 80000.0,
    implementation_months: int = 6,
    annual_contact_volume: float | None = None,
) -> dict:
    """Illustrative planning model; projections are not actual issuer savings."""
    if target_intents is None:
        target_intents = ["interest_explanation", "payment_due", "fee_explanation", "payment_processing", "credit_limit"]
    if contacts.empty:
        return {k: 0.0 for k in ["annual_total_contacts", "annual_in_scope_contacts", "annual_contained_contacts", "aht_minutes", "gross_labor_savings", "ai_variable_cost", "annual_platform_cost", "steady_state_net_benefit", "year1_net_benefit", "break_even_months", "eligible_share"]}
    per_day = len(contacts) / max(days_observed, 1)
    # Use a validated business volume when supplied; otherwise annualize the synthetic sample.
    annual_total = float(annual_contact_volume) if annual_contact_volume is not None else per_day * 365
    in_scope = contacts[contacts["intent"].isin(target_intents)]
    eligible_share = len(in_scope) / len(contacts)
    annual_in_scope = annual_total * eligible_share
    contained = annual_in_scope * max(0, min(containment_rate, 1))
    aht = float(in_scope["handle_time_minutes"].mean()) if len(in_scope) else float(contacts["handle_time_minutes"].mean())
    gross_savings = contained * (aht / 60.0) * loaded_hourly_cost
    variable_cost = annual_in_scope * ai_cost_per_interaction
    steady_net = gross_savings - variable_cost - annual_platform_cost
    year1_net = steady_net - one_time_build_cost
    monthly_net = steady_net / 12
    break_even_months = (one_time_build_cost / monthly_net) if monthly_net > 0 else None
    return {
        "annual_total_contacts": float(annual_total),
        "annual_in_scope_contacts": float(annual_in_scope),
        "annual_contained_contacts": float(contained),
        "eligible_share": float(eligible_share),
        "aht_minutes": float(aht),
        "gross_labor_savings": float(gross_savings),
        "ai_variable_cost": float(variable_cost),
        "annual_platform_cost": float(annual_platform_cost),
        "one_time_build_cost": float(one_time_build_cost),
        "steady_state_net_benefit": float(steady_net),
        "year1_net_benefit": float(year1_net),
        "break_even_months": float(break_even_months) if break_even_months is not None else None,
        "implementation_months": int(implementation_months),
    }


def scenarios(contacts: pd.DataFrame, annual_contact_volume: float = 250000, target_intents: list[str] | None = None) -> pd.DataFrame:
    definitions = [
        ("Conservative", 0.15, 28.0, 0.16, 75000.0, 100000.0),
        ("Base case", 0.30, 34.0, 0.10, 50000.0, 80000.0),
        ("Upside", 0.42, 38.0, 0.07, 45000.0, 70000.0),
    ]
    rows = []
    for name, contain, labor_cost, ai_cost, platform, build in definitions:
        result = calculate_business_case(
            contacts, containment_rate=contain, loaded_hourly_cost=labor_cost,
            ai_cost_per_interaction=ai_cost, annual_platform_cost=platform, one_time_build_cost=build,
            annual_contact_volume=annual_contact_volume, target_intents=target_intents,
        )
        rows.append({"Scenario": name, "Containment rate": contain, "Annual in-scope contacts": result["annual_in_scope_contacts"],
                     "Gross labor savings": result["gross_labor_savings"], "Annual AI + platform cost": result["ai_variable_cost"] + result["annual_platform_cost"],
                     "Steady-state net benefit": result["steady_state_net_benefit"], "Year 1 net benefit": result["year1_net_benefit"]})
    return pd.DataFrame(rows)
