from __future__ import annotations

import os
from pathlib import Path

import requests

BASE_URL = os.getenv("BACKEND_URL", "http://backend:8000/api").rstrip("/")


def get_clients() -> list[dict]:
    response = requests.get(f"{BASE_URL}/clients", timeout=30)
    response.raise_for_status()
    return response.json()


def generate_report(client_id: str, thread_id: str) -> dict:
    response = requests.post(
        f"{BASE_URL}/reports/generate",
        json={
            "client_id": client_id,
            "thread_id": thread_id,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def approve_report(
    thread_id: str,
    approved: bool,
    approval_notes: str | None,
    approver_name: str | None,
) -> dict:
    response = requests.post(
        f"{BASE_URL}/reports/approve",
        json={
            "thread_id": thread_id,
            "approved": approved,
            "approval_notes": approval_notes,
            "approver_name": approver_name,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def download_pdf(pdf_path: str) -> bytes:
    response = requests.get(
        f"{BASE_URL}/reports/file",
        params={"path": pdf_path},
        timeout=120,
    )
    response.raise_for_status()
    return response.content


def deliver_report(
    thread_id: str,
    channel: str | None,
    requested_by: str | None,
) -> dict:
    response = requests.post(
        f"{BASE_URL}/reports/deliver",
        json={
            "thread_id": thread_id,
            "channel": channel,
            "requested_by": requested_by,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()