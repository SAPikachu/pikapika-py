#!/usr/bin/env python

import os
import json

RAW_BASE_DIR = "../../../../submodules/"

MODULE_EXPORTS = {
    "jquery": ["jQuery", "$"],
    "underscore": ["_"],
    "backbone": ["Backbone"],
}

MODULES = [
    {
        "name": "backbone",
        "raw_file": "backbone/backbone.js",
        "dependency": [
            "jquery",
            "underscore",
        ],
    },
    {
        "name": "underscore",
        "raw_file": "underscore/underscore.js",
        "dependency": [
        ],
    },
]

TEMPLATE = ("""
(function (factory) {

    if (typeof define === "function" && define.amd) {
        // AMD. Register as an anonymous module.
        define(["require"`dependency_names'], factory);
    } else {
        // Browser globals
        factory();
    }
}(function(require){

var real_factory = function() {

`raw_file'

};

if (require) {
    var imports = `imports';
    var export = "`export'";
    var context = {};
    for (var key in imports) {
        if (imports.hasOwnProperty(key)) {
            context[key] = require(imports[key]);
        }
    }
    real_factory.call(context);
    if (export !== "") {
        return context[export] || window[export];
    }
} else {
    real_factory();
}

}));
""".replace("{", "{{")
   .replace("}", "}}")
   .replace("`", "{")
   .replace("'", "}")
)

def build():
    for module in MODULES:
        with open(RAW_BASE_DIR + module["raw_file"], "r") as f:
            raw_file = f.read()

        dependency_names = "".join(
            [', "{}"'.format(x) for x in module["dependency"]]
        )
        export = MODULE_EXPORTS[module["name"]][0]
        imports = {}
        for dep in module["dependency"]:
            for import_name in MODULE_EXPORTS[dep]:
                imports[import_name] = dep

        with open(module["name"] + ".js", "w") as f:
            f.write(TEMPLATE.format(
                raw_file=raw_file,
                dependency_names=dependency_names,
                export=export,
                imports=json.dumps(imports),
            ))

if __name__ == "__main__":
    build()
