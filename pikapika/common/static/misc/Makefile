PIE_BASE=../../../../submodules/PIE/
PIE_SOURCE_NAME=PIE.htc

all: PIE.htc

PIE.htc: ${PIE_BASE}build/${PIE_SOURCE_NAME}
	cp $< $@

${PIE_BASE}build/${PIE_SOURCE_NAME}: ${PIE_BASE}build.xml ${PIE_BASE}sources/*
	cd ${PIE_BASE}; ant

