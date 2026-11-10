"""Offline policy fixture. Addresses use zero-based Modbus protocol notation."""

profiles = {
    "Fronius": {"watts": {40091, 40092}, "input_energy": {40285, 40286, 40268}},
    "SolarEdge": {"watts": {40083, 40084}, "input_energy": None},
}
tasks = {"dashboard": "watts", "analyst": "input_energy"}


def permits(profile, role, operation, start, count):
    task = tasks.get(role)
    allowed = profiles[profile].get(task)
    return bool(allowed and operation == "read" and count > 0
                and all(address in allowed for address in range(start, start + count)))


cases = [
    ("Fronius", "dashboard", "read", 40091, 2, True),
    ("Fronius", "analyst", "read", 40285, 2, True),
    ("Fronius", "analyst", "read", 40268, 1, True),
    ("SolarEdge", "dashboard", "read", 40083, 2, True),
    ("SolarEdge", "dashboard", "read", 40091, 2, False),
    ("SolarEdge", "dashboard", "read", 40083, 3, False),
    ("SolarEdge", "analyst", "read", 40143, 2, False),
    ("SolarEdge", "analyst", "read", 40285, 2, False),
    ("SolarEdge", "analyst", "read", 40083, 2, False),
    ("SolarEdge", "dashboard", "write", 40083, 1, False),
    ("SolarEdge", "analyst", "write", 40143, 1, False),
]
for profile, role, operation, start, count, expected in cases:
    if permits(profile, role, operation, start, count) != expected:
        raise SystemExit(f"Unexpected decision: {profile}, {role}, {operation}, {start}, {count}")
print(f"{len(cases)} expected access decisions verified.")
