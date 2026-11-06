import os
import sqlite3
from datetime import datetime

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

DATABASE_PATH = os.getenv("DATABASE_PATH", "turnos.db")
NOTIFICATIONS_URL = os.getenv("NOTIFICATIONS_URL", "http://localhost:8001")
app = FastAPI(title="TurnoFácil Agenda API", version="1.0.0")


class ReservationInput(BaseModel):
    customer_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    service: str = Field(min_length=2, max_length=100)
    starts_at: datetime


def connect():
    os.makedirs(os.path.dirname(DATABASE_PATH) or ".", exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            service TEXT NOT NULL,
            starts_at TEXT NOT NULL
        )""")


init_db()


@app.get("/health")
def health():
    return {"status": "ok", "service": "agenda"}


@app.post("/reservations", status_code=201)
def create_reservation(payload: ReservationInput):
    with connect() as db:
        cursor = db.execute(
            "INSERT INTO reservations(customer_name,email,service,starts_at) VALUES(?,?,?,?)",
            (payload.customer_name, str(payload.email), payload.service, payload.starts_at.isoformat()),
        )
        reservation = {"id": cursor.lastrowid, **payload.model_dump(mode="json")}
    try:
        response = requests.post(
            f"{NOTIFICATIONS_URL}/internal/notifications",
            json={"reservation_id": reservation["id"], "email": reservation["email"],
                  "message": f"Reserva confirmada: {reservation['service']} el {reservation['starts_at']}"},
            timeout=2,
        )
        response.raise_for_status()
    except requests.RequestException:
        # La reserva persiste aunque el servicio de avisos esté temporalmente caído.
        pass
    return reservation


@app.get("/reservations")
def list_reservations():
    with connect() as db:
        return [dict(row) for row in db.execute("SELECT * FROM reservations ORDER BY id")]


@app.get("/reservations/{reservation_id}")
def get_reservation(reservation_id: int):
    with connect() as db:
        row = db.execute("SELECT * FROM reservations WHERE id=?", (reservation_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return dict(row)
