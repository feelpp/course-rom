'use strict'

const fs = require('node:fs')
const path = require('node:path')

const [siteDirectory, siteUrl] = process.argv.slice(2)
if (!siteDirectory || !siteUrl) {
  throw new Error('Usage: node scripts/verify-search-index.cjs <site-directory> <site-url>')
}

const indexPath = path.join(siteDirectory, 'search-index.json')
const index = JSON.parse(fs.readFileSync(indexPath, 'utf8'))
const expectedPrefix = new URL(siteUrl).pathname.replace(/\/?$/, '/')

if (!Array.isArray(index.documents) || index.documents.length === 0) {
  throw new Error('Search index contains no documents')
}
for (const document of index.documents) {
  if (!document.title || !document.content || !document.url.startsWith(expectedPrefix)) {
    throw new Error(`Invalid search index document: ${JSON.stringify(document)}`)
  }
}
console.log(`Verified ${index.documents.length} search documents under ${expectedPrefix}`)