# Paper 42: matching blocked by missing inputs

The supplied CSV exists, but papers/42_*.pdf resolved to no file and observation_registry/paper_42.json does not exist.

Input resolution failed before prepare_inputs.py could be invoked; no supplied PDF could be selected. The task input-resolution check returned setup status 2.

Actual diagnostic:

```text
Input resolution failed: expected one supplied PDF matching papers/42_*.pdf; found 0. Required registry observation_registry/paper_42.json is also missing.
```

Alignment validation: not applicable because the required input set could not be prepared. No alignment JSON, observation assignments or success-shaped result was created. Inputs were preserved. This is an input/setup failure, not evidence that the paper has no observations or no matching records.
