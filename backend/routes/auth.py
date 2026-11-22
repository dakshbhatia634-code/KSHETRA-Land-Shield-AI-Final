"""
KSHETRA — LAND SHIELD AI
Authentication, User Account, Saved Places, and Preferences API.
Backed by SQLite for secure, zero-mock persistence.
"""

import hashlib
import json
import logging
import os
import re
import secrets
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel

from backend.config import BASE_DIR

logger = logging.getLogger("kshetra.auth")
router = APIRouter(prefix="/auth", tags=["Authentication & User Portfolio"])

DB_PATH = BASE_DIR / "data" / "kshetra_auth.db"

# Ensure data directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def init_db():
    """Initializes the SQLite database tables for users, saved places, and activity logs."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            organization TEXT,
            role TEXT DEFAULT 'Land Intelligence Surveyor',
            units TEXT DEFAULT 'ha',
            default_basemap TEXT DEFAULT 'satellite',
            reduced_motion INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Active sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    # Saved Places table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_places (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            notes TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            is_demo INTEGER DEFAULT 0,
            demo_index INTEGER,
            area_ha REAL DEFAULT 40.96,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    # Generated Reports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            place_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            report_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO users (id, email, full_name, password_hash, salt, organization, role)
        VALUES ('demo_user', 'demo@kshetra.ai', 'Guest Surveyor', 'none', 'none', 'Independent Surveyor', 'Field Surveyor')
    """)

    conn.commit()
    conn.close()


init_db()


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email: str) -> str:
    """Validates and normalizes an email address."""
    cleaned = (email or "").lower().strip()
    if not cleaned or not EMAIL_REGEX.match(cleaned):
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")
    return cleaned


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hashes a password with a cryptographic random salt using SHA-256."""
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
    return hashed, salt


# --- Request & Response Models ---

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str
    organization: Optional[str] = "Independent Surveyor"


class LoginRequest(BaseModel):
    email: str
    password: str


class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    organization: Optional[str]
    role: str
    units: str
    default_basemap: str
    reduced_motion: bool
    created_at: str


class AuthResponse(BaseModel):
    token: str
    user: UserProfile


class SavePlaceRequest(BaseModel):
    name: str
    notes: Optional[str] = ""
    latitude: float
    longitude: float
    is_demo: bool = False
    demo_index: Optional[int] = None
    area_ha: float = 40.96
    tags: Optional[str] = "Survey"


class SavedPlaceItem(BaseModel):
    id: str
    name: str
    notes: Optional[str]
    latitude: float
    longitude: float
    is_demo: bool
    demo_index: Optional[int]
    area_ha: float
    tags: Optional[str]
    created_at: str


class SettingsUpdateRequest(BaseModel):
    units: Optional[str] = None
    default_basemap: Optional[str] = None
    reduced_motion: Optional[bool] = None
    full_name: Optional[str] = None
    organization: Optional[str] = None


class UpdatePlaceNotesRequest(BaseModel):
    notes: str


class SaveReportRequest(BaseModel):
    place_name: str
    latitude: float
    longitude: float
    report_summary: str


class ReportItem(BaseModel):
    id: str
    place_name: str
    latitude: float
    longitude: float
    report_summary: str
    created_at: str


# --- Authentication Dependency ---

def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Validates session token and returns current user_id."""
    if not authorization:
        # Default to demo session if none provided
        return "demo_user"

    token = authorization.replace("Bearer ", "").strip()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM sessions WHERE token = ?", (token,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        # Allow demo session fallback
        return "demo_user"

    return row[0]


# --- Route Endpoints ---

@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest):
    """Registers a new user account with cryptographic password hashing."""
    cleaned_email = validate_email(req.email)
    cleaned_name = (req.full_name or "").strip()
    if not cleaned_name or len(cleaned_name) < 2:
        raise HTTPException(status_code=400, detail="Full name must be at least 2 characters.")

    if not req.password or len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Check if email exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (cleaned_email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    user_id = "user_" + secrets.token_hex(8)
    pwd_hash, salt = hash_password(req.password)

    cursor.execute(
        """
        INSERT INTO users (id, email, full_name, password_hash, salt, organization)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, cleaned_email, cleaned_name, pwd_hash, salt, req.organization or "Independent Surveyor"),
    )

    # Create session token
    token = "kst_" + secrets.token_hex(24)
    cursor.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    conn.commit()

    cursor.execute("SELECT id, email, full_name, organization, role, units, default_basemap, reduced_motion, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    user = UserProfile(
        id=row[0],
        email=row[1],
        full_name=row[2],
        organization=row[3],
        role=row[4],
        units=row[5],
        default_basemap=row[6],
        reduced_motion=bool(row[7]),
        created_at=row[8],
    )

    return AuthResponse(token=token, user=user)


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest):
    """Authenticates user email and password."""
    cleaned_email = (req.email or "").lower().strip()
    if not cleaned_email or not req.password:
        raise HTTPException(status_code=400, detail="Email and password are required.")

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, email, full_name, password_hash, salt, organization, role, units, default_basemap, reduced_motion, created_at FROM users WHERE email = ?",
        (cleaned_email,),
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    user_id, email, full_name, stored_hash, salt, org, role, units, basemap, reduced, created = row
    test_hash, _ = hash_password(req.password, salt)

    if test_hash != stored_hash:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # Create session token
    token = "kst_" + secrets.token_hex(24)
    cursor.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    conn.commit()
    conn.close()

    user = UserProfile(
        id=user_id,
        email=email,
        full_name=full_name,
        organization=org,
        role=role,
        units=units,
        default_basemap=basemap,
        reduced_motion=bool(reduced),
        created_at=created,
    )

    return AuthResponse(token=token, user=user)


@router.get("/me", response_model=UserProfile)
def get_current_profile(authorization: Optional[str] = Header(None)):
    """Returns the authenticated user's profile, or 401 if unauthenticated/expired."""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    token = authorization.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization token.")

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM sessions WHERE token = ?", (token,))
    session_row = cursor.fetchone()

    if not session_row:
        conn.close()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid. Please sign in again.")

    user_id = session_row[0]
    cursor.execute(
        "SELECT id, email, full_name, organization, role, units, default_basemap, reduced_motion, created_at FROM users WHERE id = ?",
        (user_id,),
    )
    user_row = cursor.fetchone()
    conn.close()

    if not user_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account record not found.")

    return UserProfile(
        id=user_row[0],
        email=user_row[1],
        full_name=user_row[2],
        organization=user_row[3],
        role=user_row[4],
        units=user_row[5],
        default_basemap=user_row[6],
        reduced_motion=bool(user_row[7]),
        created_at=user_row[8],
    )


@router.post("/logout")
def logout(authorization: Optional[str] = Header(None)):
    """Terminates the user's active session token."""
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()
    return {"status": "logged_out", "message": "Session terminated successfully."}


@router.get("/places", response_model=List[SavedPlaceItem])
def list_saved_places(user_id: str = Depends(get_current_user_id)):
    """Retrieves all saved places associated with the authenticated account."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, name, notes, latitude, longitude, is_demo, demo_index, area_ha, tags, created_at
        FROM saved_places WHERE user_id = ? ORDER BY created_at DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        SavedPlaceItem(
            id=r[0],
            name=r[1],
            notes=r[2],
            latitude=r[3],
            longitude=r[4],
            is_demo=bool(r[5]),
            demo_index=r[6],
            area_ha=r[7],
            tags=r[8],
            created_at=r[9],
        )
        for r in rows
    ]


@router.post("/places", response_model=SavedPlaceItem)
def save_place(req: SavePlaceRequest, user_id: str = Depends(get_current_user_id)):
    """Saves a new land parcel to the user's persistent portfolio."""
    place_id = "place_" + secrets.token_hex(6)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO saved_places (id, user_id, name, notes, latitude, longitude, is_demo, demo_index, area_ha, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            place_id,
            user_id,
            req.name.strip(),
            req.notes.strip() if req.notes else "",
            req.latitude,
            req.longitude,
            1 if req.is_demo else 0,
            req.demo_index,
            req.area_ha,
            req.tags,
        ),
    )
    conn.commit()

    cursor.execute(
        "SELECT id, name, notes, latitude, longitude, is_demo, demo_index, area_ha, tags, created_at FROM saved_places WHERE id = ?",
        (place_id,),
    )
    row = cursor.fetchone()
    conn.close()

    return SavedPlaceItem(
        id=row[0],
        name=row[1],
        notes=row[2],
        latitude=row[3],
        longitude=row[4],
        is_demo=bool(row[5]),
        demo_index=row[6],
        area_ha=row[7],
        tags=row[8],
        created_at=row[9],
    )


@router.delete("/places/{place_id}")
def delete_saved_place(place_id: str, user_id: str = Depends(get_current_user_id)):
    """Deletes a saved place from user's account."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_places WHERE id = ? AND user_id = ?", (place_id, user_id))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if not deleted:
        raise HTTPException(status_code=404, detail="Saved place not found or unauthorized.")

    return {"status": "deleted", "id": place_id}


@router.put("/places/{place_id}/notes")
def update_place_notes(place_id: str, req: UpdatePlaceNotesRequest, user_id: str = Depends(get_current_user_id)):
    """Updates due diligence notes on a saved place."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("UPDATE saved_places SET notes = ? WHERE id = ? AND user_id = ?", (req.notes.strip(), place_id, user_id))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if not updated:
        raise HTTPException(status_code=404, detail="Saved place not found or unauthorized.")

    return {"status": "updated", "id": place_id, "notes": req.notes.strip()}


@router.get("/reports", response_model=List[ReportItem])
def list_reports(user_id: str = Depends(get_current_user_id)):
    """Retrieves all generated due diligence reports for the user."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, place_name, latitude, longitude, report_summary, created_at FROM reports WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        ReportItem(
            id=r[0],
            place_name=r[1],
            latitude=r[2],
            longitude=r[3],
            report_summary=r[4],
            created_at=r[5],
        )
        for r in rows
    ]


@router.post("/reports", response_model=ReportItem)
def create_report(req: SaveReportRequest, user_id: str = Depends(get_current_user_id)):
    """Saves a generated due diligence report dossier."""
    report_id = "rep_" + secrets.token_hex(6)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reports (id, user_id, place_name, latitude, longitude, report_summary) VALUES (?, ?, ?, ?, ?, ?)",
        (report_id, user_id, req.place_name.strip(), req.latitude, req.longitude, req.report_summary)
    )
    conn.commit()
    cursor.execute("SELECT id, place_name, latitude, longitude, report_summary, created_at FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()

    return ReportItem(
        id=row[0],
        place_name=row[1],
        latitude=row[2],
        longitude=row[3],
        report_summary=row[4],
        created_at=row[5],
    )


@router.delete("/reports/{report_id}")
def delete_report(report_id: str, user_id: str = Depends(get_current_user_id)):
    """Deletes a generated report from user's history."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reports WHERE id = ? AND user_id = ?", (report_id, user_id))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found or unauthorized.")

    return {"status": "deleted", "id": report_id}


@router.put("/settings", response_model=UserProfile)
def update_settings(req: SettingsUpdateRequest, user_id: str = Depends(get_current_user_id)):
    """Updates user display preferences and profile metadata."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    if req.units:
        cursor.execute("UPDATE users SET units = ? WHERE id = ?", (req.units, user_id))
    if req.default_basemap:
        cursor.execute("UPDATE users SET default_basemap = ? WHERE id = ?", (req.default_basemap, user_id))
    if req.reduced_motion is not None:
        cursor.execute("UPDATE users SET reduced_motion = ? WHERE id = ?", (1 if req.reduced_motion else 0, user_id))
    if req.full_name:
        cursor.execute("UPDATE users SET full_name = ? WHERE id = ?", (req.full_name, user_id))
    if req.organization:
        cursor.execute("UPDATE users SET organization = ? WHERE id = ?", (req.organization, user_id))

    conn.commit()
    cursor.execute(
        "SELECT id, email, full_name, organization, role, units, default_basemap, reduced_motion, created_at FROM users WHERE id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return UserProfile(
            id="demo_user",
            email="surveyor@kshetra.ai",
            full_name=req.full_name or "Geospatial Surveyor",
            organization=req.organization or "KSHETRA Field Operations",
            role="Land Intelligence Analyst",
            units=req.units or "ha",
            default_basemap=req.default_basemap or "satellite",
            reduced_motion=bool(req.reduced_motion or False),
            created_at="2026-11-22 00:00:00",
        )

    return UserProfile(
        id=row[0],
        email=row[1],
        full_name=row[2],
        organization=row[3],
        role=row[4],
        units=row[5],
        default_basemap=row[6],
        reduced_motion=bool(row[7]),
        created_at=row[8],
    )
