#!/usr/bin/env bash
# Installs the reporting-agent skill and its subagents into a target
# project. Only ever touches the reporting-agent files themselves — it
# never deletes or overwrites anything else already in the target.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-.}"

mkdir -p "$TARGET/.opencode/skills" "$TARGET/.opencode/agents" "$TARGET/.omp/agents"

rm -rf "$TARGET/.opencode/skills/reporting-agent"
cp -r "$SCRIPT_DIR/.opencode/skills/reporting-agent" "$TARGET/.opencode/skills/reporting-agent"

cp "$SCRIPT_DIR/.opencode/agents/reporting-writer.md" "$TARGET/.opencode/agents/reporting-writer.md"
cp "$SCRIPT_DIR/.opencode/agents/reporting-editor.md" "$TARGET/.opencode/agents/reporting-editor.md"
cp "$SCRIPT_DIR/.omp/agents/reporting-writer.md" "$TARGET/.omp/agents/reporting-writer.md"
cp "$SCRIPT_DIR/.omp/agents/reporting-editor.md" "$TARGET/.omp/agents/reporting-editor.md"

RESOLVED="$(cd "$TARGET" && pwd)"
echo "Installed reporting-agent into: $RESOLVED"
echo "  .opencode/skills/reporting-agent/"
echo "  .opencode/agents/reporting-writer.md, reporting-editor.md"
echo "  .omp/agents/reporting-writer.md, reporting-editor.md"
