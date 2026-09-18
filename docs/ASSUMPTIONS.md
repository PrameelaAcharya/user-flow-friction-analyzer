# Assumptions

## Session data

The project uses a synthetic session log representing one user completing a common web shopping flow.

The sample contains 20 steps covering login, product search, product navigation, cart, and checkout.

## Friction detection

The analyzer uses rule-based signals from the session log.

### Failed attempt

A step is considered a failed attempt when its outcome is recorded as `failed`.

### Repeated action

A repeated action is detected when the user performs the same action on the same target and screen immediately after a failed attempt.

### Long pause

A step lasting 15 seconds or more is treated as a possible long pause.

### Backtracking

Backtracking is identified from repeated movement between the same screens in opposite directions.

## Severity

Severity is calculated from the combined friction score.

The score is used as a prioritization signal and does not prove the user's emotional state.

## AI

The AI component is used only for summarizing detected friction points and their likely user impact.

The AI does not determine whether an event is a friction point.