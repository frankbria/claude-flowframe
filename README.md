# Claude FlowFrame

[![Follow on X](https://img.shields.io/twitter/follow/FrankBria18044?style=social)](https://x.com/FrankBria18044)

**Minimal agentic orchestration framework for Claude Code workflows**

Claude FlowFrame is a lightweight, focused tool that provides just the essential orchestration capabilities needed for automated AI workflows. Unlike full-featured platforms, FlowFrame does only what's necessary: memory management, swarm coordination, and lifecycle hooks.

## Features

- 🧠 **Simple Memory System**: Key-value storage with namespaces for workflow state
- 🐝 **Swarm Orchestration**: Coordinate multiple AI agents via Claude Code
- 🪝 **Lifecycle Hooks**: Pre/post-task callbacks for automation
- 📦 **Zero Dependencies**: Minimal footprint, maximum portability
- 🎯 **MCP-First Design**: Leverages Claude Code's Task tool via MCP servers

## What FlowFrame Is NOT

- ❌ No vector databases or semantic search
- ❌ No web UI or dashboard
- ❌ No 100+ tools or enterprise features
- ❌ No custom agent implementations
- ❌ No neural training or learning systems

FlowFrame delegates all agent work to Claude Code and provides only the glue layer for orchestration.

## Installation

### From Source

```bash
cd ~/projects/claude-flowframe
pip install -e .
```

### Using uv (recommended)

```bash
cd ~/projects/claude-flowframe
uv pip install -e .
```

## Quick Start

### Memory Operations

```bash
# Store workflow state
claude-flowframe memory store "workflow/issue-123/prompt" "Build REST API" \
  --namespace workflow \
  --metadata '{"issue_id": "123", "timestamp": "2025-12-26"}'

# Query stored values
claude-flowframe memory query "workflow/issue-123/prompt" --namespace workflow

# List all keys in namespace
claude-flowframe memory list --namespace workflow

# Delete a key
claude-flowframe memory delete "workflow/issue-123/prompt" --namespace workflow
```

### Swarm Orchestration

```bash
# Initialize a swarm
claude-flowframe swarm init \
  --topology hierarchical \
  --max-agents 5 \
  --namespace "workflow/issue-123"

# Spawn agents to execute a task
claude-flowframe swarm spawn \
  --objective "Implement user authentication API" \
  --strategy development \
  --agents "coder,tester,reviewer" \
  --namespace "workflow/issue-123"

# Check swarm status
claude-flowframe swarm status --namespace "workflow/issue-123" --json
```

### Lifecycle Hooks

```bash
# Execute pre-task hook
claude-flowframe hooks pre-task \
  --description "Implement: issue-123" \
  --session-id "workflow/issue-123"

# Execute post-task hook
claude-flowframe hooks post-task \
  --task-id "workflow/issue-123" \
  --export-metrics

# Execute session-end hook
claude-flowframe hooks session-end \
  --session-id "workflow/issue-123" \
  --export-metrics
```

## Custom Hook Scripts

You can add custom bash scripts to execute during lifecycle events:

```bash
# Create hooks directory
mkdir -p ~/.claude-flowframe/hooks

# Add pre-task hook (runs before task execution)
cat > ~/.claude-flowframe/hooks/pre-task.sh << 'EOF'
#!/bin/bash
echo "Pre-task hook: $CLAUDE_FLOWFRAME_SESSION_ID"
# Add custom logic here (linting, checks, etc.)
EOF

# Add post-task hook (runs after task completion)
cat > ~/.claude-flowframe/hooks/post-task.sh << 'EOF'
#!/bin/bash
echo "Post-task hook: $CLAUDE_FLOWFRAME_SESSION_ID"
# Add custom logic here (formatting, metrics, etc.)
EOF

# Make scripts executable
chmod +x ~/.claude-flowframe/hooks/*.sh
```

## Architecture

```
~/.claude-flowframe/
├── memory/
│   └── {namespace}/
│       └── {key}.json
├── swarms/
│   └── {namespace}/
│       ├── config.json
│       ├── status.json
│       └── task_*.txt
└── hooks/
    ├── pre-task.sh
    ├── post-task.sh
    ├── session-end.sh
    └── logs/
```

## Integration with Workflows

FlowFrame is designed to integrate with automated workflows like the traycer-workflow.sh script:

```bash
#!/bin/bash
# Example workflow integration

ISSUE_ID="cf-123"
NAMESPACE="workflow/${ISSUE_ID}"

# Phase 1: Store workflow context
claude-flowframe memory store "${NAMESPACE}/prompt" "$TRAYCER_PROMPT" \
  --namespace workflow

# Phase 2: Initialize and spawn swarm
claude-flowframe swarm init --topology mesh --max-agents 5 --namespace "$NAMESPACE"
claude-flowframe hooks pre-task --description "Implement: ${ISSUE_ID}" --session-id "$NAMESPACE"

claude-flowframe swarm spawn \
  --objective "$TRAYCER_PROMPT" \
  --strategy development \
  --agents "coder,tester,reviewer" \
  --namespace "$NAMESPACE"

# Phase 3: Check status
while true; do
  STATUS=$(claude-flowframe swarm status --namespace "$NAMESPACE" --json | jq -r '.status')
  [[ "$STATUS" == "completed" ]] && break
  sleep 10
done

# Phase 4: Cleanup
claude-flowframe hooks session-end --session-id "$NAMESPACE" --export-metrics
```

## Development

### Setup Development Environment

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Or with uv
uv pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
pytest --cov=claude_flowframe tests/
```

### Code Quality

```bash
# Format and lint
ruff check src/
ruff format src/

# Type checking
mypy src/
```

## Comparison with Claude-Flow

| Feature | Claude-Flow | Claude FlowFrame |
|---------|-------------|------------------|
| Memory System | ✅ Vector DB + Semantic Search | ✅ Simple JSON key-value |
| Agent Orchestration | ✅ 64 specialized agents | ✅ MCP Task delegation only |
| Web UI | ✅ Full dashboard | ❌ CLI only |
| MCP Tools | ✅ 100+ tools | ✅ Uses existing MCP servers |
| Hooks System | ✅ Advanced workflows | ✅ Basic lifecycle callbacks |
| Enterprise Features | ✅ Full suite | ❌ Minimal by design |
| Learning/Training | ✅ Neural networks | ❌ None |
| Installation Size | ~500MB | ~5MB |

## License

MIT

## Contributing

Contributions welcome! Keep it minimal - the goal is to do less, not more.

1. Fork the repository
2. Create a feature branch
3. Make your changes (remember: keep it simple!)
4. Submit a pull request

## Credits

Inspired by [claude-flow](https://github.com/ruvnet/claude-flow) by Reuven Cohen, but stripped down to the essentials for workflow orchestration.
