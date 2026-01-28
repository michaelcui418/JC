from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Stage:
    stage_id: str
    name: str
    start_date: date
    end_date: date
    actions: list[str]
    training_frequency_per_week: int

    @classmethod
    def from_dict(cls, payload: dict) -> "Stage":
        return cls(
            stage_id=payload["id"],
            name=payload["name"],
            start_date=date.fromisoformat(payload["start_date"]),
            end_date=date.fromisoformat(payload["end_date"]),
            actions=list(payload.get("actions", [])),
            training_frequency_per_week=int(payload["training_frequency_per_week"]),
        )

    def includes(self, target_date: date) -> bool:
        return self.start_date <= target_date <= self.end_date


@dataclass(frozen=True)
class Plan:
    plan_id: str
    name: str
    version: str
    stages: tuple[Stage, ...]
    metadata: dict

    @classmethod
    def from_dict(cls, payload: dict, plan_id: str) -> "Plan":
        stages = tuple(Stage.from_dict(stage) for stage in payload["stages"])
        return cls(
            plan_id=plan_id,
            name=payload.get("name", plan_id),
            version=payload.get("version", "1.0"),
            stages=stages,
            metadata=payload.get("metadata", {}),
        )

    def iter_stages(self) -> Iterable[Stage]:
        return iter(self.stages)


class PlanManager:
    def __init__(self, plans_dir: Path | str | None = None) -> None:
        if plans_dir is None:
            repo_root = Path(__file__).resolve().parents[2]
            plans_dir = repo_root / "plans"
        self.plans_dir = Path(plans_dir)

    def list_plan_files(self) -> list[Path]:
        return sorted(self.plans_dir.glob("*.json"))

    def load_plan(self, plan_file: str = "default_plan.json") -> Plan:
        plan_path = self.plans_dir / plan_file
        if not plan_path.exists():
            raise FileNotFoundError(f"Plan file not found: {plan_path}")
        payload = json.loads(plan_path.read_text(encoding="utf-8"))
        return Plan.from_dict(payload, plan_id=plan_path.stem)

    def resolve_stage(
        self,
        plan: Plan,
        target_date: date | None = None,
        stage_id: str | None = None,
    ) -> Stage:
        if stage_id:
            for stage in plan.iter_stages():
                if stage.stage_id == stage_id:
                    return stage
            raise ValueError(f"Stage '{stage_id}' not found in plan '{plan.plan_id}'.")

        resolved_date = target_date or date.today()
        for stage in plan.iter_stages():
            if stage.includes(resolved_date):
                return stage

        raise ValueError(
            f"No stage found for date {resolved_date.isoformat()} in plan '{plan.plan_id}'."
        )

    def load_plan_for_date_or_stage(
        self,
        plan_file: str = "default_plan.json",
        target_date: date | None = None,
        stage_id: str | None = None,
    ) -> tuple[Plan, Stage]:
        plan = self.load_plan(plan_file)
        stage = self.resolve_stage(plan, target_date=target_date, stage_id=stage_id)
        return plan, stage
