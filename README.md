# TCOP web-book

Source for the MEDC 30504 student web-book, published at
https://beiser-lab.github.io/tcop-web-book/ from the `gh-pages` branch. Only cleared
material goes here: our own text, figures drawn for the book, and openly licensed figures.
The 2018 course pack extract and the review files stay outside, in `Web-book/`.

## Layout

- `_quarto.yml`: book configuration (chapters, bibliography, theme)
- `index.qmd`: front page
- `cardiovascular/`, `muscle/`, `pulmonary/`: the 30 chapters; each folder's `figures/<chapter>/` holds generated SVGs (do not edit by hand)
- `references.bib` and `bib/`: bibliographies; every figure credit and cited claim points here
- `scripts/statics_model.py`: Python port of the Respiratory Mechanics Lab statics model (dist/model.js v24); keep in step with it
- `scripts/figs_<chapter>.py`: draws each chapter's figures (`figstyle.py` holds the shared style)
- `styles.css`: shared colors with the simulators
- `preview-tools/`: pandoc-only preview (no Quarto needed)

## Build

Figures:

    MPLCONFIGDIR=$TMPDIR python3 scripts/figs_<chapter>.py

Preview with pandoc (output in `_preview/`, served by the `web-book-preview` launch config on port 4180):

    sh preview-tools/build-preview.sh

Full book with Quarto:

    quarto render      # output in _book/, served by the `web-book-quarto` launch config on port 4181
    quarto preview

Inside Claude Code's sandbox, Quarto can't write its cache to ~/Library/Caches, so run it as
`HOME="$TMPDIR/qhome" quarto render` there. In your own terminal, plain `quarto render` works.

## Figure rules

- Curves are drawn from equations or the simulator models in the course palette
  (lung #a65e00, chest wall #155f83, respiratory system #800000, muscles #d22f1e).
- A figure that redraws a classic experiment or a textbook figure says "adapted from" in its
  caption and cites the original in `references.bib`. Redraws use our own layout, not a tracing.
- No lecturer names, student names or patient details in text, figures or captions.

## Publish

    quarto render
    # then push the contents of _book/ to the gh-pages branch (with a .nojekyll file)
