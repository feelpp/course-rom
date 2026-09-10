// Antora 3.x passes extension configuration only when register.length > 0.
// The rc.5 submodule's default argument makes its register.length === 0.
const jupyter = require('@feelpp/antora-extensions/src/jupyter.js')
require('./notebook-converter.cjs').register()
module.exports.register = function ({ config }) {
  jupyter.register.call(this, { config })
}
