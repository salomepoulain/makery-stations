# station-name/menu.mk
# Standalone Makefile. Works with: cd .makery/kitchen/stations/<name> && make <recipe>

# Recipes defined below are run via: bake call s=<station> d=<recipe>
# (first, fresh, burnt are managed by the Head Chef)

# Compute station directory when included from main menu.mk
STATION_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

menu::
	@bash -c 'source "$(STATION_DIR)cook/personality.sh" && STARTER "$$COOK_NAME'"'"'s Menu" && \
		ITEM "shady" "Stash this project'"'"'s .vault into __stash__" && \
		ITEM "perma" "Merge this project'"'"'s .vault into the permanent cross-project vault" && \
		ITEM "permanent" "Replace this project'"'"'s .vault with a live link to the permanent vault" && \
		ITEM "decouple" "Undo permanent: relink .vault to this project'"'"'s own stash" && \
		ITEM "undo" "Undo the most recent perma merge (files only, not a permanent link)" && \
		LINE'

# Add your recipes below:

shady:
	@bash $(STATION_DIR)cook/skills/shady.sh

perma:
	@bash $(STATION_DIR)cook/skills/perma.sh

permanent:
	@bash $(STATION_DIR)cook/skills/permanent.sh

decouple:
	@bash $(STATION_DIR)cook/skills/decouple.sh

undo:
	@bash $(STATION_DIR)cook/skills/undo.sh
