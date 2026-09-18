# Limitations

## Synthetic data

The current demonstration uses synthetic session data rather than production user sessions.

## Rule-based detection

The friction detector depends on predefined rules and thresholds.

Real user behavior can be more complex than these rules capture.

## Long pauses

A long pause does not necessarily mean confusion. A user may simply have been interrupted or distracted.

## Backtracking

Navigation patterns can indicate difficulty, but returning to a previous page can also be intentional.

## Severity

Severity is a prioritization mechanism based on detected signals. It should not be interpreted as a direct measurement of user frustration.

## AI summary

The AI summary depends on the detected evidence supplied to the model. It cannot identify friction that the rule-based detector did not detect.

## Scale

The prototype is designed for a bounded session log and is not optimized for large-scale production analytics.

## Generalization

The current rules were designed for the demonstration session and may require adjustment for different products or user flows.