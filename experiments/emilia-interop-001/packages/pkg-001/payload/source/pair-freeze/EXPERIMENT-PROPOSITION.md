# WEXP × EMILIA positive/hostile pair — experiment proposition

Artifact: `WEXP-EMILIA-PAIR-FREEZE-001`  
Proposition authority: Founder work order  
Proposition status: fixed before WEXP expectation derivation

> The stronger result depends on the exact meter-observation-to-action CAID
> binding.

The controlled intervention is the removal of exactly the meter observation's
top-level `action_caid` member at JSON Pointer
`/emilia_input/observations/1/action_caid`. The meter observation is then
re-signed under the same pinned meter key so signature validity is not a
confound. No other semantic input, source pin, key, control domain, requirement,
operation identifier, nonce, facility identifier, effect, or time window may
change.

This proposition concerns the paired experiment. It does not declare that CAID
correlation is WEXP semantic support, WEXP target equality, or WEXP
arguments-hash identity. The WEXP effect of the intervention is derived
independently and frozen separately.
