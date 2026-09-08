#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
DIR=$(echo "$input" | jq -r '.workspace.current_dir')
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
DURATION_MS=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')

CYAN='\033[36m'; GREEN='\033[32m'; YELLOW='\033[33m'; RED='\033[31m'; GRAY='\033[90m'; WHITE='\033[37m'; ORANGE='\033[38;5;166m'; RESET='\033[0m'
SEP="${GRAY}|${RESET}"

# Pick bar color based on context usage
BAR_COLOR="$WHITE"

MINS=$((DURATION_MS / 60000)); SECS=$(((DURATION_MS % 60000) / 1000))

BRANCH=""
git -c core.fsmonitor=false rev-parse --git-dir > /dev/null 2>&1 && BRANCH=$(git -c core.fsmonitor=false branch --show-current 2>/dev/null)

make_bar() {
  local pct=$(printf '%.0f' "$1")
  local blocks="$2"
  local filled=$(( pct * blocks / 100 ))
  local bar=""
  local i
  for (( i=0; i<blocks; i++ )); do
    if [ "$i" -lt "$filled" ]; then
      bar="${bar}█"
    else
      bar="${bar}░"
    fi
  done
  echo "$bar"
}

# make_bar_with_pipe pct blocks pipe_block
# Renders a bar with a | at pipe_block boundary.
# Blocks before pipe are filled (█), pipe is |, blocks after are filled or empty.
make_bar_with_pipe() {
  local pct="${1%.*}"
  local blocks="$2"
  local pipe_block="$3"
  local filled=$(( (pct * blocks + 50) / 100 ))
  [ "$filled" -lt 1 ] && filled=1
  local bar=""
  local i
  for (( i=0; i<blocks; i++ )); do
    if [ "$i" -eq "$pipe_block" ]; then
      bar="${bar} "
    else
      if [ "$i" -lt "$filled" ]; then
        bar="${bar}█"
      else
        bar="${bar}░"
      fi
    fi
  done
  # If pipe_block equals blocks, append pipe at end
  if [ "$pipe_block" -ge "$blocks" ]; then
    bar="${bar} "
  fi
  echo "$bar"
}

# Format seconds-until-reset as Xd Yh or Xh Ym (time remaining)
fmt_reset() {
  local now; now=$(date +%s)
  local secs=$(( $1 - now ))
  [ "$secs" -le 0 ] && echo "now" && return
  local days=$(( secs / 86400 ))
  local hrs=$(( (secs % 86400) / 3600 ))
  local mins=$(( (secs % 3600) / 60 ))
  if [ "$days" -ge 1 ]; then
    echo "${days}d${hrs}h"
  else
    echo "${hrs}h${mins}m"
  fi
}

FIVE_PCT=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
FIVE_RESET=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
WEEK_PCT=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
WEEK_RESET=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')

COST_FMT=$(printf '$%.2f' "$COST")

# Build context bar with 10-block width to match rate limit bars
CTX_BAR=$(make_bar "$PCT" 15)

# Build the colored rate part for display (using actual bar values, not placeholder)
NOW=$(date +%s)
RATE_PART=""
if [ -n "$FIVE_PCT" ]; then
  FIVE_INT=$(printf '%.0f' "$FIVE_PCT")
  RESET_STR=""
  PIPE_BLOCK=9
  if [ -n "$FIVE_RESET" ]; then
    RESET_STR=" <$(fmt_reset "$FIVE_RESET")"
    FIVE_REMAINING_SECS=$(( FIVE_RESET - NOW ))
    [ "$FIVE_REMAINING_SECS" -lt 0 ] && FIVE_REMAINING_SECS=0
    # pipe_block = elapsed_secs / secs_per_block = (18000 - remaining) / 1800
    # e.g. 17m remaining: (18000-1020)/1800 = 9  (pipe near right = almost out of time)
    # e.g. 2h30m remaining: (18000-9000)/1800 = 5 (pipe in middle)
    FIVE_ELAPSED_SECS=$(( 18000 - FIVE_REMAINING_SECS ))
    [ "$FIVE_ELAPSED_SECS" -lt 0 ] && FIVE_ELAPSED_SECS=0
    PIPE_BLOCK=$(( FIVE_ELAPSED_SECS / 1200 ))
    [ "$PIPE_BLOCK" -le 0 ] && PIPE_BLOCK=1
    [ "$PIPE_BLOCK" -ge 14 ] && PIPE_BLOCK=13
  fi
  B=$(make_bar_with_pipe "$FIVE_PCT" 15 "$PIPE_BLOCK")
  RATE_PART=" ${SEP} ${GRAY}${B}${RESET} ${FIVE_INT}%${RESET_STR}"
fi
if [ -n "$WEEK_PCT" ]; then
  WEEK_INT=$(printf '%.0f' "$WEEK_PCT")
  RESET_STR=""
  PIPE_BLOCK=9
  if [ -n "$WEEK_RESET" ]; then
    RESET_STR=" <$(fmt_reset "$WEEK_RESET")"
    WEEK_REMAINING_SECS=$(( WEEK_RESET - NOW ))
    [ "$WEEK_REMAINING_SECS" -lt 0 ] && WEEK_REMAINING_SECS=0
    # pipe_block = elapsed_secs / secs_per_block = (604800 - remaining) / 60480
    # 7d = 604800s, 10 blocks -> each block = 60480s (16.8h)
    WEEK_ELAPSED_SECS=$(( 604800 - WEEK_REMAINING_SECS ))
    [ "$WEEK_ELAPSED_SECS" -lt 0 ] && WEEK_ELAPSED_SECS=0
    PIPE_BLOCK=$(( WEEK_ELAPSED_SECS / 40320 ))
    [ "$PIPE_BLOCK" -le 0 ] && PIPE_BLOCK=1
    [ "$PIPE_BLOCK" -ge 14 ] && PIPE_BLOCK=13
  fi
  B=$(make_bar_with_pipe "$WEEK_PCT" 15 "$PIPE_BLOCK")
  RATE_PART="${RATE_PART} ${SEP} ${GRAY}${B}${RESET} ${WEEK_INT}%${RESET_STR}"
fi

FOLDER="${DIR##*/}"
if [ -n "$BRANCH" ]; then
  echo -e "${ORANGE}${MODEL}${RESET} ${GRAY}-${RESET} ${ORANGE}${FOLDER}${RESET} ${GRAY}-${RESET} ${ORANGE}${BRANCH}${RESET}"
else
  echo -e "${ORANGE}${MODEL}${RESET} ${GRAY}-${RESET} ${ORANGE}${FOLDER}${RESET}"
fi
echo -e "${WHITE}${BAR_COLOR}${CTX_BAR}${RESET}${WHITE} ${PCT}%${RESET} ${SEP} ${WHITE}${COST_FMT}${RESET} ${SEP} ${WHITE}${MINS}m ${SECS}s${RATE_PART}${RESET}"
