# station-name/menu.mk
# Standalone Makefile. Works with: cd .makery/kitchen/stations/<name> && make <recipe>

# Recipes defined below are run via: bake call s=<station> d=<recipe>
# (first, fresh, burnt are managed by the Head Chef)

# Compute station directory when included from main menu.mk
STATION_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

menu::
	@bash -c 'source "$(STATION_DIR)cook/personality.sh" && STARTER "$$COOK_NAME'"'"'s Menu" && \
		ITEM "setup" "Re-run setup: chezmoi, oh-my-zsh, powerlevel10k, apply dotfiles (idempotent)" && \
		LINE'

# Add your recipes below:

# setup: re-run the same idempotent setup hired.sh runs on first hire
setup:
	@bash $(STATION_DIR)cook/contract/hired.sh
