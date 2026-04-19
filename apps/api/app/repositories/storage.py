import json
from typing import Any

from app.core.db import get_connection
from app.schemas.brief import Alert, BriefCounts, Delta, TraceStep
from app.schemas.common import Cohort, KeyExec
from app.schemas.watchlist import Company


class StorageRepository:
    def upsert_company(self, company: Company, updated_at: str) -> None:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO companies (id, name, domain, headcount, last_funding, key_execs_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    domain = excluded.domain,
                    headcount = excluded.headcount,
                    last_funding = excluded.last_funding,
                    key_execs_json = excluded.key_execs_json,
                    updated_at = excluded.updated_at
                """,
                (
                    company.id,
                    company.name,
                    company.domain,
                    company.headcount,
                    company.last_funding,
                    json.dumps([exec.model_dump() for exec in company.key_execs]),
                    updated_at,
                ),
            )

    def add_watchlist_entry(self, company_id: int, cohort: Cohort, added_at: str) -> None:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO watchlist_entries (company_id, cohort, added_at)
                VALUES (?, ?, ?)
                ON CONFLICT(company_id) DO UPDATE SET
                    cohort = excluded.cohort,
                    added_at = excluded.added_at
                """,
                (company_id, cohort, added_at),
            )

    def delete_watchlist_entry(self, company_id: int) -> bool:
        with get_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM watchlist_entries WHERE company_id = ?",
                (company_id,),
            )
            return cursor.rowcount > 0

    def watchlist_entry_exists(self, company_id: int) -> bool:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM watchlist_entries WHERE company_id = ?",
                (company_id,),
            ).fetchone()
            return row is not None

    def count_watchlist_entries(self) -> int:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM watchlist_entries"
            ).fetchone()
            return int(row["count"])

    def list_watchlist(self, cohort: Cohort | None = None) -> list[Company]:
        query = """
            SELECT c.id, c.name, c.domain, c.headcount, c.last_funding, c.key_execs_json,
                   w.cohort, w.added_at
            FROM watchlist_entries w
            INNER JOIN companies c ON c.id = w.company_id
        """
        params: list[Any] = []
        if cohort is not None:
            query += " WHERE w.cohort = ?"
            params.append(cohort)
        query += " ORDER BY w.added_at DESC"

        with get_connection() as connection:
            rows = connection.execute(query, params).fetchall()
        return [self._company_from_row(row) for row in rows]

    def get_watchlist_company(self, company_id: int) -> Company | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT c.id, c.name, c.domain, c.headcount, c.last_funding, c.key_execs_json,
                       w.cohort, w.added_at
                FROM watchlist_entries w
                INNER JOIN companies c ON c.id = w.company_id
                WHERE w.company_id = ?
                """,
                (company_id,),
            ).fetchone()
        if row is None:
            return None
        return self._company_from_row(row)

    def add_snapshot(self, company_id: int, taken_at: str, payload: dict[str, Any]) -> int:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO snapshots (company_id, taken_at, payload_json)
                VALUES (?, ?, ?)
                """,
                (company_id, taken_at, json.dumps(payload)),
            )
            return int(cursor.lastrowid)

    def count_snapshots(self, company_id: int) -> int:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM snapshots WHERE company_id = ?",
                (company_id,),
            ).fetchone()
            return int(row["count"])

    def get_latest_snapshot(self, company_id: int) -> dict[str, Any] | None:
        return self._get_snapshot(company_id=company_id, offset=0)

    def get_previous_snapshot(self, company_id: int) -> dict[str, Any] | None:
        return self._get_snapshot(company_id=company_id, offset=1)

    def list_alerts(self, company_id: int | None = None) -> list[Alert]:
        query = """
            SELECT id, company_id, company_json, cohort, delta_json, alert_type, severity,
                   explanation, recommended_action, trace_json, detected_at
            FROM alerts
        """
        params: list[Any] = []
        if company_id is not None:
            query += " WHERE company_id = ?"
            params.append(company_id)
        query += " ORDER BY detected_at DESC, id DESC"

        with get_connection() as connection:
            rows = connection.execute(query, params).fetchall()
        return [self._alert_from_row(row) for row in rows]

    def add_alert(self, alert: Alert) -> int:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO alerts (
                    company_id,
                    company_json,
                    cohort,
                    delta_json,
                    alert_type,
                    severity,
                    explanation,
                    recommended_action,
                    trace_json,
                    detected_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    alert.company.id,
                    json.dumps(alert.company.model_dump()),
                    alert.cohort,
                    json.dumps(alert.delta.model_dump()),
                    alert.alert_type,
                    alert.severity,
                    alert.explanation,
                    alert.recommended_action,
                    json.dumps([step.model_dump() for step in alert.trace]),
                    alert.detected_at,
                ),
            )
            return int(cursor.lastrowid)

    def save_brief_run(self, summary: str, generated_at: str, counts: BriefCounts) -> None:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO brief_runs (summary, generated_at, counts_json)
                VALUES (?, ?, ?)
                """,
                (summary, generated_at, json.dumps(counts.model_dump())),
            )

    def get_latest_brief_run(self) -> dict[str, Any] | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT summary, generated_at, counts_json
                FROM brief_runs
                ORDER BY generated_at DESC, id DESC
                LIMIT 1
                """
            ).fetchone()
        if row is None:
            return None
        return {
            "summary": row["summary"],
            "generated_at": row["generated_at"],
            "counts": BriefCounts(**json.loads(row["counts_json"])),
        }

    def _get_snapshot(self, company_id: int, offset: int) -> dict[str, Any] | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, company_id, taken_at, payload_json
                FROM snapshots
                WHERE company_id = ?
                ORDER BY taken_at DESC, id DESC
                LIMIT 1 OFFSET ?
                """,
                (company_id, offset),
            ).fetchone()
        if row is None:
            return None
        return {
            "id": row["id"],
            "company_id": row["company_id"],
            "taken_at": row["taken_at"],
            "payload": json.loads(row["payload_json"]),
        }

    def _company_from_row(self, row: Any) -> Company:
        return Company(
            id=row["id"],
            name=row["name"],
            domain=row["domain"],
            cohort=row["cohort"],
            headcount=row["headcount"],
            last_funding=row["last_funding"],
            key_execs=[KeyExec(**item) for item in json.loads(row["key_execs_json"])],
            added_at=row["added_at"],
        )

    def _alert_from_row(self, row: Any) -> Alert:
        return Alert(
            id=row["id"],
            company=Company(**json.loads(row["company_json"])),
            cohort=row["cohort"],
            delta=Delta(**json.loads(row["delta_json"])),
            alert_type=row["alert_type"],
            severity=row["severity"],
            explanation=row["explanation"],
            recommended_action=row["recommended_action"],
            trace=[TraceStep(**item) for item in json.loads(row["trace_json"])],
            detected_at=row["detected_at"],
        )


storage_repository = StorageRepository()
