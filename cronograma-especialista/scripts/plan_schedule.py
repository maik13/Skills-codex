#!/usr/bin/env python3
"""Planejador determinístico inspirado no motor operacional do Planejamento 2.0."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import defaultdict, deque
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


EPSILON = 1e-9
MAX_DAYS_WITHOUT_EXPLICIT_HORIZON = 365 * 5
RELATION_ALIASES = {
    "FS": "FS",
    "FIM-INICIO": "FS",
    "FIM–INICIO": "FS",
    "SS": "SS",
    "INICIO-INICIO": "SS",
    "INÍCIO-INÍCIO": "SS",
    "INÍCIO–INÍCIO": "SS",
    "FF": "FF",
    "FIM-FIM": "FF",
    "FIM–FIM": "FF",
}


def parse_iso(value: Any, field: str, errors: list[dict[str, str]], required: bool = False) -> date | None:
    if value in (None, ""):
        if required:
            errors.append({"code": "REQUIRED_DATE", "field": field, "message": f"{field} é obrigatório."})
        return None
    if not isinstance(value, str):
        errors.append({"code": "INVALID_DATE", "field": field, "message": f"{field} deve usar YYYY-MM-DD."})
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        errors.append({"code": "INVALID_DATE", "field": field, "message": f"{field} deve usar YYYY-MM-DD."})
        return None


def number(value: Any, field: str, errors: list[dict[str, str]], minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append({"code": "INVALID_NUMBER", "field": field, "message": f"{field} deve ser numérico."})
        return 0.0
    result = float(value)
    if minimum is not None and result < minimum:
        errors.append({"code": "OUT_OF_RANGE", "field": field, "message": f"{field} deve ser maior ou igual a {minimum}."})
    return result


def normalize_relation(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    key = value.strip().upper().replace("_", "-")
    return RELATION_ALIASES.get(key)


def is_workday(day: date, settings: dict[str, Any], holidays: set[date]) -> bool:
    if day in holidays:
        return False
    if day.weekday() == 5 and not settings.get("workOnSaturdays", False):
        return False
    if day.weekday() == 6 and not settings.get("workOnSundays", False):
        return False
    return True


def add_workdays(day: date, count: int, settings: dict[str, Any], holidays: set[date]) -> date:
    if count <= 0:
        return day
    cursor = day
    remaining = count
    while remaining:
        cursor += timedelta(days=1)
        if is_workday(cursor, settings, holidays):
            remaining -= 1
    return cursor


def next_workday(day: date, settings: dict[str, Any], holidays: set[date]) -> date:
    return add_workdays(day, 1, settings, holidays)


def detect_cycle(activity_ids: set[str], dependencies: list[tuple[str, str]]) -> list[str]:
    indegree = {activity_id: 0 for activity_id in activity_ids}
    successors: dict[str, list[str]] = defaultdict(list)
    for predecessor, successor in dependencies:
        successors[predecessor].append(successor)
        indegree[successor] += 1
    queue = deque(sorted(activity_id for activity_id, degree in indegree.items() if degree == 0))
    visited: list[str] = []
    while queue:
        current = queue.popleft()
        visited.append(current)
        for successor in successors[current]:
            indegree[successor] -= 1
            if indegree[successor] == 0:
                queue.append(successor)
    return sorted(activity_id for activity_id, degree in indegree.items() if degree > 0)


def validate_and_normalize(payload: Any) -> tuple[dict[str, Any] | None, list[dict[str, str]], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not isinstance(payload, dict):
        return None, [{"code": "INVALID_PAYLOAD", "field": "$", "message": "A entrada deve ser um objeto JSON."}], warnings

    normalized = copy.deepcopy(payload)
    settings = normalized.get("settings")
    projects = normalized.get("projects")
    if not isinstance(settings, dict):
        errors.append({"code": "REQUIRED_OBJECT", "field": "settings", "message": "settings é obrigatório."})
        settings = {}
        normalized["settings"] = settings
    if not isinstance(projects, list):
        errors.append({"code": "REQUIRED_ARRAY", "field": "projects", "message": "projects deve ser uma lista."})
        projects = []
        normalized["projects"] = projects

    start = parse_iso(settings.get("globalStartDate"), "settings.globalStartDate", errors, required=True)
    end = parse_iso(settings.get("globalEndDate"), "settings.globalEndDate", errors)
    parse_iso(normalized.get("asOfDate"), "asOfDate", errors, required=True)
    team = number(settings.get("availableTeamPerDay"), "settings.availableTeamPerDay", errors, minimum=0)
    settings["availableTeamPerDay"] = team
    if start and end and end < start:
        errors.append({"code": "INVALID_HORIZON", "field": "settings.globalEndDate", "message": "globalEndDate não pode ser anterior a globalStartDate."})

    holiday_values = settings.get("holidays", [])
    if not isinstance(holiday_values, list):
        errors.append({"code": "INVALID_ARRAY", "field": "settings.holidays", "message": "holidays deve ser uma lista."})
        holiday_values = []
        settings["holidays"] = []
    for index, value in enumerate(holiday_values):
        parse_iso(value, f"settings.holidays[{index}]", errors)

    project_ids: set[str] = set()
    activity_ids: set[str] = set()
    activity_locations: dict[str, str] = {}
    dependency_edges: list[tuple[str, str]] = []

    for project_index, project in enumerate(projects):
        base = f"projects[{project_index}]"
        if not isinstance(project, dict):
            errors.append({"code": "INVALID_PROJECT", "field": base, "message": "Projeto deve ser um objeto."})
            continue
        project_id = project.get("id")
        if not isinstance(project_id, str) or not project_id.strip():
            errors.append({"code": "REQUIRED_ID", "field": f"{base}.id", "message": "O projeto precisa de ID."})
            project_id = f"__invalid_project_{project_index}"
        elif project_id in project_ids:
            errors.append({"code": "DUPLICATE_PROJECT", "field": f"{base}.id", "message": f"Projeto duplicado: {project_id}."})
        project_ids.add(project_id)
        project["id"] = project_id
        project["priority"] = number(project.get("priority", 9999), f"{base}.priority", errors)
        parse_iso(project.get("startDate"), f"{base}.startDate", errors)
        parse_iso(project.get("deadlineDate"), f"{base}.deadlineDate", errors)
        activities = project.get("activities")
        if not isinstance(activities, list):
            errors.append({"code": "INVALID_ARRAY", "field": f"{base}.activities", "message": "activities deve ser uma lista."})
            project["activities"] = []
            continue
        for activity_index, activity in enumerate(activities):
            activity_base = f"{base}.activities[{activity_index}]"
            if not isinstance(activity, dict):
                errors.append({"code": "INVALID_ACTIVITY", "field": activity_base, "message": "Atividade deve ser um objeto."})
                continue
            activity_id = activity.get("id")
            if not isinstance(activity_id, str) or not activity_id.strip():
                errors.append({"code": "REQUIRED_ID", "field": f"{activity_base}.id", "message": "A atividade precisa de ID."})
                activity_id = f"__invalid_activity_{project_index}_{activity_index}"
            elif activity_id in activity_ids:
                errors.append({"code": "DUPLICATE_ACTIVITY", "field": f"{activity_base}.id", "message": f"Atividade duplicada: {activity_id}."})
            activity_ids.add(activity_id)
            activity_locations[activity_id] = activity_base
            activity["id"] = activity_id
            activity["projectId"] = project_id
            total = number(activity.get("totalQuantity"), f"{activity_base}.totalQuantity", errors, minimum=0)
            completed = number(activity.get("completedQuantity", 0), f"{activity_base}.completedQuantity", errors, minimum=0)
            capacity = number(activity.get("capacityPerDay"), f"{activity_base}.capacityPerDay", errors, minimum=0)
            people = number(activity.get("requiredPeople"), f"{activity_base}.requiredPeople", errors, minimum=0)
            activity["priority"] = number(activity.get("priority", 9999), f"{activity_base}.priority", errors)
            activity["sequence"] = number(activity.get("sequence", activity_index + 1), f"{activity_base}.sequence", errors)
            if completed > total + EPSILON:
                errors.append({"code": "PROGRESS_EXCEEDS_TOTAL", "field": f"{activity_base}.completedQuantity", "message": "A quantidade concluída supera a quantidade total."})
            if total - completed > EPSILON and capacity <= EPSILON:
                errors.append({"code": "ZERO_CAPACITY", "field": f"{activity_base}.capacityPerDay", "message": "Atividade com saldo precisa de capacidade diária positiva."})
            if people > team + EPSILON and not activity.get("acceptsProportionalProduction", False):
                warnings.append({"code": "TEAM_BELOW_REQUIREMENT", "field": f"{activity_base}.requiredPeople", "message": f"{activity_id} exige {people:g} pessoas, acima das {team:g} disponíveis."})
            activity["totalQuantity"] = total
            activity["completedQuantity"] = completed
            activity["capacityPerDay"] = capacity
            activity["requiredPeople"] = people
            parse_iso(activity.get("plannedStartDate"), f"{activity_base}.plannedStartDate", errors)
            parse_iso(activity.get("actualStartDate", activity.get("realStartDate")), f"{activity_base}.actualStartDate", errors)
            parse_iso(activity.get("actualEndDate", activity.get("realEndDate")), f"{activity_base}.actualEndDate", errors)
            dependencies = activity.get("dependencies", [])
            if not isinstance(dependencies, list):
                errors.append({"code": "INVALID_ARRAY", "field": f"{activity_base}.dependencies", "message": "dependencies deve ser uma lista."})
                activity["dependencies"] = []

    seen_dependencies: set[tuple[str, str, str]] = set()
    for project in projects:
        if not isinstance(project, dict):
            continue
        for activity in project.get("activities", []):
            if not isinstance(activity, dict):
                continue
            normalized_dependencies: list[dict[str, Any]] = []
            for dep_index, dependency in enumerate(activity.get("dependencies", [])):
                field = f"{activity_locations.get(activity['id'], activity['id'])}.dependencies[{dep_index}]"
                if not isinstance(dependency, dict):
                    errors.append({"code": "INVALID_DEPENDENCY", "field": field, "message": "Dependência deve ser um objeto."})
                    continue
                predecessor = dependency.get("dependsOnId") or dependency.get("predecessor")
                relation = normalize_relation(dependency.get("type"))
                lag = dependency.get("lagDays", dependency.get("lag", 0))
                if predecessor not in activity_ids:
                    errors.append({"code": "MISSING_PREDECESSOR", "field": f"{field}.dependsOnId", "message": f"Predecessora inexistente: {predecessor}."})
                    continue
                if predecessor == activity["id"]:
                    errors.append({"code": "SELF_DEPENDENCY", "field": f"{field}.dependsOnId", "message": "Atividade não pode depender de si mesma."})
                    continue
                if relation is None:
                    errors.append({"code": "INVALID_RELATION", "field": f"{field}.type", "message": "Use FS, SS ou FF."})
                    continue
                if isinstance(lag, bool) or not isinstance(lag, int) or lag < 0:
                    errors.append({"code": "INVALID_LAG", "field": f"{field}.lagDays", "message": "lagDays deve ser um inteiro maior ou igual a zero."})
                    continue
                key = (predecessor, activity["id"], relation)
                if key in seen_dependencies:
                    errors.append({"code": "DUPLICATE_DEPENDENCY", "field": field, "message": "Dependência duplicada."})
                    continue
                seen_dependencies.add(key)
                dependency_edges.append((predecessor, activity["id"]))
                normalized_dependencies.append({"dependsOnId": predecessor, "type": relation, "lagDays": lag})
            activity["dependencies"] = normalized_dependencies

    cycle = detect_cycle(activity_ids, dependency_edges) if activity_ids else []
    if cycle:
        errors.append({"code": "CYCLE", "field": "projects", "message": "Ciclo de dependências: " + ", ".join(cycle)})
    return normalized, errors, warnings


def plan(payload: Any) -> dict[str, Any]:
    normalized, errors, warnings = validate_and_normalize(payload)
    if errors or normalized is None:
        return {"status": "invalid", "errors": errors, "warnings": warnings}

    settings = normalized["settings"]
    projects = normalized["projects"]
    start = datetime.strptime(settings["globalStartDate"], "%Y-%m-%d").date()
    explicit_end = settings.get("globalEndDate")
    end = datetime.strptime(explicit_end, "%Y-%m-%d").date() if explicit_end else start + timedelta(days=MAX_DAYS_WITHOUT_EXPLICIT_HORIZON)
    holidays = {datetime.strptime(value, "%Y-%m-%d").date() for value in settings.get("holidays", [])}
    team = float(settings["availableTeamPerDay"])

    active_projects = [project for project in projects if project.get("active", True)]
    project_map = {project["id"]: project for project in active_projects}
    activities = [activity for project in active_projects for activity in project.get("activities", [])]
    activity_map = {activity["id"]: activity for activity in activities}

    for activity in activities:
        activity["_remaining"] = max(0.0, activity["totalQuantity"] - activity["completedQuantity"])
        activity["_scheduled"] = 0.0
        activity["_calculatedStart"] = None
        activity["_calculatedEnd"] = None
        activity["_allocations"] = []
        actual_start = activity.get("actualStartDate", activity.get("realStartDate"))
        actual_end = activity.get("actualEndDate", activity.get("realEndDate"))
        activity["_started"] = bool(actual_start or activity["completedQuantity"] > EPSILON or activity.get("status") in ("Em Andamento", "Concluído"))
        activity["_startDate"] = datetime.strptime(actual_start, "%Y-%m-%d").date() if actual_start else None
        activity["_complete"] = activity["_remaining"] <= EPSILON or activity.get("status") == "Concluído"
        activity["_finishDate"] = datetime.strptime(actual_end, "%Y-%m-%d").date() if actual_end else None
        if activity["_complete"] and activity["_finishDate"] is None:
            activity["_finishDate"] = start - timedelta(days=1)

    def progress(activity: dict[str, Any]) -> float:
        return min(activity["totalQuantity"], activity["completedQuantity"] + activity["_scheduled"])

    def dependency_allows_start(activity: dict[str, Any], day: date) -> bool:
        for dependency in activity["dependencies"]:
            predecessor = activity_map[dependency["dependsOnId"]]
            lag = dependency["lagDays"]
            if dependency["type"] == "FS":
                if not predecessor["_complete"] or predecessor["_finishDate"] is None:
                    return False
                if day < add_workdays(predecessor["_finishDate"], lag + 1, settings, holidays):
                    return False
            elif dependency["type"] == "SS":
                if not predecessor["_started"] or predecessor["_startDate"] is None:
                    return False
                if day < add_workdays(predecessor["_startDate"], lag, settings, holidays):
                    return False
        return True

    def ff_allows_finish(activity: dict[str, Any], day: date) -> bool:
        for dependency in activity["dependencies"]:
            if dependency["type"] != "FF":
                continue
            predecessor = activity_map[dependency["dependsOnId"]]
            if not predecessor["_complete"] or predecessor["_finishDate"] is None:
                return False
            if day < add_workdays(predecessor["_finishDate"], dependency["lagDays"], settings, holidays):
                return False
        return True

    daily_summary: dict[str, dict[str, float]] = {}
    cursor = start
    days_examined = 0
    while cursor <= end and any(not activity["_complete"] for activity in activities):
        if is_workday(cursor, settings, holidays):
            candidates: list[dict[str, Any]] = []
            for activity in activities:
                if activity["_complete"]:
                    continue
                project = project_map[activity["projectId"]]
                earliest_values = [start]
                for value in (project.get("startDate"), activity.get("plannedStartDate")):
                    if value:
                        earliest_values.append(datetime.strptime(value, "%Y-%m-%d").date())
                if cursor < max(earliest_values):
                    continue
                if dependency_allows_start(activity, cursor):
                    candidates.append(activity)

            candidates.sort(key=lambda activity: (
                project_map[activity["projectId"]]["priority"],
                activity["priority"],
                activity["sequence"],
                activity["id"],
            ))
            people_available = team
            people_used = 0.0
            unmet_demand = 0.0
            produced_today = 0.0

            for activity in candidates:
                remaining = max(0.0, activity["_remaining"] - activity["_scheduled"])
                if remaining <= EPSILON:
                    continue
                required = activity["requiredPeople"]
                capacity = activity["capacityPerDay"]
                people_needed = required
                possible = min(remaining, capacity)

                if required > people_available + EPSILON:
                    if activity.get("acceptsProportionalProduction", False) and people_available > EPSILON and required > EPSILON:
                        possible = min(remaining, capacity * people_available / required)
                        people_needed = people_available
                    elif required > EPSILON:
                        unmet_demand += required
                        continue

                for dependency in activity["dependencies"]:
                    if dependency["type"] != "SS":
                        continue
                    predecessor = activity_map[dependency["dependsOnId"]]
                    available_from_predecessor = progress(predecessor) - progress(activity)
                    possible = min(possible, max(0.0, available_from_predecessor))

                if possible + EPSILON >= remaining and not ff_allows_finish(activity, cursor):
                    possible = 0.0
                if possible <= EPSILON:
                    continue

                if capacity > EPSILON and possible < capacity - EPSILON and activity.get("acceptsProportionalProduction", False):
                    people_needed = min(people_needed, required * possible / capacity)
                people_needed = min(people_needed, people_available)
                possible = round(possible, 6)
                people_needed = round(people_needed, 6)

                if not activity["_started"]:
                    activity["_started"] = True
                    activity["_startDate"] = cursor
                if activity["_calculatedStart"] is None:
                    activity["_calculatedStart"] = cursor
                activity["_scheduled"] += possible
                activity["_allocations"].append({
                    "date": cursor.isoformat(),
                    "quantityProduced": possible,
                    "peopleUsed": people_needed,
                })
                people_available -= people_needed
                people_used += people_needed
                produced_today += possible
                if activity["_scheduled"] + EPSILON >= activity["_remaining"]:
                    activity["_complete"] = True
                    activity["_finishDate"] = cursor
                    activity["_calculatedEnd"] = cursor

            daily_summary[cursor.isoformat()] = {
                "peopleAvailable": round(team, 6),
                "peopleUsed": round(people_used, 6),
                "idlePeople": round(max(0.0, people_available), 6),
                "unmetDemand": round(unmet_demand, 6),
                "quantityProduced": round(produced_today, 6),
            }
        cursor += timedelta(days=1)
        days_examined += 1
        if days_examined > MAX_DAYS_WITHOUT_EXPLICIT_HORIZON and not explicit_end:
            break

    alerts: list[dict[str, Any]] = []
    output_projects: list[dict[str, Any]] = []
    unscheduled_count = 0
    all_finish_dates: list[date] = []
    process_load: dict[str, dict[str, float]] = defaultdict(lambda: {"remainingQuantity": 0.0, "nominalWorkDays": 0.0, "personDays": 0.0})

    for project in projects:
        output_project = {key: copy.deepcopy(value) for key, value in project.items() if key != "activities"}
        output_activities: list[dict[str, Any]] = []
        project_finish_dates: list[date] = []
        for activity in project.get("activities", []):
            output_activity = {key: copy.deepcopy(value) for key, value in activity.items() if not key.startswith("_")}
            if project.get("active", True):
                unscheduled = max(0.0, activity["_remaining"] - activity["_scheduled"])
                if unscheduled > EPSILON:
                    unscheduled_count += 1
                    planning_status = "Não programada"
                    alerts.append({
                        "code": "UNSCHEDULED_ACTIVITY",
                        "severity": "high",
                        "projectId": project["id"],
                        "activityId": activity["id"],
                        "message": f"{activity['id']} manteve {unscheduled:g} {activity.get('unit', '')} fora do horizonte.",
                    })
                elif activity["_remaining"] <= EPSILON:
                    planning_status = "Concluída"
                else:
                    planning_status = "Programada"
                output_activity.update({
                    "remainingQuantityAtCutoff": round(activity["_remaining"], 6),
                    "scheduledQuantity": round(activity["_scheduled"], 6),
                    "unscheduledQuantity": round(unscheduled, 6),
                    "calculatedStartDate": activity["_calculatedStart"].isoformat() if activity["_calculatedStart"] else None,
                    "calculatedEndDate": activity["_calculatedEnd"].isoformat() if activity["_calculatedEnd"] else None,
                    "workingDays": len(activity["_allocations"]),
                    "dailyAllocations": activity["_allocations"],
                    "planningStatus": planning_status,
                })
                if activity["_finishDate"]:
                    project_finish_dates.append(activity["_finishDate"])
                    all_finish_dates.append(activity["_finishDate"])
                if activity["_remaining"] > EPSILON:
                    load = process_load[activity.get("processName", "Não informado")]
                    load["remainingQuantity"] += activity["_remaining"]
                    load["nominalWorkDays"] += activity["_remaining"] / activity["capacityPerDay"]
                    load["personDays"] += activity["_remaining"] / activity["capacityPerDay"] * activity["requiredPeople"]
            else:
                output_activity.update({"planningStatus": "Projeto inativo", "dailyAllocations": []})
            output_activities.append(output_activity)
        output_project["activities"] = output_activities
        project_end = max(project_finish_dates) if project_finish_dates else None
        output_project["calculatedEndDate"] = project_end.isoformat() if project_end else None
        deadline_value = project.get("deadlineDate")
        if deadline_value and project_end:
            deadline = datetime.strptime(deadline_value, "%Y-%m-%d").date()
            variance = (project_end - deadline).days
            output_project["deadlineVarianceCalendarDays"] = variance
            if variance > 0:
                alerts.append({
                    "code": "DEADLINE_MISSED",
                    "severity": "high",
                    "projectId": project["id"],
                    "message": f"Projeto termina {variance} dia(s) após o prazo {deadline_value}.",
                })
        output_projects.append(output_project)

    bottlenecks = [
        {"processName": process_name, **{key: round(value, 6) for key, value in values.items()}}
        for process_name, values in sorted(process_load.items(), key=lambda item: (-item[1]["personDays"], item[0]))
    ]
    peak_people = max((summary["peopleUsed"] for summary in daily_summary.values()), default=0.0)
    saturated_days = sum(1 for summary in daily_summary.values() if team > EPSILON and summary["peopleUsed"] >= team - EPSILON)
    status = "ok" if unscheduled_count == 0 else "infeasible"
    return {
        "status": status,
        "actionState": "SIMULADO",
        "errors": [],
        "warnings": warnings,
        "summary": {
            "asOfDate": normalized["asOfDate"],
            "globalStartDate": settings["globalStartDate"],
            "calculatedCompletionDate": max(all_finish_dates).isoformat() if all_finish_dates else None,
            "availableTeamPerDay": team,
            "peakPeopleUsed": peak_people,
            "saturatedWorkdays": saturated_days,
            "unscheduledActivities": unscheduled_count,
        },
        "projects": output_projects,
        "dailySummary": daily_summary,
        "bottlenecks": bottlenecks,
        "alerts": alerts,
    }


def load_payload(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera um cronograma nivelado conforme a lógica do Planejamento 2.0.")
    parser.add_argument("input", help="Arquivo JSON de entrada ou - para stdin.")
    parser.add_argument("--pretty", action="store_true", help="Formata o JSON de saída.")
    args = parser.parse_args()
    try:
        result = plan(load_payload(args.input))
    except (OSError, json.JSONDecodeError) as exc:
        result = {"status": "invalid", "errors": [{"code": "INPUT_ERROR", "message": str(exc)}], "warnings": []}
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2 if args.pretty else None)
    sys.stdout.write("\n")
    return 0 if result.get("status") == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
