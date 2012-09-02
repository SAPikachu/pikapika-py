PIE_BASE=../../../../submodules/PIE/

all: PIE.htc

PIE.htc: ${PIE_BASE}build/PIE.htc
	cp $< $@

${PIE_BASE}build/PIE.htc: ${PIE_BASE}build.xml ${PIE_BASE}sources/*
	cd ${PIE_BASE}; ant

