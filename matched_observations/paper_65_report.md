# Paper 65: required inputs missing

No supplied PDF matches `papers/65_*.pdf`, and `observation_registry/paper_65.json` is missing. The paper-specific CRA CSV exists, but this is not a complete input set.

Input resolution failed before `prepare_inputs.py` could be invoked; no supplied PDF could be selected. The task input-resolution check returned setup status 2.

Actual diagnostic:

```text
Input resolution failed: expected one supplied PDF matching papers/65_*.pdf; found 0. Required registry observation_registry/paper_65.json is also missing.
```

Alignment validation: not applicable because the required inputs could not be prepared. No alignment JSON or observation assignments were created. This setup failure is not evidence that the paper has no observations or matching records. All supplied files were preserved.
