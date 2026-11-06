import os
import sqlite3
from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field

DATABASE_PATH = os.getenv("DATABASE_PATH", "notificaciones.db")
app = FastAPI(title="TurnoFácil Notificaciones API", version="1.0.0")


class NotificationInput(BaseModel):
    reservation_id: int
    email: EmailStr
    message: str = Field(min_length=1, max_length=500)


def connect():
    os.makedirs(os.path.dirname(DATABASE_PATH) or ".", exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reservation_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""")


init_db()


@app.get("/health")
def health():
    return {"status": "ok", "service": "notificaciones"}


@app.post("/internal/notifications", status_code=202)
def receive_notification(payload: NotificationInput):
    with connect() as db:
        cursor = db.execute(
            "INSERT INTO notifications(reservation_id,email,message,created_at) VALUES(?,?,?,?)",
            (payload.reservation_id, str(payload.email), payload.message,
             datetime.now(timezone.utc).isoformat()),
        )
    return {"id": cursor.lastrowid, "status": "accepted"}


@app.get("/notifications")
def list_notifications():
    with connect() as db:
        return [dict(row) for row in db.execute("SELECT * FROM notifications ORDER BY id")]
