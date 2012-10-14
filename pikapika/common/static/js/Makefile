all: build-amd-modules optimized-scripts.js

build-amd-modules:
	./build-amd-modules.py

optimized-scripts.js:
	node ../../../../submodules/r.js/dist/r.js -o app.build.js

.PHONY: build-amd-modules optimized-scripts.js

