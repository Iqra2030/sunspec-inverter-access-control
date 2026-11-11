# Threat model
## Assets and trust
Protect the intended scope of application access and the meaning of approved measurements. Trust the operator's task descriptions, profile inventory, semantic labels and policy engine. Assume the gateway authenticates applications and binds their roles to an endpoint-specific policy. The offline function receives this role as an argument. It implements no authentication, TCP proxy, deployment transaction or discovery.

## Adversary and checked decisions
Assume an application account is compromised and submits requests through the enforcement path. The policy checker rejects reads outside the approved spans, reads targeting a different unit ID, all writes, unapproved function codes and malformed address/count arguments. A request spanning both approved and unapproved addresses is denied in full. Generation withholds unsupported tasks and unresolved measurement meanings.

A stale or mistaken configuration is another source of risk. The audit reports addresses whose point names changed or are absent from the partial replacement inventory. The change report gives the old and new spans and flags decoding changes. A flag requires an operator or deployment system to act.

## Boundaries of the result
A malicious endpoint can falsify allowed telemetry. A bypass path can evade the gateway. Incorrect task descriptions, forged profile data, compromised gateway credentials, denial of service and dynamic changes after commissioning remain outside the checked model. Classification of authorised control actions by physical safety is outside the read-only example.

A deployed system must bind policy to endpoint identity and profile version, invalidate stale policy during replacement, authenticate clients, and install the new policy atomically. It must coordinate client decoding and scale-factor refresh. The current script demonstrates decisions before and after replacement under trusted inputs. It does not demonstrate these deployment guarantees.

## Counterexample
A compromised dashboard retains its old read permission at 40091–40092 after replacement. The range now identifies different fields. The current SolarEdge policy rejects it. This illustrates stale authorisation scope even where the replacement's fields are unsupported. It establishes neither a physical attack impact nor an information leak from valid PF values.
