---
name: adk-developer
description: Expert guidance for developing, testing, and deploying agents using the Google Agent Development Kit (ADK). Use for tasks involving agent creation, orchestration, tools, memory, mcp, session, evaluation, caching, compression, optimization, callback, and deployment.
---

# ADK Developer Skill

This skill provides expert procedural guidance and reference materials for developing agents with the Google Agent Development Kit (ADK).

## Quick Navigation

*   [**ADK Cheatsheet**](references/adk-cheatsheet.md): Code snippets for Agents, Tools, Workflow, and Configuration.
*   [**Development Workflow**](references/development-workflow.md): The end-to-end process from Spec -> Build -> Eval -> Deploy.
*   [**Operational Guidelines**](references/operational-guidelines.md): **CRITICAL** rules for code modification and safety.

## Core Mandates for ADK Development

1.  **Follow the Spec**: Always check `conductor/product.md`, `conductor/workflow.md`, or relevant plans in `plan/` or `tracks/` first. These are the source of truth.
2.  **Preserve Code**: Adhere strictly to the [Operational Guidelines](references/operational-guidelines.md). Never rewrite code unnecessarily.
3.  **Start Small with Evals**: When iterating, start with 1-2 evaluation cases. Don't run the full suite until core cases pass.

## Common Tasks

### Creating a New Agent

See [ADK Cheatsheet - Agent Definitions](references/adk-cheatsheet.md#2-agent-definitions-llmagent).

### Adding Tools

See [ADK Cheatsheet - Tools](references/adk-cheatsheet.md#7-tools-the-agents-capabilities). Remember to use `FunctionTool` for custom functions and check import paths carefully.

### Running Evaluations

See [Development Workflow - Phase 3](references/development-workflow.md#phase-3-the-evaluation-loop-main-iteration-phase).

```bash
make eval
```

### Deployment

See [Development Workflow - Phase 6](references/development-workflow.md#phase-6-production-deployment---choose-your-path).

## Troubleshooting

If you encounter errors:
1.  Check [Operational Guidelines - Troubleshooting](references/operational-guidelines.md#troubleshooting).
2.  Verify `GOOGLE_CLOUD_LOCATION` matches your model's availability.
3.  Ensure you are using `uv run` for Python commands.
