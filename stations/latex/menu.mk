# station-name/menu.mk
# Standalone Makefile. Works with: cd .makery/kitchen/stations/<name> && make <recipe>

# Recipes defined below are run via: bake call s=<station> d=<recipe>
# (first, fresh, burnt are managed by the Head Chef)

# Compute station directory when included from main menu.mk
STATION_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

menu::
	@bash -c 'source "$(STATION_DIR)cook/personality.sh" && STARTER "$$COOK_NAME'"'"'s Menu" && \
		ITEM "<<report>>" "<<turns main.tex into main.pdf from report/ folder>>" && \
		LINE'

# Add your recipes below:

# models: Switch between Anthropic and OpenRouter providers
report:
	@bash $(STATION_DIR)cook/skills/report.sh
