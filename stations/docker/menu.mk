# station-name/menu.mk
# Standalone Makefile. Works with: cd .makery/kitchen/stations/<name> && make <recipe>

# Recipes defined below are run via: bake call s=<station> d=<recipe>
# (first, fresh, burnt are managed by the Head Chef)

# Compute station directory when included from main menu.mk
STATION_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

menu::
	@bash -c 'source "$(STATION_DIR)cook/personality.sh" && STARTER "$$COOK_NAME'"'"'s Menu" && \
		ITEM "build" "Build the dev container image via .docker/compose.yaml" && \
		ITEM "rebuild" "Force a clean no-cache rebuild of the dev image" && \
		ITEM "run" "Run the dev container and open zsh at /workspace" && \
		ITEM "clean" "Stop compose services and remove project image/container" && \
		LINE'

# Add your recipes below:

build:
	@bash $(STATION_DIR)cook/skills/build.sh

rebuild:
	@bash $(STATION_DIR)cook/skills/rebuild.sh

run:
	@bash $(STATION_DIR)cook/skills/shell.sh

shell: run

clean:
	@bash $(STATION_DIR)cook/skills/clean.sh
