# station-name/menu.mk
# Standalone Makefile. Works with: cd .makery/kitchen/stations/<name> && make <recipe>

# Recipes defined below are run via: bake call s=<station> d=<recipe>
# (first, fresh, burnt are managed by the Head Chef)

# Compute station directory when included from main menu.mk
STATION_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

menu::
	@bash -c 'source "$(STATION_DIR)cook/personality.sh" && STARTER "$$COOK_NAME'"'"'s Menu" && \
		ITEM "repo" "Create private GitHub repo, set remote, push initial commit" && \
		ITEM "match" "Find a repo named like this folder under your account, clone/pull it in" && \
		ITEM "public" "Make this repo public (asks for confirmation)" && \
		ITEM "private" "Make this repo private (asks for confirmation)" && \
		ITEM "gitignore" "Refresh .gitignore from all stations'"'"' contraband" && \
		LINE'

# Add your recipes below:

repo:
	@bash $(STATION_DIR)cook/skills/repo.sh

match:
	@bash $(STATION_DIR)cook/skills/match.sh

public:
	@bash $(STATION_DIR)cook/skills/public.sh

private:
	@bash $(STATION_DIR)cook/skills/private.sh

gitignore:
	@bash $(STATION_DIR)cook/skills/gitignore.sh
