"""Run offline: python3 verify.py"""
import copy
from policy import load, generate, decide, audit_stale, diff

tasks = load("tasks.json")
key = load("answer_key.json")
profiles = {"fronius": load("profiles/fronius.json"), "solaredge": load("profiles/solaredge.json")}
policies = {n: generate(p, tasks) for n, p in profiles.items()}

# 0. Evidence status of every point a permission rests on
print("Evidence behind each generated permission:")
for n, pol in policies.items():
    for role, entries in pol.items():
        for e in entries:
            if e["status"] == "permit":
                print(f"  {n}/{role}/{e['task']}: {e['evidence']}")
            else:
                print(f"  {n}/{role}/{e['task']}: UNSUPPORTED ({profiles[n]['points'][tasks['tasks'][e['task']]['point']]['evidence']['status']})")
        for e in entries:
            assert "unverified" not in e.get("evidence", []), "a permission rests on an unverified point"

# 1. Generated policy against the answer key
for r in key["requests"]:
    got, why = decide(policies[r["profile"]], r["role"], r["unit"], r["fc"], r["start"], r["count"])
    assert got == r["expect"], f"{r} -> {got} ({why})"
print(f"{len(key['requests'])} request decisions match the answer key.")

# 2. Stale-rule counterexample: the Fronius policy, unchanged, on the SolarEdge device
stale = policies["fronius"]
ok, _ = decide(stale, "dashboard", 1, 3, 40091, 2)
assert ok, "stale rule should still permit the old read"
findings = audit_stale(stale, profiles["solaredge"])
dash = [f for f in findings if f["role"] == "dashboard"]
assert all(f["finding"] == "wrong_quantity" for f in dash)
print("Stale dashboard rule: read still permitted, but SolarEdge maps the addresses to:")
for f in dash:
    print(f"  {f['address']}: approved {f['approved_point']}, address maps to {f['now_resolves_to']}")
for f in findings:
    if f["role"] == "analyst":
        assert f["finding"] in ("unmapped", "wrong_quantity")
print("Stale analyst rule: addresses unmapped on the new profile. The counter is unsupported there anyway.")

# 3. Change verifier
changes = diff(policies["fronius"], policies["solaredge"], profiles["fronius"], profiles["solaredge"])
for exp in key["diff"]:
    row = next(c for c in changes if c["role"] == exp["role"] and c["task"] == exp["task"])
    for k, v in exp.items():
        assert row[k] == v, (row, k, v)
print("Change verifier output:")
for c in changes:
    print(" ", c)

# 4. Meaning check: if SolarEdge did support the counter, 'Synergy unit 0' is not 'MPPT input 1'
variant = copy.deepcopy(profiles["solaredge"])
variant["points"]["DCWH_1"]["supported"] = True
variant["points"]["DCWH_1"]["sf"] = None
pol_v = generate(variant, tasks)
row = next(c for c in diff(policies["fronius"], pol_v, profiles["fronius"], variant) if c["task"] == "input1_lifetime_dc_energy")
assert row["change"] == "review_required"
assert not decide(pol_v, "analyst", 1, 3, 40143, 2)[0]
print("Hypothetical check passed: a supported counter would still need operator review of its meaning.")
# Targeted regressions found during the review.
bad_tasks = copy.deepcopy(tasks)
bad_tasks["tasks"]["total_ac_power"]["operation"] = "write"
assert not decide(generate(profiles["solaredge"], bad_tasks), "dashboard", 1, 3, 40083, 2)[0]
missing_sf = copy.deepcopy(profiles["solaredge"])
del missing_sf["points"]["W_SF"]
assert generate(missing_sf, tasks)["dashboard"][0]["status"] == "unsupported"
for start, count in [(-1, 2), (40083, 0), (40083, 126), (65535, 2), (40083, 1.5)]:
    assert not decide(policies["solaredge"], "dashboard", 1, 3, start, count)[0]
assert not decide(policies["fronius"], "dashboard", 1, 3, 40091, 1)[0]
assert diff(policies["fronius"], {}, profiles["fronius"], profiles["solaredge"])[0]["change"] == "retired"
assert diff({}, policies["solaredge"], profiles["fronius"], profiles["solaredge"])[1]["change"] == "added"
print("15 answer-key decisions plus stale-policy, change and regression checks passed.")
