# Documentation Setup

This document describes the MkDocs Material documentation setup for texer.

## What Was Created

### Configuration Files

- **mkdocs.yml** - MkDocs configuration with Material theme
- **pyproject.toml** - Added `[project.optional-dependencies]` section with `docs` extras
- **.gitignore** - Added `site/` directory for build output

### Documentation Structure

```
docs/
├── index.md                          # Home page with quick examples
├── javascripts/
│   └── mathjax.js                    # MathJax configuration for LaTeX rendering
├── getting-started/
│   ├── installation.md               # Installation guide
│   ├── mental-model.md               # How texer works conceptually
│   └── core-concepts.md              # Deep dive into specs and evaluation
├── tables/
│   ├── basic.md                      # Basic table creation
│   ├── data-driven.md                # Using specs for dynamic tables
│   ├── formatting.md                 # Cell formatting (placeholder)
│   └── advanced.md                   # MultiColumn, MultiRow (placeholder)
├── plots/
│   ├── basic.md                      # Basic plot creation
│   ├── data-driven.md                # Using specs for dynamic plots (placeholder)
│   ├── multiple-series.md            # Multiple data series (placeholder)
│   ├── groupplots.md                 # Subplot grids (placeholder)
│   └── advanced.md                   # Advanced options (placeholder)
├── specs/
│   ├── overview.md                   # Specs overview (placeholder)
│   ├── ref.md                        # Ref spec details (placeholder)
│   ├── iter.md                       # Iter spec details (placeholder)
│   ├── format.md                     # Format spec details (placeholder)
│   ├── cond.md                       # Cond spec details (placeholder)
│   └── raw.md                        # Raw spec details (placeholder)
├── compilation/
│   ├── saving.md                     # Saving to files (placeholder)
│   └── pdf.md                        # PDF compilation (placeholder)
└── api/
    ├── tables.md                     # Auto-generated API docs for tables
    ├── plots.md                      # Auto-generated API docs for plots
    ├── specs.md                      # Auto-generated API docs for specs
    └── utils.md                      # Auto-generated API docs for utils
```

### README Changes

- **README.md** - Simplified to focus on quick start and link to full docs
- **README.old.md** - Backup of original comprehensive README

## Building the Documentation

### Install Dependencies

```bash
pip install -e ".[docs]"
```

### Build Static Site

```bash
mkdocs build
```

Output will be in `site/` directory.

### Serve Locally

```bash
mkdocs serve
```

Then open http://127.0.0.1:8000

### Deploy to GitHub Pages

```bash
mkdocs gh-deploy
```

This will build and push to the `gh-pages` branch.

## Features Enabled

- **Material Design** theme
- **Dark/Light mode** toggle
- **Syntax highlighting** with copy button
- **Code annotations**
- **Tabbed content** (see examples in index.md)
- **Admonitions** (notes, warnings, tips)
- **MathJax** for LaTeX math rendering
- **mkdocstrings** for auto-generated API documentation
- **Search** functionality
- **Navigation tabs** and sections

## Next Steps

### Expand Placeholder Pages

Many documentation pages are placeholders. You can expand them by:

1. Copying relevant sections from `README.old.md`
2. Breaking them into logical subsections
3. Adding more examples and use cases

### API Documentation

The API reference pages use mkdocstrings to auto-generate documentation from docstrings. To improve them:

1. Add comprehensive docstrings to your Python code
2. Use Google-style docstrings (configured in mkdocs.yml)
3. Add type hints (already present in the code)

### Customize Theme

Edit `mkdocs.yml` to customize:

- Colors (`theme.palette.primary` and `theme.palette.accent`)
- Logo and favicon (`theme.logo` and `theme.favicon`)
- Social links (`extra.social`)
- Repository URL (already configured)

### GitHub Pages

To deploy to GitHub Pages:

1. Update the `repo_url` in mkdocs.yml with your actual repository URL
2. Run `mkdocs gh-deploy`
3. Enable GitHub Pages in repository settings (should auto-enable for gh-pages branch)
4. Update the README.md documentation link with your actual docs URL

## Maintenance

- Keep documentation in sync with code changes
- Update examples when adding new features
- Add new pages to `nav` section in mkdocs.yml
- Review and update placeholders periodically
