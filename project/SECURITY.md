# Security Policy — The Drake Display

## Scope

The Drake Display is a data-visualization and modeling project that consumes public astronomical catalogs and produces an interactive model. Its security surface is modest, but as the engine grows (data pipelines, a web application, potential user-supplied scenarios) real concerns apply: dependency vulnerabilities, unsafe handling of downloaded data, and, in later phases, anything touching a hosted deployment.

## Reporting a vulnerability

If you discover a security issue, please report it **privately** rather than opening a public issue. Contact the maintainer directly at <drake-project@hecarrieswater.com> .

Please include: a description of the issue, steps to reproduce, the affected component or version, and any suggested remediation.

## What to expect

- Acknowledgement of your report within a reasonable window.
- A good-faith assessment and, where warranted, a fix.
- Credit for the discovery if you wish (and if the report is valid).

## Supported versions

During the design and pre-release phases, only the current state of the `main` branch is supported. A formal support policy will accompany the first tagged release.

## Good-neighbor practices the project follows

- Pinned, reviewed dependencies.
- No execution of untrusted downloaded data as code.
- Least-privilege handling of any credentials (none are required to consume the public catalogs used today).
