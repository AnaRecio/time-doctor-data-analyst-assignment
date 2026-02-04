from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import random
import uuid

import numpy as np
import pandas as pd


@dataclass
class Config:
    seed: int = 42

    # Time window for events
    start_date: str = "2025-11-01" 
    days: int = 90

    # Scale
    n_accounts: int = 200 # number of accounts to generate

    # Users per account range
    min_users_per_account: int = 3
    max_users_per_account: int = 120

    # Imperfections
    pct_missing_duration: float = 0.015
    pct_missing_task_id: float = 0.015
    pct_outlier_duration: float = 0.003
    pct_late_events: float = 0.07

    # Output
    out_dir: str = "data/raw"


def set_seeds(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def make_uuid() -> str:
    return str(uuid.uuid4()) # unique identifier


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S") 


def ensure_out_dir(path: str) -> Path:
    out_path = Path(path)
    out_path.mkdir(parents=True, exist_ok=True)
    return out_path


def generate_accounts(cfg: Config) -> pd.DataFrame:
    plan_tiers = ["free", "basic", "pro", "enterprise"]
    plan_probs = [0.35, 0.35, 0.25, 0.05]

    regions = ["NA", "LATAM", "EU", "APAC"]
    region_probs = [0.45, 0.20, 0.25, 0.10]

    # Spread account creation across ~18 months prior to start_date
    anchor = datetime.fromisoformat(cfg.start_date)
    created_start = anchor - timedelta(days=540)

    rows = []
    for i in range(cfg.n_accounts):
        created_at = created_start + timedelta(days=int(np.random.uniform(0, 540))) 
        rows.append(
            {
                "account_id": make_uuid(),
                "account_name": f"Account_{10000 + i}",
                "plan_tier": np.random.choice(plan_tiers, p=plan_probs),
                "created_at": iso(created_at),
                "region": np.random.choice(regions, p=region_probs),
                "is_active": bool(np.random.choice([1, 0], p=[0.93, 0.07])),
            }
        )

    df = pd.DataFrame(rows)
    assert df["account_id"].nunique() == len(df)
    return df


def sample_users_per_account(plan_tier: str, cfg: Config) -> int:
    # Larger accounts on higher tiers
    if plan_tier == "enterprise":
        return int(np.random.randint(50, cfg.max_users_per_account + 1))
    if plan_tier == "pro":
        return int(np.random.randint(15, 81))
    if plan_tier == "basic":
        return int(np.random.randint(cfg.min_users_per_account, 41))
    return int(np.random.randint(cfg.min_users_per_account, 21))


def generate_users(cfg: Config, accounts: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, acc in accounts.iterrows():
        n_users = sample_users_per_account(acc["plan_tier"], cfg)

        acc_created = datetime.fromisoformat(acc["created_at"])
        for _ in range(n_users):
            user_created = acc_created + timedelta(days=int(np.random.uniform(0, 120)))

            activated = np.random.choice([True, False], p=[0.85, 0.15])
            activated_at = (user_created + timedelta(days=int(np.random.uniform(0, 7)))) if activated else None

            is_active = np.random.choice([True, False], p=[0.90, 0.10])
            deactivated_at = None
            if (not is_active) and activated_at is not None:
                deactivated_at = activated_at + timedelta(days=int(np.random.uniform(14, 140)))

            role = np.random.choice(["member", "manager", "admin"], p=[0.80, 0.15, 0.05])

            rows.append(
                {
                    "user_id": make_uuid(),
                    "account_id": acc["account_id"],
                    "role": role,
                    "created_at": iso(user_created),
                    "activated_at": iso(activated_at) if activated_at else None,
                    "timezone": np.random.choice(["UTC", "America/New_York", "America/Bogota", "Europe/London"]),
                    "country": np.random.choice(["US", "CA", "CR", "CO", "GB", "DE", "BR"]),
                    "is_active": bool(is_active),
                    "deactivated_at": iso(deactivated_at) if deactivated_at else None,
                }
            )

    df = pd.DataFrame(rows)
    assert df["user_id"].nunique() == len(df)
    return df



def decide_persona() -> str:
    return np.random.choice(["power", "regular", "light"], p=[0.10, 0.60, 0.30]) # user engagement persona


def activity_probability(plan_tier: str, persona: str) -> float:
    base = {"free": 0.18, "basic": 0.25, "pro": 0.33, "enterprise": 0.42}[plan_tier]
    mult = {"light": 0.60, "regular": 1.00, "power": 1.35}[persona]
    return float(min(0.85, base * mult))


def make_event_row(
    user_row: pd.Series,
    event_ts: datetime,
    event_name: str,
    event_category: str,
    duration_seconds: int | None = None,
    task_id: str | None = None,
) -> dict:
    return {
        "event_id": make_uuid(),
        "event_ts": iso(event_ts),
        "ingested_at": None,  # filled later (late arriving support)
        "event_name": event_name,
        "event_category": event_category,
        "user_id": user_row["user_id"],
        "account_id": user_row["account_id"],
        "task_id": task_id,
        "duration_seconds": duration_seconds,
        "is_productive": True if (event_category == "work_session" and event_name == "timer_stop") else None,
        "source": np.random.choice(["desktop", "web", "mobile", "api"], p=[0.70, 0.15, 0.10, 0.05]),
    }


def generate_events(cfg: Config, accounts: pd.DataFrame, users: pd.DataFrame) -> pd.DataFrame:
    start = datetime.fromisoformat(cfg.start_date)
    dates = [start + timedelta(days=i) for i in range(cfg.days)]

    tier_by_account = dict(zip(accounts["account_id"], accounts["plan_tier"]))

    # Assign persona per user (stable)
    persona_by_user = {u: decide_persona() for u in users["user_id"].tolist()}

    rows: list[dict] = []

    # Iterate users; generate events only for activated users
    for _, u in users.iterrows():
        if pd.isna(u["activated_at"]):
            continue

        tier = tier_by_account[u["account_id"]]
        persona = persona_by_user[u["user_id"]]
        p_active = activity_probability(tier, persona)

        # Soft churn: some users stop generating events after a cutoff date
        churn_cutoff = None
        if np.random.rand() < 0.12:
            churn_cutoff = start + timedelta(days=int(np.random.uniform(15, cfg.days)))

        for d in dates:
            if churn_cutoff and d > churn_cutoff:
                continue

            # If user is inactive in dim_user, reduce events heavily
            if (u["is_active"] is False) and (np.random.rand() < 0.80):
                continue

            if np.random.rand() > p_active:
                continue

            # Engagement events
            n_eng = int(np.random.randint(1, 4))
            for _ in range(n_eng):
                ts = d + timedelta(minutes=int(np.random.uniform(0, 1440)))
                rows.append(make_event_row(u, ts, "app_open", "engagement"))
                if np.random.rand() < 0.40:
                    ts2 = ts + timedelta(minutes=int(np.random.uniform(1, 30)))
                    rows.append(make_event_row(u, ts2, "dashboard_view", "engagement"))

            # Work session events (use timer_stop.duration_seconds as the source of truth for time)
            if np.random.rand() < 0.75:
                start_min = int(np.random.uniform(8 * 60, 11 * 60)) # start between 8:00 and 11:00
                session_start = d + timedelta(minutes=start_min)
                duration = int(np.random.uniform(20 * 60, 3 * 60 * 60))  # 20m to 3h
                session_end = session_start + timedelta(seconds=duration)

                rows.append(make_event_row(u, session_start, "timer_start", "work_session", duration_seconds=None))
                rows.append(make_event_row(u, session_end, "timer_stop", "work_session", duration_seconds=duration))

                # Idle sometimes
                if np.random.rand() < 0.18:
                    idle_ts = session_start + timedelta(minutes=int(np.random.uniform(10, 90)))
                    idle_dur = int(np.random.uniform(60, 600))
                    rows.append(make_event_row(u, idle_ts, "idle_detected", "work_session", duration_seconds=idle_dur))

                # Manual time added rarely
                if np.random.rand() < 0.05:
                    mt_ts = d + timedelta(minutes=int(np.random.uniform(12 * 60, 18 * 60)))
                    mt_dur = int(np.random.uniform(5 * 60, 45 * 60))
                    rows.append(make_event_row(u, mt_ts, "manual_time_added", "work_session", duration_seconds=mt_dur))

            # Output events (task created/completed with shared task_id)
            if np.random.rand() < 0.55:
                lam = 2 if persona != "power" else 5
                n_tasks = int(np.random.poisson(lam=lam))
                for _ in range(max(0, n_tasks)):
                    task_id = make_uuid()
                    created_ts = d + timedelta(minutes=int(np.random.uniform(9 * 60, 17 * 60)))
                    done_ts = created_ts + timedelta(minutes=int(np.random.uniform(15, 240)))

                    rows.append(make_event_row(u, created_ts, "task_created", "output", task_id=task_id))
                    rows.append(make_event_row(u, done_ts, "task_completed", "output", task_id=task_id))

    df = pd.DataFrame(rows)
    df = inject_imperfections(cfg, df)
    return df


def inject_imperfections(cfg: Config, df: pd.DataFrame) -> pd.DataFrame:
    n = len(df)
    if n == 0:
        return df

    # Fill ingested_at: mostly near-real-time, some late events
    event_ts = pd.to_datetime(df["event_ts"])
    delays_minutes = np.random.exponential(scale=5, size=n)

    delays = pd.to_timedelta(delays_minutes, unit="m").to_numpy()

    late_mask = np.random.rand(n) < cfg.pct_late_events
    late_hours = np.random.uniform(1, 72, size=n)

    # Replace a subset with "late" delays
    delays[late_mask] = pd.to_timedelta(late_hours[late_mask], unit="h").to_numpy()


    df["ingested_at"] = (event_ts + delays).dt.strftime("%Y-%m-%dT%H:%M:%S")

    # Missing duration_seconds for some work_session events
    dur_mask = df["event_name"].isin(["timer_stop", "idle_detected", "manual_time_added"]) & (
        np.random.rand(n) < cfg.pct_missing_duration
    )
    df.loc[dur_mask, "duration_seconds"] = None

    # Missing task_id for some task_completed events
    task_mask = (df["event_name"] == "task_completed") & (np.random.rand(n) < cfg.pct_missing_task_id)
    df.loc[task_mask, "task_id"] = None

    # Outlier durations for some timer_stop events (timer left running)
    out_mask = (df["event_name"] == "timer_stop") & (np.random.rand(n) < cfg.pct_outlier_duration)
    df.loc[out_mask, "duration_seconds"] = np.random.uniform(8 * 3600, 16 * 3600, size=out_mask.sum()).astype(int)

    return df


def write_csv(df: pd.DataFrame, out_dir: str, filename: str) -> Path:
    out_path = ensure_out_dir(out_dir)
    full_path = out_path / filename
    df.to_csv(full_path, index=False)
    return full_path


def main() -> None:
    cfg = Config()
    set_seeds(cfg.seed)

    print("Generating data with config:")
    print(cfg)
    print("-" * 60)

    accounts = generate_accounts(cfg)
    users = generate_users(cfg, accounts)
    events = generate_events(cfg, accounts, users)

    p1 = write_csv(accounts, cfg.out_dir, "dim_account.csv")
    p2 = write_csv(users, cfg.out_dir, "dim_user.csv")
    p3 = write_csv(events, cfg.out_dir, "fct_event.csv")

    print("Generated files:")
    print(f"  {p1}  rows={len(accounts)}")
    print(f"  {p2}  rows={len(users)}")
    print(f"  {p3}  rows={len(events)}")

    # Quick health checks
    print("-" * 60)
    print("Quick checks:")
    if len(events) > 0:
        evt = events.copy()
        evt["event_date"] = pd.to_datetime(evt["event_ts"]).dt.date
        print(f"  date range: {evt['event_date'].min()} -> {evt['event_date'].max()}")
        print(f"  late events (ingested_at > event_ts + 1h): ", end="")
        lag = pd.to_datetime(evt["ingested_at"]) - pd.to_datetime(evt["event_ts"])
        print(f"{(lag > pd.Timedelta(hours=1)).mean():.2%}")
        print(f"  missing duration_seconds: {events['duration_seconds'].isna().mean():.2%}")
        print(f"  missing task_id on task_completed: ", end="")
        tc = events[events["event_name"] == "task_completed"]
        print(f"{tc['task_id'].isna().mean():.2%}" if len(tc) else "n/a")
    print("-" * 60)


if __name__ == "__main__":
    main()
