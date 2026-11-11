# Research review and novelty search
Date searched: 11 November 2026.

## Candidate contribution
Verify preservation of workflow-specific permissions across an inverter profile change, including movement of register locations, changes in decoding, unsupported dependencies, unit IDs and changes in measurement scope. Evaluate the correctness of withdrawal and re-grant decisions against an independently specified answer key.

Novelty remains provisional. The implemented example is a feasibility demonstration.

## Search record
Public web engines were queried with:
- "SunSpec" "replacement" "policy" authorization
- "ForestFirewalls" "change" policy device
- "Secure SunSpec Modbus" "roles" "configurable"
- SunSpec inverter replacement profile change authorization policy generation register permissions
- ForestFirewalls device replacement policy maintenance SunSpec semantic mapping

Inspected official specification sections, the ForestFirewalls technical report, public reference mappings and an additional closely related patent disclosure. This is a bounded search. It cannot prove absence throughout the literature.

| Comparator | Already covered | Remaining question in this review |
|---|---|---|
| [Secure SunSpec Modbus](https://sunspec.org/wp-content/uploads/2009/03/Secure-SunSpec-Modbus-Specification_final.pdf), §5.3 | Configurable supported-point rights, required role maps and additional roles. | No replacement-time benchmark of workflow preservation was identified in the inspected specification. Configurability already enables manual maintenance. |
| [SunSpec RBAC reference](https://github.com/sunspec/rbac) | Point-level role permissions and map generation. | Compare the proposed maintenance method against this material, including a manually configured narrow role. |
| [ForestFirewalls](https://arxiv.org/pdf/1902.05689), system overview and evaluation | Abstract policy generation, topology independence and checks before and after deployment. | Its demonstrated abstraction is network policy. The reviewed material did not establish SunSpec measurement-scope and decoder migration. Generic policy maintenance is already covered. |
| [US12225133B2 disclosure](https://patents.google.com/patent/US12225133B2/en), figure 5 and associated description | Translates a user rule through SunSpec Modbus into an access-control representation. | This overlaps the broad rule-translation proposal. The replacement-specific comparison remains to be established through further literature and implementation study. |

The patent is included as technical prior-art evidence. This review provides no legal assessment.

## Evaluation still required
The uploaded package contains two profiles, two roles and two tasks. It therefore does not meet the proposed larger evaluation condition.

Use at least three documented profiles or configurations and several roles/tasks. Explicitly distinguish a configuration variant from a third manufacturer. Compare the generated policy with a manual SunSpec-aware policy using the same role map, task documents and enforcement engine. Seed stale spans, excess range access, wrong unit IDs, missing scale factors, semantic mismatches and unsupported counters. Ask an independent reviewer to write and freeze the answer key before running the generator. Record false permits, false denials, unsupported-task detection, required edits and comparable maintenance time.

Tests in this repository establish implementation consistency. They do not establish novelty, independent correctness or a measured advantage over the manual baseline. Take this example and the documented overlap to the supervisor before committing to a final contribution.
