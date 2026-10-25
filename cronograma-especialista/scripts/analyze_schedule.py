#!/usr/bin/env python3
"""Validate a normalized precedence network and calculate generalized CPM."""

from __future__ import annotations

import argparse
import heapq
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALLOWED_TYPES = {"FS", "SS", "FF", "SF"}
TOLERANCE = 1e-9


@dataclass(frozen=True)
class Edge:
    predecessor: str
    successor: str
    relation: str
    lag: float
    weight: float


def finite_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def analyze(payload: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if not isinstance(payload, dict) or not isinstance(payload.get("activities"), list):
        return {
            "status": "invalid",
            "errors": [{"code": "INVALID_ROOT", "message": "A raiz deve conter uma lista activities."}],
            "warnings": [],
        }

    raw_activities = payload["activities"]
    durations: dict[str, float] = {}
    raw_by_id: dict[str, dict[str, Any]] = {}

    for index, raw in enumerate(raw_activities):
        if not isinstance(raw, dict):
            errors.append({"code": "INVALID_ACTIVITY", "message": f"activities[{index}] não é um objeto."})
            continue
        activity_id = str(raw.get("id", "")).strip()
        if not activity_id:
            errors.append({"code": "MISSING_ID", "message": f"activities[{index}] não possui id."})
            continue
        if activity_id in raw_by_id:
            errors.append({"code": "DUPLICATE_ID", "message": f"ID duplicado: {activity_id}."})
            continue
        duration = finite_number(raw.get("duration"))
        if duration is None or duration < 0:
            errors.append({"code": "INVALID_DURATION", "message": f"Duração inválida em {activity_id}."})
            continue
        raw_by_id[activity_id] = raw
        durations[activity_id] = duration

    edges: list[Edge] = []
    seen_relations: set[tuple[str, str, str, float]] = set()

    for successor, raw in raw_by_id.items():
        dependencies = raw.get("dependencies", [])
        if dependencies is None:
            dependencies = []
        if not isinstance(dependencies, list):
            errors.append({"code": "INVALID_DEPENDENCIES", "message": f"dependencies de {successor} não é uma lista."})
            continue
        for dep_index, dependency in enumerate(dependencies):
            if not isinstance(dependency, dict):
                errors.append({"code": "INVALID_DEPENDENCY", "message": f"Dependência {dep_index} de {successor} não é um objeto."})
                continue
            predecessor = str(dependency.get("predecessor", "")).strip()
            relation = str(dependency.get("type", "FS")).strip().upper()
            lag = finite_number(dependency.get("lag", 0))
            if predecessor not in durations:
                errors.append({"code": "MISSING_PREDECESSOR", "message": f"{successor} referencia predecessora inexistente: {predecessor or '(vazia)'}."})
                continue
            if predecessor == successor:
                errors.append({"code": "SELF_DEPENDENCY", "message": f"{successor} depende de si mesma."})
                continue
            if relation not in ALLOWED_TYPES:
                errors.append({"code": "INVALID_RELATION", "message": f"Tipo {relation or '(vazio)'} inválido em {predecessor} → {successor}."})
                continue
            if lag is None:
                errors.append({"code": "INVALID_LAG", "message": f"Lag inválido em {predecessor} → {successor}."})
                continue
            relation_key = (predecessor, successor, relation, lag)
            if relation_key in seen_relations:
                errors.append({"code": "DUPLICATE_DEPENDENCY", "message": f"Dependência duplicada: {predecessor} {relation} {successor}, lag {lag}."})
                continue
            seen_relations.add(relation_key)
            if lag < 0:
                warnings.append({"code": "NEGATIVE_LAG", "message": f"Defasagem negativa em {predecessor} → {successor}; confirme se a antecipação é permitida."})

            if relation == "FS":
                weight = durations[predecessor] + lag
            elif relation == "SS":
                weight = lag
            elif relation == "FF":
                weight = durations[predecessor] + lag - durations[successor]
            else:  # SF
                weight = lag - durations[successor]
            edges.append(Edge(predecessor, successor, relation, lag, weight))

    if errors:
        return {"status": "invalid", "errors": errors, "warnings": warnings}

    successors: dict[str, list[Edge]] = {activity_id: [] for activity_id in durations}
    indegree = {activity_id: 0 for activity_id in durations}
    for edge in edges:
        successors[edge.predecessor].append(edge)
        indegree[edge.successor] += 1

    ready = [activity_id for activity_id, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)
    order: list[str] = []
    while ready:
        current = heapq.heappop(ready)
        order.append(current)
        for edge in sorted(successors[current], key=lambda item: (item.successor, item.relation, item.lag)):
            indegree[edge.successor] -= 1
            if indegree[edge.successor] == 0:
                heapq.heappush(ready, edge.successor)

    if len(order) != len(durations):
        cycle_nodes = sorted(activity_id for activity_id, degree in indegree.items() if degree > 0)
        return {
            "status": "invalid",
            "errors": [{"code": "CYCLE", "message": "A rede contém ciclo envolvendo: " + ", ".join(cycle_nodes) + "."}],
            "warnings": warnings,
        }

    earliest_start = {activity_id: 0.0 for activity_id in durations}
    for current in order:
        for edge in successors[current]:
            candidate = earliest_start[current] + edge.weight
            earliest_start[edge.successor] = max(earliest_start[edge.successor], candidate, 0.0)

    earliest_finish = {
        activity_id: earliest_start[activity_id] + durations[activity_id]
        for activity_id in durations
    }
    project_duration = max(earliest_finish.values(), default=0.0)

    latest_start = {
        activity_id: project_duration - durations[activity_id]
        for activity_id in durations
    }
    for current in reversed(order):
        for edge in successors[current]:
            latest_start[current] = min(latest_start[current], latest_start[edge.successor] - edge.weight)

    results: list[dict[str, Any]] = []
    for activity_id in order:
        total_float = latest_start[activity_id] - earliest_start[activity_id]
        if successors[activity_id]:
            free_float = min(
                earliest_start[edge.successor] - (earliest_start[activity_id] + edge.weight)
                for edge in successors[activity_id]
            )
        else:
            free_float = project_duration - earliest_finish[activity_id]
        results.append({
            "id": activity_id,
            "duration": durations[activity_id],
            "early_start": earliest_start[activity_id],
            "early_finish": earliest_finish[activity_id],
            "late_start": latest_start[activity_id],
            "late_finish": latest_start[activity_id] + durations[activity_id],
            "total_float": 0.0 if abs(total_float) <= TOLERANCE else total_float,
            "free_float": 0.0 if abs(free_float) <= TOLERANCE else free_float,
            "critical": abs(total_float) <= TOLERANCE,
        })

    return {
        "status": "ok",
        "errors": [],
        "warnings": warnings,
        "project_duration": project_duration,
        "topological_order": order,
        "activities": results,
    }


def load_payload(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida uma rede normalizada e calcula CPM generalizado.")
    parser.add_argument("input", help="Arquivo JSON de entrada ou - para stdin.")
    parser.add_argument("--pretty", action="store_true", help="Formata o JSON de saída.")
    args = parser.parse_args()

    try:
        result = analyze(load_payload(args.input))
    except (OSError, json.JSONDecodeError) as exc:
        result = {"status": "invalid", "errors": [{"code": "INPUT_ERROR", "message": str(exc)}], "warnings": []}

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2 if args.pretty else None)
    sys.stdout.write("\n")
    return 0 if result.get("status") == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
