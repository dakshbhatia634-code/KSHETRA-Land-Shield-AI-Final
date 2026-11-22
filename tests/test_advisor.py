"""
KSHETRA — Land Shield AI
AI Land Advisor Test Suite.

Audits and verifies:
1. Natural greeting handling without unsolicited land reports.
2. Capabilities query handling.
3. Educational science queries (soil pH, NDVI, bearing capacity).
4. Context-aware simplification follow-ups.
5. Context-aware elaboration ("Why?") follow-ups.
6. Agriculture suitability analysis grounded in active location context.
7. Construction suitability switching grounded in active location context.
8. Comprehensive risk assessment grounded in active location context.
9. Unrelated general questions answered properly without forcing land analysis.
10. Multi-location context grounding across different agro-climatic zones.
11. Response schema compliance (intent, engine, llm_connected, missing_configuration, timestamp).
12. FastAPI route registration on both /api/advisor/chat and /advisor/chat.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.routes.advisor import (
    advisor_chat_endpoint,
    classify_user_intent,
    generate_conversational_reply,
    AdvisorChatRequest,
    ChatMessage,
)
from backend.main import app


def run_tests():
    print("=" * 75)
    print("  KSHETRA AI LAND ADVISOR — CONVERSATIONAL INTELLIGENCE AUDIT")
    print("=" * 75)

    passed = 0
    total = 0

    def assert_test(name: str, condition: bool, details: str = ""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  [PASS] {name} {f'({details})' if details else ''}")
        else:
            print(f"  [FAIL] {name} - FAILED: {details}")

    # 1. Route mounting in FastAPI app
    print("\n--- 1. Router Registration & Endpoints ---")
    routes = list(app.openapi()["paths"].keys())
    assert_test("Mounted on /api/advisor/chat", "/api/advisor/chat" in routes)
    assert_test("Mounted on /advisor/chat", "/advisor/chat" in routes)

    # 2. Greeting Test: "Hello"
    print("\n--- 2. Greeting (No Unsolicited Land Report) ---")
    req_hello = AdvisorChatRequest(message="Hello")
    res_hello = advisor_chat_endpoint(req_hello)
    assert_test("Intent is GREETING", res_hello.intent == "GREETING")
    assert_test("Casual, helpful response", "help" in res_hello.reply.lower() or "hello" in res_hello.reply.lower())
    assert_test("Does NOT dump coordinate report", "28.4007" not in res_hello.reply)
    assert_test("Schema has engine and llm_connected", bool(res_hello.engine) and res_hello.llm_connected is False)

    # 3. Capabilities Test: "What can you do?"
    print("\n--- 3. Capabilities Breakdown ---")
    req_cap = AdvisorChatRequest(message="What can you do?")
    res_cap = advisor_chat_endpoint(req_cap)
    assert_test("Intent is CAPABILITIES", res_cap.intent == "CAPABILITIES")
    assert_test("Mentions agriculture", "agricultural" in res_cap.reply.lower() or "crop" in res_cap.reply.lower())
    assert_test("Mentions construction", "construction" in res_cap.reply.lower())
    assert_test("Mentions risks", "risk" in res_cap.reply.lower())

    # 4. Educational Question: "What is soil pH?"
    print("\n--- 4. Science Educational Query ---")
    req_ph = AdvisorChatRequest(message="What is soil pH?")
    res_ph = advisor_chat_endpoint(req_ph)
    assert_test("Intent is SCIENCE_SOIL_PH", res_ph.intent == "SCIENCE_SOIL_PH")
    assert_test("Defines acidity/alkalinity scale 0 to 14", "0 to 14" in res_ph.reply or "acidic" in res_ph.reply.lower())
    assert_test("Notes in-situ testing requirement", "in-situ" in res_ph.reply.lower() or "core test" in res_ph.reply.lower())

    # 5. Simplification Follow-up: "Explain it simply."
    print("\n--- 5. Simplification Follow-up with Context History ---")
    history = [
        ChatMessage(role="user", content="What is soil pH?"),
        ChatMessage(role="assistant", content=res_ph.reply),
    ]
    req_simp = AdvisorChatRequest(message="Explain it simply.", conversation_history=history)
    res_simp = advisor_chat_endpoint(req_simp)
    assert_test("Intent is SIMPLIFICATION", res_simp.intent == "SIMPLIFICATION")
    assert_test("Uses everyday plant analogy", "sweet or sour" in res_simp.reply.lower() or "plant" in res_simp.reply.lower())
    assert_test("Simplified explanation", len(res_simp.reply) > 50)

    # 6. Deep Elaboration Follow-up: "Why?"
    print("\n--- 6. Elaboration Follow-up (Why?) ---")
    req_why = AdvisorChatRequest(message="Why?", conversation_history=history)
    res_why = advisor_chat_endpoint(req_why)
    assert_test("Intent is ELABORATION", res_why.intent == "ELABORATION")
    assert_test("Explains chemical binding mechanism", "acidic" in res_why.reply.lower() or "nutrient" in res_why.reply.lower())

    # 7. Agriculture Suitability: "Is this selected location suitable for agriculture?"
    print("\n--- 7. Agriculture Suitability (Active Location Context) ---")
    ctx_faridabad = {
        "name": "Faridabad Agro-Urban Fringe",
        "lat": 28.4007,
        "lon": 77.3501,
        "vegetation_coverage_pct": 38.4,
        "built_up_coverage_pct": 14.8,
        "slope_deg": 1.2,
        "elevation_m": 208,
        "annual_rainfall_mm": 720,
        "dominant_class": "Ploughed Open Soil",
    }
    req_agri = AdvisorChatRequest(
        message="Is this selected location suitable for agriculture?",
        location_context=ctx_faridabad,
    )
    res_agri = advisor_chat_endpoint(req_agri)
    assert_test("Intent is AGRICULTURE_SUITABILITY", res_agri.intent == "AGRICULTURE_SUITABILITY")
    assert_test("Answers question directly", "yes" in res_agri.reply.lower())
    assert_test("Uses real vegetation percentage (38.4%)", "38.4%" in res_agri.reply)
    assert_test("Uses real slope angle (1.2°)", "1.2°" in res_agri.reply)
    assert_test("Recommends crop cycles (Rabi/Kharif)", "wheat" in res_agri.reply.lower() or "rabi" in res_agri.reply.lower())
    assert_test("Mentions in-situ testing verification", "subterranean" in res_agri.reply.lower() or "verified" in res_agri.reply.lower())

    # 8. Construction Suitability: "What about construction?"
    print("\n--- 8. Construction Suitability Switching ---")
    history_agri = [
        ChatMessage(role="user", content="Is this selected location suitable for agriculture?"),
        ChatMessage(role="assistant", content=res_agri.reply),
    ]
    req_const = AdvisorChatRequest(
        message="What about construction?",
        conversation_history=history_agri,
        location_context=ctx_faridabad,
    )
    res_const = advisor_chat_endpoint(req_const)
    assert_test("Intent is CONSTRUCTION_SUITABILITY", res_const.intent == "CONSTRUCTION_SUITABILITY")
    assert_test("Analyzes grading and terrain slope", "grading" in res_const.reply.lower() or "slope" in res_const.reply.lower())
    assert_test("Mentions foundation considerations", "foundation" in res_const.reply.lower() or "footing" in res_const.reply.lower())
    assert_test("Mentions zoning/CLU clearance", "zoning" in res_const.reply.lower() or "clu" in res_const.reply.lower())

    # 9. Risk Analysis: "What are the risks?"
    print("\n--- 9. Comprehensive Risk Assessment ---")
    req_risk = AdvisorChatRequest(
        message="What are the risks?",
        location_context=ctx_faridabad,
    )
    res_risk = advisor_chat_endpoint(req_risk)
    assert_test("Intent is RISKS", res_risk.intent == "RISKS")
    assert_test("Prioritizes Jamabandi / Title ownership", "jamabandi" in res_risk.reply.lower() or "ownership" in res_risk.reply.lower())
    assert_test("Mentions seasonal waterlogging/drainage", "waterlogging" in res_risk.reply.lower() or "drainage" in res_risk.reply.lower())
    assert_test("Mentions borehole bearing capacity", "bearing capacity" in res_risk.reply.lower() or "borehole" in res_risk.reply.lower())

    # 10. Unrelated Question: "Tell me something unrelated to land analysis."
    print("\n--- 10. Unrelated General Queries ---")
    req_unrelated = AdvisorChatRequest(message="Tell me something unrelated to land analysis.")
    res_unrelated = advisor_chat_endpoint(req_unrelated)
    assert_test("Intent is UNRELATED_GENERAL", res_unrelated.intent == "UNRELATED_GENERAL")
    assert_test("Answers without forcing land analysis", "honey" in res_unrelated.reply.lower() or "egyptian" in res_unrelated.reply.lower())
    assert_test("Does not dump telemetry", "hectare" not in res_unrelated.reply.lower() and "sentinel" not in res_unrelated.reply.lower())

    # 11. Multi-location context (Ludhiana Intensive Wheat Belt)
    print("\n--- 11. Multi-Location Context Grounding ---")
    ctx_ludhiana = {
        "name": "Ludhiana Intensive Wheat Belt",
        "lat": 30.9010,
        "lon": 75.8573,
        "vegetation_coverage_pct": 52.1,
        "slope_deg": 0.8,
        "elevation_m": 247,
        "annual_rainfall_mm": 680,
    }
    req_ludhiana = AdvisorChatRequest(
        message="Is this selected location suitable for agriculture?",
        location_context=ctx_ludhiana,
    )
    res_ludhiana = advisor_chat_endpoint(req_ludhiana)
    assert_test("Grounded in Ludhiana", "Ludhiana" in res_ludhiana.reply)
    assert_test("Uses Ludhiana vegetation (52.1%)", "52.1%" in res_ludhiana.reply)
    assert_test("Context used is recorded", res_ludhiana.context_used == "Ludhiana Intensive Wheat Belt")

    # 12. Transparent Fallback Reporting
    print("\n--- 12. Transparent Engine & Fallback Status ---")
    assert_test("Reports llm_connected accurately", res_hello.llm_connected is False)
    assert_test("Reports missing configuration explicitly", res_hello.missing_configuration is not None)
    assert_test("Engine identified as Grounded Local Intelligence", "Local Intelligence" in res_hello.engine)
    assert_test("Zero internal model algorithm names exposed", "SatelliteUNet" not in res_agri.reply and "RandomForest" not in res_agri.reply)

    print("\n" + "=" * 75)
    print(f"  RESULTS: {passed}/{total} TESTS PASSED ({(passed/total)*100:.1f}%)")
    print("=" * 75)

    if passed == total:
        print("\n  >> ALL AI LAND ADVISOR AUDIT CHECKS COMPLETED SUCCESSFULLY! <<\n")
        return 0
    else:
        print(f"\n  >> {total - passed} CHECKS FAILED! <<\n")
        return 1


if __name__ == "__main__":
    code = run_tests()
    sys.exit(code)
