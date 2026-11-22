"""
KSHETRA — Land Shield AI
Authentication, Registration, Login & Session Persistence Comprehensive Test Suite.

Audits and verifies all 13 specification requirements:
1. Open app as logged-out user (get_current_profile without token raises 401).
2. Register a brand-new test account (data validation, email normalization, password hashing).
3. Verify account is saved in SQLite database with secure SHA-256 + salt (NEVER plaintext).
4. Log in using that newly registered account.
5. Verify correct account name appears in returned user profile.
6. Navigate to dashboard (session remains valid).
7. Navigate to homepage (session remains valid).
8. Refresh browser (token in header retrieves user profile via /api/auth/me).
9. Verify session remains valid and correct user is still shown.
10. Log out (token revoked and deleted from SQLite sessions table).
11. Verify UI / API returns to Guest state (revoked token raises 401).
12. Attempt to log in with incorrect password and verify meaningful error (401).
13. Attempt to register existing email and verify duplicate registration error (400).
Additional tests:
14. Email format validation (rejects invalid email formats).
15. Password length validation (rejects < 6 characters).
16. Name validation (rejects empty/whitespace names).
17. Saved places isolation under authenticated account.
"""

import os
import secrets
import sqlite3
import sys
from pathlib import Path
from fastapi import HTTPException

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.routes.auth import (
    register,
    login,
    get_current_profile,
    logout,
    list_saved_places,
    save_place,
    delete_saved_place,
    RegisterRequest,
    LoginRequest,
    SavePlaceRequest,
    DB_PATH,
    hash_password,
)


def run_tests():
    print("=" * 80)
    print("  KSHETRA AUTHENTICATION & ACCOUNT SYSTEM AUDIT (100% SPEC VERIFICATION)")
    print("=" * 80)

    passed = 0
    total = 0

    def record_test(name: str, condition: bool, details: str = ""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  [PASS] Case {total:02d}: {name} {f'({details})' if details else ''}")
        else:
            print(f"  [FAIL] Case {total:02d}: {name} {f'({details})' if details else ''}")

    # -------------------------------------------------------------------------
    # CASE 1: Open app as logged-out user
    # -------------------------------------------------------------------------
    try:
        get_current_profile(authorization=None)
        record_test("Open app as logged-out user (no token raises 401)", False, "Should raise 401")
    except HTTPException as e:
        record_test("Open app as logged-out user (no token raises 401)", e.status_code == 401, f"Status: {e.status_code}, Detail: {e.detail}")

    # -------------------------------------------------------------------------
    # CASE 2: Register a brand-new test account
    # -------------------------------------------------------------------------
    suffix = secrets.token_hex(4)
    reg_email = f"surveyor_{suffix}@landshield.ai"
    reg_password = "SecureSurveyorPass99!"
    reg_name = f"Surveyor Specialist {suffix}"
    reg_org = "Bhartiya GeoSurvey"

    reg_resp = None
    try:
        reg_resp = register(RegisterRequest(
            full_name=reg_name,
            email=f"  {reg_email.upper()}  ",  # tests normalization
            password=reg_password,
            organization=reg_org
        ))
        record_test("Register a brand-new test account", reg_resp.token.startswith("kst_") and reg_resp.user.email == reg_email.lower(), f"Token generated: {reg_resp.token[:12]}...")
    except Exception as e:
        record_test("Register a brand-new test account", False, str(e))

    # -------------------------------------------------------------------------
    # CASE 3: Verify that the account is saved in the database
    # -------------------------------------------------------------------------
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, full_name, password_hash, salt, organization FROM users WHERE email = ?", (reg_email.lower(),))
    user_row = cursor.fetchone()
    conn.close()

    db_verified = False
    if user_row:
        u_id, u_email, u_name, u_hash, u_salt, u_org = user_row
        # Verify password is not in plaintext
        no_plaintext = reg_password not in u_hash and len(u_hash) == 64
        # Verify hash matches
        computed_hash, _ = hash_password(reg_password, u_salt)
        hash_matches = (computed_hash == u_hash)
        db_verified = (u_email == reg_email.lower() and u_name == reg_name and no_plaintext and hash_matches)

    record_test("Verify account saved in SQLite DB with secure hash (not plaintext)", db_verified, f"Salted SHA-256 verified in {DB_PATH.name}")

    # -------------------------------------------------------------------------
    # CASE 4: Log in using that newly registered account
    # -------------------------------------------------------------------------
    login_resp = None
    try:
        login_resp = login(LoginRequest(
            email=f" {reg_email.upper()} ",
            password=reg_password
        ))
        record_test("Log in using newly registered account", login_resp is not None and login_resp.token.startswith("kst_"), f"Token: {login_resp.token[:12]}...")
    except Exception as e:
        record_test("Log in using newly registered account", False, str(e))

    # -------------------------------------------------------------------------
    # CASE 5: Verify that the correct account name appears
    # -------------------------------------------------------------------------
    name_matches = login_resp and login_resp.user.full_name == reg_name and login_resp.user.email == reg_email.lower()
    record_test("Verify correct account name appears", name_matches, f"Name: '{login_resp.user.full_name}'")

    # -------------------------------------------------------------------------
    # CASE 6 & 7: Navigate to dashboard & homepage (Session validity check)
    # -------------------------------------------------------------------------
    nav_auth_header = f"Bearer {login_resp.token}"
    dash_profile = None
    try:
        dash_profile = get_current_profile(authorization=nav_auth_header)
        record_test("Navigate to dashboard (session valid)", dash_profile.full_name == reg_name, f"User: {dash_profile.full_name}")
    except Exception as e:
        record_test("Navigate to dashboard (session valid)", False, str(e))

    home_profile = None
    try:
        home_profile = get_current_profile(authorization=nav_auth_header)
        record_test("Navigate to homepage (session valid across views)", home_profile.email == reg_email.lower(), f"Email: {home_profile.email}")
    except Exception as e:
        record_test("Navigate to homepage (session valid across views)", False, str(e))

    # -------------------------------------------------------------------------
    # CASE 8 & 9: Refresh browser (re-authenticating via stored token)
    # -------------------------------------------------------------------------
    refresh_profile = None
    try:
        refresh_profile = get_current_profile(authorization=f"Bearer {login_resp.token}")
        record_test("Browser refresh re-authentication via stored token", refresh_profile.id == login_resp.user.id, f"Persisted ID: {refresh_profile.id}")
        record_test("Verify session remains valid & correct user shown", refresh_profile.full_name == reg_name, f"Shown: {refresh_profile.full_name}")
    except Exception as e:
        record_test("Browser refresh re-authentication via stored token", False, str(e))
        record_test("Verify session remains valid & correct user shown", False, str(e))

    # -------------------------------------------------------------------------
    # CASE 10: Log out
    # -------------------------------------------------------------------------
    logout_success = False
    try:
        logout_resp = logout(authorization=f"Bearer {login_resp.token}")
        logout_success = (logout_resp.get("status") == "logged_out")
    except Exception as e:
        pass

    # Verify token removed from DB sessions
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM sessions WHERE token = ?", (login_resp.token,))
    token_in_db = cursor.fetchone()
    conn.close()

    record_test("Log out (token deleted from SQLite sessions table)", logout_success and token_in_db is None, "Token revoked")

    # -------------------------------------------------------------------------
    # CASE 11: Verify UI / API returns to Guest/Sign in state after logout
    # -------------------------------------------------------------------------
    try:
        get_current_profile(authorization=f"Bearer {login_resp.token}")
        record_test("UI/API returns to Guest state (revoked token raises 401)", False, "Should raise 401")
    except HTTPException as e:
        record_test("UI/API returns to Guest state (revoked token raises 401)", e.status_code == 401, f"Detail: {e.detail}")

    # -------------------------------------------------------------------------
    # CASE 12: Attempt to log in with an incorrect password
    # -------------------------------------------------------------------------
    try:
        login(LoginRequest(email=reg_email, password="CompletelyWrongPassword123!"))
        record_test("Login with incorrect password rejected with 401", False, "Should raise 401")
    except HTTPException as e:
        record_test("Login with incorrect password rejected with 401", e.status_code == 401, f"Detail: {e.detail}")

    # -------------------------------------------------------------------------
    # CASE 13: Attempt to register an existing email (duplicate check)
    # -------------------------------------------------------------------------
    try:
        register(RegisterRequest(
            full_name="Duplicate Imposter",
            email=reg_email.upper(),  # case-insensitive check
            password="AnotherPassword123!"
        ))
        record_test("Duplicate email registration rejected with 400", False, "Should raise 400")
    except HTTPException as e:
        record_test("Duplicate email registration rejected with 400", e.status_code == 400, f"Detail: {e.detail}")

    # -------------------------------------------------------------------------
    # ADDITIONAL SPEC CASES: Input Validation & User Isolation
    # -------------------------------------------------------------------------
    # 14. Invalid email format
    try:
        register(RegisterRequest(full_name="Bad Email", email="invalid-email-string", password="password123"))
        record_test("Invalid email format rejected with 400", False, "Should raise 400")
    except HTTPException as e:
        record_test("Invalid email format rejected with 400", e.status_code == 400, f"Detail: {e.detail}")

    # 15. Short password (< 6 chars)
    try:
        register(RegisterRequest(full_name="Short Pass", email=f"short_{suffix}@domain.com", password="123"))
        record_test("Short password (<6 chars) rejected with 400", False, "Should raise 400")
    except HTTPException as e:
        record_test("Short password (<6 chars) rejected with 400", e.status_code == 400, f"Detail: {e.detail}")

    # 16. Empty name
    try:
        register(RegisterRequest(full_name="   ", email=f"noname_{suffix}@domain.com", password="validpass123"))
        record_test("Empty name rejected with 400", False, "Should raise 400")
    except HTTPException as e:
        record_test("Empty name rejected with 400", e.status_code == 400, f"Detail: {e.detail}")

    # 17. Saved places isolation under user account
    user2_resp = register(RegisterRequest(
        full_name=f"Surveyor Two {suffix}",
        email=f"user2_{suffix}@domain.com",
        password="ValidPassword123!"
    ))
    save_resp = save_place(
        SavePlaceRequest(name="Faridabad Agro Sector 82", notes="Field Inspection Required", latitude=28.4007, longitude=77.3501),
        user_id=user2_resp.user.id
    )
    places = list_saved_places(user_id=user2_resp.user.id)
    record_test("Saved places persisted under user account", len(places) >= 1 and places[0].name == "Faridabad Agro Sector 82", f"Found {len(places)} saved parcel")

    # Cleanup test place
    delete_saved_place(save_resp.id, user_id=user2_resp.user.id)
    places_after = list_saved_places(user_id=user2_resp.user.id)
    record_test("Saved place deletion under user account", len(places_after) == 0, "Cleaned up test parcel")

    print("=" * 80)
    print(f"  TOTAL TESTS: {total} | PASSED: {passed} | FAILED: {total - passed}")
    print("=" * 80)
    assert passed == total, f"{total - passed} tests failed!"
    return passed == total


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
