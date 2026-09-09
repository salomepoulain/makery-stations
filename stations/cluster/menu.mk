# station-name/menu.mk
# Standalone Makefile. Works with: cd .makery/kitchen/stations/<name> && make <recipe>

# Recipes defined below are run via: bake call s=<station> d=<recipe>
# (first, fresh, burnt are managed by the Head Chef)

# Compute station directory when included from main menu.mk
STATION_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

menu::
	@bash -c 'source "$(STATION_DIR)cook/personality.sh" && STARTER "$$COOK_NAME'"'"'s Menu" && \
		ITEM "shell" "Install/update dotfiles and shell: chezmoi, oh-my-zsh, powerlevel10k (idempotent)" && \
		ITEM "sync [host]" "Continuously sync this project'"'"'s __sync__/ folder (drag-and-drop) with a remote host via Mutagen" && \
		ITEM "shady-sync [host]" "Continuously sync this project'"'"'s .shadow/ (everything bake shady stashed) with a remote host via Mutagen" && \
		LINE'

# Add your recipes below:

# shell: install/update dotfiles and shell environment
shell:
	@bash $(STATION_DIR)cook/recipes/shell.sh

# sync: continuous two-way __sync__/ sync with a remote host via Mutagen
sync:
	@bash $(STATION_DIR)cook/recipes/sync.sh $(filter-out sync call,$(MAKECMDGOALS))

# shady-sync: continuous two-way .shadow/ sync with a remote host via Mutagen
shady-sync:
	@bash $(STATION_DIR)cook/recipes/shady-sync.sh $(filter-out shady-sync call,$(MAKECMDGOALS))
