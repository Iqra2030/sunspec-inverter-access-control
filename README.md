# Maintaining SunSpec read permissions after inverter replacement
Worked example · 10 November 2026

## Site decision

A dashboard may read total inverter AC active power in watts. A separate yield analyst may read lifetime DC energy for the first reported DC input in watt-hours. The operator approves only those measurements and their decoding prerequisites. The two applications cross the same logical conduit. This example assumes authenticated roles and a trusted, prevalidated profile inventory. Discovery belongs to commissioning, outside the application permissions.

Compare a three-phase Fronius Datamanager float configuration (113 plus 160) with a SolarEdge three-phase Synergy logging profile (103 plus 160). These are documented interface profiles. Physical interchangeability, a specific installed firmware, and real device behaviour have not been tested.

## Profile evidence and decisions

Addresses below are **zero-based protocol addresses**, inclusive. Subtract one from the Fronius table's printed register number. SolarEdge supplies both conventions. These are monitoring points only.

| Approved task | Before, Fronius | After, SolarEdge | Expected policy change |
|---|---|---|---|
| Dashboard reads total active power W | Printed 40092–40093 → 40091–40092, one float32 | 40083 is a signed value and 40084 its signed decimal scale factor. Watts = value × 10^scale. | Move the permission to 40083–40084 and change the decoder. Retire the former pair. |
| Yield analyst reads input 1 lifetime DC energy | Printed 40286–40287 → 40285–40286, acc32. Printed 40269 → 40268 supplies DCWH_SF. | The first repeated unit's DCWH at 40143–40144 is explicitly unsupported. The manual gives zero as the placeholder. | Return unsupported task and issue no permission for the analyst. A placeholder zero is not a measured zero. |

**Why an address-only policy fails.** On SolarEdge the old dashboard addresses 40091–40092 designate power factor and its scale. Reusing the Fronius rule leaves the desired power measurement inaccessible and permits a read of different fields. The presence of model 160 on both devices also fails to establish that the requested energy counter is supported. An aggregate inverter energy reading would change the unit of observation and cannot fulfil the analyst's task.

## Expected decisions for the replacement

| Role and request | Expected result | Reason |
|---|---|---|
| Dashboard reads 40083–40084 | Permit | Both registers are needed to decode watts. |
| Dashboard reads 40091–40092 | Deny | Stale permission. |
| Dashboard reads 40083–40085 | Deny whole request | The last register is outside the task. |
| Analyst requests input 1 lifetime energy | Report unsupported at policy generation | The profile explicitly declares the counter unavailable. |
| Analyst reads 40143–40144 or a former Fronius address | Deny | No active mapping fulfils the task. |
| Either application writes | Deny | Both approved tasks are read-only. |

Run `python3 verify.py` offline. The fixture checks expected decisions for both profiles, including the stale-rule counterexample. An illustrative SolarEdge raw value of 12345 at scale −1 decodes to 1234.5 W. Values are synthetic. The checks are author-prepared consistency tests. A later experiment needs an independent reviewer and a manual baseline to measure any advantage.

## Sources

1. [Fronius Datamanager operating instructions](https://manuals.fronius.com/html/4204102049/en-US.html), Common & Inverter Model and Multiple MPPT Inverter Extension Model.
2. [Fronius Datamanager float register table, mirrored manufacturer document](https://www.photovoltaikforum.com/core/attachment/103560-inverter-register-map-float-v1-0-with-symohybrid-model-124-pdf/), rows W, DCWH_SF and 1_DCWH. The table identifies the inverter family as 111–113 and the W type as float32.
3. [SolarEdge SunSpec Logging Technical Note, v3.2, June 2025](https://knowledge-center.solaredge.com/sites/kc/files/sunspec-implementation-technical-note.pdf), inverter model mapping and multiple-MPPT extension. Compare I_AC_Power, I_AC_Power_SF, I_AC_PF and the first DCWH row.
