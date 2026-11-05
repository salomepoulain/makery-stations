# shell/menu.mk
# Standalone Makefile. Works with: cd .makery/kitchen/stations/<name> && make <recipe>

# Recipes defined below are run via: bake call s=<station> d=<recipe>
# (first, fresh, burnt are managed by the Head Chef)

# Compute station directory when included from main menu.mk
STATION_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

# No recipes: the shell config goes in your home, which bake doesn't touch.
# Hiring shows the two commands. Without an ITEM line, bake shows no menu.
menu::
	@true
