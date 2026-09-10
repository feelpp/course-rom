const test = require('node:test')
const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const asciidoctor = require('@asciidoctor/core')()
const { generateNotebook } = require('@feelpp/antora-extensions/src/jupyter.js')
require('../notebook-converter.cjs').register()

const convert = source => JSON.parse(asciidoctor.convert(source, { backend: 'jupyter', standalone: true }))

test('description lists preserve text, math, multiple terms and nested code in order', () => {
  const notebook = convert(`= Example
:stem: latexmath

State::
Unknown:: The vector stem:[u].
+
[source,python]
----
x = 2
print(x)
----
+
After the code.

Output:: A scalar.

Empty::
`)
  assert.equal(notebook.cells.filter(cell => cell.cell_type === 'code').length, 1)
  assert.match(notebook.cells[0].source.join(''), /\*\*State\*\*.*\*\*Unknown\*\*/s)
  assert.match(notebook.cells[0].source.join(''), /\$u\$/)
  assert.equal(notebook.cells[1].cell_type, 'code')
  assert.match(notebook.cells[1].source.join(''), /x = 2\nprint\(x\)/)
  assert.match(notebook.cells.slice(2).flatMap(cell => cell.source).join(''), /After the code.*Output.*A scalar.*Empty/s)
})

test('official exporter reports unsupported content with the page resource ID', () => {
  const page = { contents: Buffer.from('= Unsupported\n\naudio::sound.ogg[]\n'),
    src: { component: 'course-rom', version: '', module: 'ROOT', relative: 'bad.adoc' } }
  assert.throws(() => generateNotebook(page), /course-rom.*bad.adoc.*Notebook export would omit content: audio/)
})

for (const { source: relative } of require('../../teaching/course-release.json').labs) {
test(`official exporter preserves notebook metadata for ${relative}`, () => {
  const contents = fs.readFileSync(path.join(__dirname, '../../docs/modules/ROOT/pages', relative))
  const notebook = JSON.parse(generateNotebook({ contents, pub: { url: "/course-rom/labs/session01-digital-twins.html" },
    src: { component: 'course-rom', version: '', module: 'ROOT', relative },
  }))
  assert.equal(notebook.nbformat, 4)
  assert.ok(notebook.metadata.kernelspec.display_name)
  assert.ok(notebook.cells.some(cell => cell.cell_type === 'code'))
  assert.ok(notebook.cells.every(cell => cell.cell_type !== 'code' || cell.outputs.length === 0))
})
}

test('downloaded thermal notebooks link to published notes and data', () => {
  for (const relative of ['labs/session13-thermal-fin.adoc', 'labs/session14-integrated-study.adoc']) {
    const contents = fs.readFileSync(path.join(__dirname, '../../docs/modules/ROOT/pages', relative))
    const notebook = JSON.parse(generateNotebook({ contents, pub: { url: `/course-rom/${relative.replace('.adoc', '.html')}` },
      src: { component: 'course-rom', version: '', module: 'ROOT', relative } }))
    const markdown = notebook.cells.filter(cell => cell.cell_type === 'markdown')
      .map(cell => Array.isArray(cell.source) ? cell.source.join('') : cell.source).join('\n')
    assert.match(markdown, /\]\(https:\/\/feelpp.github.io\/course-rom\/rom\/applications\/thermal-fin.html\)/)
    assert.match(markdown, /\]\(https:\/\/feelpp.github.io\/course-rom\/course-rom\/_attachments\/data\/thermal-fin-coarse.npz\)/)
    assert.doesNotMatch(markdown, /\]\((?:rom::|setup.ipynb|\.\.\/data\/)/)
  }
})
