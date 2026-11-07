"""
Direct API Test Suite for PredixAI.
Executes business logic and endpoints without anyio/lifespan threading locks.
"""

import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.connection import SessionLocal
from app.main import seed_initial_fleet
from app.api import machines, predictions, alerts, maintenance, analytics, assistant
from app.models.domain import SensorReadingInput, MachineCreate, AssistantQuery

# Ensure initial fleet is seeded
seed_initial_fleet()

db = SessionLocal()

print("[TEST 1] Testing get_all_machines()...")
mach_list = machines.get_all_machines(db=db)
print(f"  -> Returned {len(mach_list)} machines.")
assert len(mach_list) >= 6

print("[TEST 2] Testing get_machine_details()...")
details = machines.get_machine_details('ENG-001', db=db)
m_id = details['machine']['machine_id']
m_h = details['machine']['health_score']
print(f"  -> Machine {m_id} health: {m_h}%")
assert m_id == 'ENG-001'

print("[TEST 3] Testing predict_full_pipeline()...")
input_data = SensorReadingInput(
    machine_id='ENG-001',
    cycle=126,
    s2=642.5, s3=1590.1, s4=1405.0, s7=553.5, s8=2388.07, s9=9048.2, s11=47.52, s12=521.7,
    s13=2388.04, s14=8137.0, s15=8.42, s17=392.0, s20=39.0, s21=23.4
)
pred_res = predictions.predict_full_pipeline(input_data, db=db)
print(f"  -> Pred RUL: {pred_res['predicted_rul']} | Fail Prob: {pred_res['failure_probability']} | Risk: {pred_res['risk_level']}")
print(f"  -> Top SHAP factors: {len(pred_res['shap_factors'])}")
assert 'predicted_rul' in pred_res
assert 'failure_probability' in pred_res

print("[TEST 4] Testing get_alerts()...")
alert_list = alerts.get_alerts(db=db)
print(f"  -> Retrieved {len(alert_list)} alerts.")
assert len(alert_list) >= 2

print("[TEST 5] Testing get_fleet_analytics()...")
ana_res = analytics.get_fleet_analytics(db=db)
kpis = ana_res['kpis']
print(f"  -> KPIs: Total={kpis['total_machines']}, Fleet Avg Health={kpis['fleet_health_score']}%")
assert kpis['total_machines'] >= 6

print("[TEST 6] Testing ask_assistant()...")
chat_res = assistant.ask_assistant(AssistantQuery(machine_id='ENG-003', query='Diagnose ENG-003'), db=db)
print(f"  -> Assistant Diagnostic: {chat_res.response[:120]}...")
assert "ENG-003" in chat_res.response

print("\n" + "=" * 60)
print("ALL 6 DIRECT API INTEGRATION TESTS PASSED SUCCESSFULLY!")
print("=" * 60)
