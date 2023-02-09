DEMO_SCRIPTS := $(shell find scripts/ -name "*.txt" | sed 's/\.txt//g' | sed 's/scripts\/\///g' | sort )

list:
	@echo $(DEMO_SCRIPTS)

test:
	for value in $(DEMO_SCRIPTS); do \
		python3 seismicRayTracer.py $$value ; \
	done