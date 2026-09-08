# station-name/menu.mk
# Standalone Makefile. Works with: cd .makery/kitchen/stations/<name> && make <recipe>

# Recipes defined below are run via: bake call s=<station> d=<recipe>
# (first, fresh, burnt are managed by the Head Chef)

# Compute station directory when included from main menu.mk
STATION_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

menu::
	@bash -c 'source "$(STATION_DIR)cook/personality.sh" && STARTER "$$COOK_NAME'"'"'s Menu" && \
		ITEM "models" "Switch between Anthropic and OpenRouter providers" && \
		ITEM "prompts" "Manage prompt templates and persona configurations" && \
		ITEM "skills" "Handle skill configurations and permissions" && \
		ITEM "commit-yolo" "Fast automated commit (free tier by default)" && \
		ITEM "commit-duo" "Interactive commit with Claude review (free tier by default)" && \
		ITEM "auto" "Toggle the blockReadsOutsideWorkingDirectories prompt on/off" && \
		LINE'

# Add your recipes below:

# models: Switch between Anthropic and OpenRouter providers
models:
	@bash $(STATION_DIR)cook/recipes/models.sh

# skills: Handle skill configurations
skills:
	@bash $(STATION_DIR)cook/recipes/skills.sh

# commit-yolo: Fast automated commit (free tier by default)
commit-yolo:
	@bash $(STATION_DIR)cook/recipes/commit-yolo.sh $(filter-out commit-yolo call,$(MAKECMDGOALS))

# commit-duo: Interactive commit with Claude review (free tier by default)
commit-duo:
	@bash $(STATION_DIR)cook/recipes/commit-duo.sh $(filter-out commit-duo call,$(MAKECMDGOALS))

# auto: Toggle blockReadsOutsideWorkingDirectories on/off
auto:
	@bash $(STATION_DIR)cook/recipes/auto.sh
