#!/usr/bin/env bash
# Change le niveau de contexte métier donné à l'agent (pour la démo).
# Usage : ./scripts/set_context.sh 0|1|2
set -euo pipefail
cd "$(dirname "$0")/.."
level="${1:?Usage : ./scripts/set_context.sh 0|1|2}"
source="demo/rules/level_${level}.md"
[[ -f "$source" ]] || { echo "Niveau inconnu : $level (0, 1 ou 2)"; exit 1; }
cp "$source" context/business_rules.md
echo "Contexte métier → niveau ${level}. Contenu de context/business_rules.md :"
echo "-----"
cat context/business_rules.md
