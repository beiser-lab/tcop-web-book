#!/bin/sh
# Pandoc-only preview of the book (no Quarto needed). Output: _preview/
# Quarto renders the same .qmd files with `quarto render` once it is installed.
set -e
cd "$(dirname "$0")/.."
rm -rf _preview && mkdir -p _preview/pulmonary
cp -R pulmonary/figures _preview/pulmonary/
cp styles.css preview-tools/preview.css _preview/
NAV='<nav class="book"><strong>TCOP web-book (preview)</strong><a href="ROOTindex.html">About</a><a href="ROOTpulmonary/statics.html">Respiratory Statics</a></nav>'
build() { # src out root
  printf '%s' "$NAV" | sed "s#ROOT#$3#g" > _preview/nav.html
  pandoc -f markdown "$1" -o "$2" --standalone --toc --toc-depth=2 --mathjax \
    --lua-filter=preview-tools/quarto-lite.lua --citeproc --csl=numbered.csl --bibliography=references.bib \
    --resource-path=.:pulmonary --css="$3styles.css" --css="$3preview.css" \
    --include-before-body=_preview/nav.html --metadata link-citations=true
}
build index.qmd _preview/index.html ""
build pulmonary/statics.qmd _preview/pulmonary/statics.html "../"
rm _preview/nav.html
echo "built _preview/"
