// Compatibility for asciidoctor-jupyter 0.7.0 with Asciidoctor.js 2.2.6.
// Preserve description-list children, including code cells, in source order.
const BaseConverter = require('asciidoctor-jupyter')

class CourseNotebookConverter extends BaseConverter {
  // Asciidoctor's Ruby bridge copies own prototype methods, not inherited ones.
  mergeAdjacentMarkdownCells (...args) {
    return super.mergeAdjacentMarkdownCells(...args)
  }

  convert (node, transform) {
    const name = transform || node.getNodeName()
    // Opt-in resolution for reference chapters exported outside Antora's HTML pipeline.
    const doc = node.getDocument()
    const site = doc.getAttribute('jupyter-site-url')
    if (name === 'inline_anchor' && node.getType() === 'bibref') {
      return `[${node.getText() || node.getTarget()}]`
    }
    if (site && name === 'inline_anchor' && node.getType() === 'xref') {
      const target = node.getTarget()
      const component = doc.getAttribute('jupyter-component')
      const page = doc.getAttribute('jupyter-page-path')
      let url
      if (target.startsWith('#')) {
        url = `${site}/${component}/${page}${target}`
      } else {
        const match = target.match(/^(?:([^:]+)::)?(?:(attachment)\$)?([^:]+)$/)
        if (!match) throw new Error(`Unsupported notebook resource reference: ${target}`)
        const [, selectedComponent, family, relative] = match
        // The Jupyter backend has already rewritten page suffixes to .ipynb.
        // Reference notes need web-page links, including chapters without notebooks.
        const destination = family ? relative : relative.replace(/\.(?:adoc|ipynb)(?=#|$)/, '.html')
        url = `${site}/${selectedComponent || component}/${family ? '_attachments/' : ''}${destination}`
      }
      return `[${node.getText() || target}](${url})`
    }
    if (name === 'dlist') {
      const cells = []
      for (const [terms, description] of node.getItems()) {
        const text = typeof description?.getText === 'function' ? description.getText() : ''
        cells.push({
          cell_type: 'markdown', metadata: {},
          source: [`\n${terms.map(term => `**${term.getText()}**`).join(', ')}\n\n${text || ''}\n\n`],
        })
        if (typeof description?.getBlocks === 'function') {
          for (const block of description.getBlocks()) cells.push(...block.convert())
        }
      }
      return cells
    }
    const result = super.convert(node, transform)
    if ((name === 'document' || name === 'embedded') && this.ignoredNodes.length) {
      throw new Error(`Notebook export would omit content: ${[...new Set(this.ignoredNodes.map(n => n.name))].join(', ')}`)
    }
    return result
  }
}

module.exports = CourseNotebookConverter
module.exports.register = function () {
  require('@asciidoctor/core')().ConverterFactory.register(CourseNotebookConverter, ['jupyter'])
}
