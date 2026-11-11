# Maintaining SunSpec read permissions after inverter replacement
Worked example · Reviewed 11 November 2026

Run `python3 verify.py` with Python 3. The implementation uses the standard library.
The checks exercise an offline authorisation model. A trusted caller supplies the authenticated role and the intended device profile.

## Approved workflows

The dashboard reads total inverter AC active power in watts. The analyst reads lifetime DC energy of MPPT input 1 in watt-hours. Each task includes its intended meaning and units. Policies grant only FC03 reads, the configured unit ID, complete named points and their scale-factor dependencies. Rejecting partial multi-register points is an explicit local policy choice.

| Task | Fronius non-Hybrid Datamanager float | SolarEdge three-phase Synergy | Outcome |
|---|---|---|---|
| Total AC power | 40091–40092, float32 | 40083 value, 40084 scale factor | Retire the former span, grant the new pair, change decoder. |
| MPPT input 1 lifetime DC energy | 40285–40286 plus scale factor 40268 | Synergy unit 0 DCWH at 40143–40144 is unsupported | Withhold permission. Its measurement scope would also need review if support were introduced. |

All addresses are zero-based. The old Fronius power addresses map to SolarEdge PF and PF_SF. This demonstrates a stale permission's changed meaning. The SolarEdge rows have a split-phase support footnote, so the example makes no claim that a three-phase Synergy device returns meaningful power-factor values there.

## Evidence verified in this review

Fronius's official [map archive](https://www.fronius.com/QR-link/0006) was retrieved successfully. In `Inverter_Register_Map_Float_v1.0_with_SYMOHYBRID_MODEL_124.xlsx`, sheet `Complete Map`, rows 39, 183 and 192 specify W, DCWH_SF and 1_DCWH. Subtract one from printed register numbers. The DC energy rows explicitly exclude Hybrid inverters. SHA256 of this workbook is `993e43a66e4e5db27f148e8d46d5c2a1920fd5b375ddf6887c81d8956f4ea273`.

The official [SolarEdge note](https://knowledge-center.solaredge.com/sites/kc/files/sunspec-implementation-technical-note.pdf) now serves v3.3, October 2026. Rechecked power on printed p.17, power factor on p.19 and Synergy unit 0 on p.21. The addresses used by the example agree with v3. The counter description is “0 (not supported)”.

The [Fronius instructions](https://manuals.fronius.com/html/4204102049/en-US.html) document float/int+SF selection and the distinct unit ID for the meter. Device selection must include the endpoint as well as its unit ID in a future gateway. Current policies are scoped to a single selected endpoint.

## Review corrections

- Task operations are checked during generation. A write task cannot acquire a read grant.
- A supported field with a different meaning or units produces `review_required` and no permission.
- Missing or unsupported scale factors withhold the corresponding task permission.
- Request fields are checked for integer types, register bounds and the FC03 quantity limit.
- Changes are matched by role and task ID. Removed roles/tasks are retired and added tasks are reported.
- Unsupported results no longer skip the removal list.
- A partial profile's unmapped address means unknown to this inventory. It does not prove that the physical inverter has no register there.

The 15 supplied answer-key decisions pass, together with stale-rule, semantic-mismatch and targeted regression checks. The answer key remains author-prepared. No independent validation or physical-device experiment has occurred.

See [threat model](THREAT_MODEL.md) and [novelty search and evaluation requirements](RESEARCH_REVIEW.md).
