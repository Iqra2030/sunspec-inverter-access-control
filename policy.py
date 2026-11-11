"""Policy generator, request check and change verifier. Standard library only."""
import json
from pathlib import Path

HERE = Path(__file__).parent
READ_FCS = {3}  # This example authorises holding-register reads only.


def load(name):
    return json.loads((HERE / name).read_text())


def spans_for(profile, point_name):
    """Register spans needed to decode one point: the point plus its scale factor."""
    pts = profile["points"]
    names = [point_name] + ([pts[point_name]["sf"]] if pts[point_name].get("sf") else [])
    return [{"point": n, "start": pts[n]["start"], "regs": pts[n]["regs"]} for n in names]


def generate(profile, tasks):
    """Task + role + installed profile -> traceable permissions, or an unsupported-task finding."""
    policy = {}
    for role, task_ids in tasks["roles"].items():
        entries = []
        for tid in task_ids:
            task = tasks["tasks"][tid]
            point = profile["points"].get(task["point"])
            if task["operation"] != "read":
                entries.append({"task": tid, "status": "unsupported", "reason": "only read tasks supported", "spans": []})
                continue
            if point is None or not point["supported"]:
                why = "point absent from profile" if point is None else point.get("note", "profile marks point unsupported")
                entries.append({"task": tid, "status": "unsupported", "reason": why, "spans": []})
            else:
                if task.get("semantic") != point["semantic"] or task.get("unit") != point["unit"]:
                    entries.append({"task": tid, "status": "review_required",
                                    "reason": "task meaning or units differ from profile", "spans": []})
                    continue
                sf = point.get("sf")
                if sf and (sf not in profile["points"] or not profile["points"][sf]["supported"]):
                    entries.append({"task": tid, "status": "unsupported",
                                    "reason": "scale factor unavailable", "spans": []})
                    continue
                entries.append({"task": tid, "status": "permit", "operation": task["operation"],
                                "justification": task["description"], "unit_id": profile["unit_id"],
                                "point": task["point"], "spans": spans_for(profile, task["point"]),
                                "evidence": [profile["points"][s["point"]]["evidence"]["status"]
                                             for s in spans_for(profile, task["point"])]})
        policy[role] = entries
    return policy


def decide(policy, role, unit_id, fc, start, count):
    """Gateway decision. Reads only, one unit ID only. A request may not cut a point in half."""
    if any(type(v) is not int for v in (unit_id, fc, start, count)):
        return False, "integer request fields required"
    if not (0 <= unit_id <= 255 and 0 <= start <= 65535 and 1 <= count <= 125
            and start + count <= 65536):
        return False, "request outside Modbus read bounds"
    if fc not in READ_FCS:
        return False, "function code not approved (read-only tasks)"
    if count < 1:
        return False, "empty request"
    entries = [e for e in policy.get(role, []) if e["status"] == "permit" and e.get("operation") == "read"]
    if not any(e["unit_id"] == unit_id for e in entries):
        return False, "unit ID not approved for this role"
    spans = [s for e in entries if e["unit_id"] == unit_id for s in e["spans"]]
    req = set(range(start, start + count))
    covered = set()
    for s in spans:
        addrs = set(range(s["start"], s["start"] + s["regs"]))
        if req & addrs:
            if not addrs <= req:
                return False, f"request cuts point {s['point']} in half"
            covered |= addrs
    if req - covered:
        return False, "request touches addresses outside the approved points"
    return True, "permitted"


def point_at(profile, address):
    for name, p in profile["points"].items():
        if p["start"] <= address < p["start"] + p["regs"]:
            return name
    return None


def audit_stale(old_policy, new_profile):
    """Apply an old permission set to a replacement device. Report what each permitted address now means."""
    findings = []
    for role, entries in old_policy.items():
        for e in entries:
            if e["status"] != "permit":
                continue
            approved = {s["point"] for s in e["spans"]}
            for s in e["spans"]:
                for a in range(s["start"], s["start"] + s["regs"]):
                    now = point_at(new_profile, a)
                    kind = "unmapped" if now is None else ("ok" if now in approved else "wrong_quantity")
                    findings.append({"role": role, "task": e["task"], "address": a,
                                     "approved_point": s["point"], "now_resolves_to": now, "finding": kind})
    return findings


def diff(before, after, profile_before, profile_after):
    """Change verifier: moved, retired, unsupported, decoder change, and meaning changes needing operator review."""
    out = []
    for role in sorted(set(before) | set(after)):
        old = {e["task"]: e for e in before.get(role, [])}
        new = {e["task"]: e for e in after.get(role, [])}
        for task_id in sorted(set(old) | set(new)):
            b, a = old.get(task_id), new.get(task_id)
            bs = [(s["start"], s["regs"]) for s in b["spans"]] if b else []
            if a is None or a["status"] != "permit":
                out.append({"role": role, "task": task_id,
                            "change": a["status"] if a else "retired", "retire": bs,
                            "grant": [], "action": "withdraw permission pending a valid task mapping"})
                continue
            current = [(s["start"], s["regs"]) for s in a["spans"]]
            pa = profile_after["points"][a["point"]]
            pb = profile_before["points"].get(b.get("point")) if b else None
            decoder = pb is None or (pb["type"], pb.get("sf")) != (pa["type"], pa.get("sf"))
            review = pb is None or (pb["semantic"], pb["unit"]) != (pa["semantic"], pa["unit"])
            change = "moved"
            if b is None or b["status"] != "permit":
                change = "added"
            elif bs == current and b["unit_id"] == a["unit_id"] and not decoder and not review:
                change = "unchanged"
            out.append({"role": role, "task": task_id, "change": change,
                        "retire": bs, "grant": current,
                        "unit_before": b.get("unit_id") if b else None, "unit_after": a["unit_id"],
                        "decoder_change": decoder, "semantic_review": review})
    return out
