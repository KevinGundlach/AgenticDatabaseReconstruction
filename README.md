# Agentic Database Reconstruction

This project explores reproducible, agentic methods for reconstructing structured
scientific databases from academic literature. The goal is to build a system that
can read source papers, extract experimental records, normalize the reported data,
and compare the reconstructed database with an expert-curated reference.

The current research corpus covers corrosion-resistant alloys and uses the Citrine
corrosion database as its initial benchmark. That domain is a test case for the
broader database-reconstruction system rather than the boundary of the project.

See [`project_spec.md`](project_spec.md) for the current research requirements and
[`overview.txt`](overview.txt) for the project background.

## Project environment

The repository is configured as a non-package uv project. It does not currently
publish a Python library or command-line application.

```powershell
uv sync
```

Specialized, self-contained agent skills live under `.agents/skills/`. For
example, `classify-pitting-plots` screens MinerU chart output for directly plotted
pitting-potential data as one component of the current corrosion benchmark.

