#!/usr/bin/env bash
# shellcheck disable=SC2034
# Provider switching recipe for Claude Code
# Usage: bake call s=claude d=models

source "$(dirname "${BASH_SOURCE[0]}")/../personality.sh"

find_project_root() {
    local current="$PWD"
    while [[ "$current" != "/" ]]; do
        if [[ -d "$current/.makery" ]]; then
            echo "$current"
            return 0
        fi
        current=$(dirname "$current")
    done
    return 1
}

# Core directories
PROJECT_ROOT=$(find_project_root)
STATION_DIR="$(dirname "${BASH_SOURCE[0]}")/../.."
PANTRY_DIR="$STATION_DIR/workbench/pantry"

# Normalize paths
STATION_DIR="$(cd "$STATION_DIR" && pwd)"
PANTRY_DIR="$STATION_DIR/workbench/pantry"

# Custom roots (optional overrides)
CLAUDE_DIR="${CLAUDE_DIR:-${PROJECT_ROOT}/.claude}"
SETTINGS_FILE="$CLAUDE_DIR/settings.local.json"
CACHE_FILE="$CLAUDE_DIR/.openrouter-models-cache.json"
CACHE_TTL=3600

fetch_openrouter_models() {
  if [ -z "${OPENROUTER_API_KEY:-}" ]; then
    SAY "Error: OPENROUTER_API_KEY is not set"
    SAY "Please run: export OPENROUTER_API_KEY=your-key"
    return 1
  fi

  rtk proxy curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" \
    "https://openrouter.ai/api/v1/models?free=true" 2>/dev/null || return 1
}

get_models_list() {
  local now current_time cache_time

  now=$(date +%s)

  if [ -f "$CACHE_FILE" ]; then
    cache_time=$(jq -r '.timestamp' "$CACHE_FILE" 2>/dev/null || echo 0)
    if [ $((now - cache_time)) -lt $CACHE_TTL ]; then
      jq -r '.data | map(select(((.pricing.prompt // "0") == "0" and (.pricing.completion // "0") == "0") and ((.name | ascii_downcase | contains("reasoning")) or (.description | ascii_downcase | contains("reasoning"))))) | sort_by(-.created, -.context_length) | .[0:15]' "$CACHE_FILE" 2>/dev/null && return 0
    fi
  fi

  local models
  models=$(fetch_openrouter_models) || return 1

  echo "$models" | jq "{timestamp: $(date +%s), data: .data}" > "$CACHE_FILE"
  echo "$models" | jq -r '.data | map(select(((.pricing.prompt // "0") == "0" and (.pricing.completion // "0") == "0") and ((.name | ascii_downcase | contains("reasoning")) or (.description | ascii_downcase | contains("reasoning"))))) | sort_by(-.created, -.context_length) | .[0:15]'
}

display_openrouter_menu() {
  local models count choice selected_model

  SAY "Fetching available OpenRouter free models..." >&2
  models=$(get_models_list) || {
    SAY "Warning: Could not fetch models from OpenRouter" >&2
    return 1
  }

  if [ -z "$models" ] || [ "$models" = "null" ]; then
    SAY "No free models available" >&2
    return 1
  fi

  SAY "Choose an OpenRouter free model:" >&2
  count=$(echo "$models" | jq 'length')

  echo "$models" | jq -r 'to_entries | .[] | "\(.key + 1)) \(.value.name | ltrimstr("Anthropic ") | ltrimstr("OpenAI ") | ltrimstr("Google ") | ltrimstr("DeepSeek: ") | ltrimstr("xAI: ")) (ctx: \(.value.context_length/1000|round)k, $\(((.value.pricing.prompt // "0") | tonumber) * 1000000 | round)/M input, $\(((.value.pricing.completion // "0") | tonumber) * 1000000 | round)/M output)"' | while IFS= read -r line; do
    echo "  $line" >&2
  done
  echo "" >&2

  read -r -p "Choice [1-$count]: " choice </dev/tty

  if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt "$count" ]; then
    SAY "Invalid choice: $choice" >&2
    return 1
  fi

  selected_model=$(echo "$models" | jq -r ".[$((choice - 1))].id")
  echo "$selected_model"
}

merge_settings() {
  local new_settings="$1"
  local tmp_file
  tmp_file=$(mktemp)
  if [ -f "$SETTINGS_FILE" ]; then
    jq -n --argjson new "$new_settings" 'input * $new' "$SETTINGS_FILE" > "$tmp_file" && mv "$tmp_file" "$SETTINGS_FILE"
  else
    echo "$new_settings" > "$tmp_file" && mv "$tmp_file" "$SETTINGS_FILE"
  fi
}

reset_to_native_auth() {
  local tmp_file
  [ -f "$SETTINGS_FILE" ] || return 0
  tmp_file=$(mktemp)
  jq 'del(.model, .effortLevel, .env.ANTHROPIC_BASE_URL, .env.ANTHROPIC_AUTH_TOKEN, .env.ANTHROPIC_API_KEY)
      | if (.env // {} | length) == 0 then del(.env) else . end' \
    "$SETTINGS_FILE" > "$tmp_file" && mv "$tmp_file" "$SETTINGS_FILE"
}

set_openrouter_model() {
  local model_id="$1"

  merge_settings "{\"model\":\"$model_id\",\"effortLevel\":\"medium\",\"env\":{\"ANTHROPIC_BASE_URL\":\"https://openrouter.ai/api/\",\"ANTHROPIC_AUTH_TOKEN\":\"$OPENROUTER_API_KEY\",\"ANTHROPIC_API_KEY\":\"\"}}"
}

get_indent_level() {
  local line="$1"
  local trimmed="${line##[[:space:]]*}"
  echo $((${#line} - ${#trimmed}))
}

is_leaf() {
  local path="$1"
  local -a parts
  IFS='.' read -ra parts <<<"${path#.}"
  local target_depth=${#parts[@]}
  local target_key=""
  [ $target_depth -gt 0 ] && target_key="${parts[$((target_depth - 1))]}"

  awk -v target_key="$target_key" -v target_depth="$target_depth" '
    /^[[:space:]]*#/ || !/: / { next }
    {
      indent = match($0, /[^ ]/) - 1
      depth = indent / 2
      if (depth == target_depth - 1 && $0 ~ target_key ": ") {
        found = 1
        exit
      }
    }
    END { exit found ? 0 : 1 }
  ' "$PANTRY_DIR/models.yaml"
}

get_keys_at_path() {
  local path="$1"
  local -a parts
  IFS='.' read -ra parts <<<"${path#.}"
  local target_depth=${#parts[@]}
  local target_key=""

  if [ -z "$path" ]; then
    target_depth=0
  else
    target_key="${parts[$((target_depth - 1))]}"
  fi

  awk -v target_depth="$target_depth" -v target_key="$target_key" -v path="$path" '
    /^[[:space:]]*#/ || /^[[:space:]]*$/ { next }
    {
      indent = match($0, /[^ ]/) - 1
      depth = indent / 2
      key = $0
      sub(/^[[:space:]]*/, "", key)
      sub(/:.*$/, "", key)

      if (path == "") {
        if (depth == 0) print key
      } else if (found && depth == target_depth) {
        print key
      } else if (depth == target_depth - 1 && key == target_key) {
        found = 1
      } else if (found && depth < target_depth) {
        found = 0
      }
    }
  ' "$PANTRY_DIR/models.yaml"
}

get_value_at_path() {
  local path="$1"
  local -a parts
  IFS='.' read -ra parts <<<"${path#.}"
  local target_depth=${#parts[@]}
  local target_key="${parts[$((target_depth - 1))]}"

  awk -v target_depth="$target_depth" -v target_key="$target_key" '
    /^[[:space:]]*#/ || !/: / { next }
    {
      indent = match($0, /[^ ]/) - 1
      depth = indent / 2
      key = $0
      sub(/^[[:space:]]*/, "", key)
      sub(/: .*$/, "", key)

      if (depth == target_depth - 1 && key == target_key) {
        value = $0
        gsub(/^[^"]*"/, "", value)
        gsub(/"[^"]*$/, "", value)
        print value
        exit 0
      }
    }
  ' "$PANTRY_DIR/models.yaml"
}

recursive_menu() {
  local path="$1"
  local offset="${2:-0}"
  local keys items_count choice display_count
  local -a items option_map

  keys=$(get_keys_at_path "$path")
  if [ -z "$keys" ]; then
    SAY "Error: No models found at path: $path" >&2
    return 1
  fi

  mapfile -t items <<<"$keys"
  items_count=${#items[@]}

  display_count=$((offset + 10))
  if [ $display_count -gt $items_count ]; then
    display_count=$items_count
  fi

  local menu_index=1

  if [ -n "$path" ]; then
    SAY "" >&2
    SAY "Path: $path" >&2
  fi

  for ((i = offset; i < display_count; i++)); do
    local key="${items[$i]}"
    local full_path
    if [ -z "$path" ]; then
      full_path=".$key"
    else
      full_path="$path.$key"
    fi

    if is_leaf "$full_path"; then
      local val
      val=$(get_value_at_path "$full_path")
      echo "  $menu_index) $key ($val)" >&2
      option_map+=("leaf:$full_path")
    else
      echo "  $menu_index) $key >" >&2
      option_map+=("branch:$full_path")
    fi
    ((menu_index++))
  done

  if [ $display_count -lt $items_count ]; then
    echo "  $menu_index) More..." >&2
    option_map+=("more:$((offset + 10))")
    ((menu_index++))
  fi

  echo "  0) Back" >&2
  echo "" >&2

  if [ -t 0 ]; then
    read -r -p "Choice [0-$((menu_index - 1))]: " choice </dev/tty
  else
    read -r -p "Choice [0-$((menu_index - 1))]: " choice
  fi

  if [ "$choice" = "0" ]; then
    return 1
  fi

  if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -ge $menu_index ]; then
    SAY "Invalid choice: $choice" >&2
    return 1
  fi

  local option="${option_map[$((choice - 1))]}"
  local option_type="${option%:*}"
  local option_value="${option#*:}"

  if [ "$option_type" = "leaf" ]; then
    get_value_at_path "$option_value"
  elif [ "$option_type" = "branch" ]; then
    recursive_menu "$option_value"
  elif [ "$option_type" = "more" ]; then
    recursive_menu "$path" "$option_value"
  fi
}

display_yaml_menu() {
  recursive_menu ""
}

SAY "Choose your model:"
echo "  1) Claude Pro/Max login (native auth)"
echo "  2) OpenRouter (free models)"
echo "  3) OpenRouter (from YAML)"
echo ""

read -p "Choice [1-3]: " choice

case "$choice" in
  1)
    reset_to_native_auth
    SAY "Switched to Claude Pro/Max login (native auth)"
    ;;
  2)
    model=$(display_openrouter_menu) || {
      SAY "Error fetching models. Enter model ID manually (e.g., meta-llama/llama-3.2-3b-instruct:free):"
      read -p "Model ID: " model
      if [ -z "$model" ]; then
        SAY "No model provided. Exiting."
        exit 1
      fi
    }

    if [ -z "${OPENROUTER_API_KEY:-}" ]; then
      SAY "Error: OPENROUTER_API_KEY is not set"
      SAY "Please run: export OPENROUTER_API_KEY=your-key"
      exit 1
    fi

    set_openrouter_model "$model"
    SAY "Switched to OpenRouter ($model)"
    ;;
  3)
    if [ ! -f "$PANTRY_DIR/models.yaml" ]; then
      SAY "Error: models.yaml not found at $PANTRY_DIR/models.yaml"
      exit 1
    fi

    if [ -z "${OPENROUTER_API_KEY:-}" ]; then
      SAY "Error: OPENROUTER_API_KEY is not set"
      SAY "Please run: export OPENROUTER_API_KEY=your-key"
      exit 1
    fi

    model=$(display_yaml_menu) || {
      SAY "No model selected. Exiting."
      exit 1
    }

    set_openrouter_model "$model"
    SAY "Switched to OpenRouter ($model)"
    ;;
  *)
    SAY "Invalid choice: $choice"
    exit 1
    ;;
esac

SAY "Settings written to $SETTINGS_FILE"
