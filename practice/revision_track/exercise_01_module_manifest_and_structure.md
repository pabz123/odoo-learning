# Exercise 01 - Module Manifest and Structure

## Goal

Practice Topics 1-2 by creating a clean Odoo module skeleton with correct load order.

## Task

Create a new custom module named `library_training` inside your own solution area:

- `my_solutions/library_training/`

Required structure:

```text
library_training/
  __init__.py
  __manifest__.py
  models/
    __init__.py
    library_book.py
  security/
    ir.model.access.csv
    library_security.xml
  views/
    library_book_views.xml
    library_menus.xml
```

## Manifest requirements

In `__manifest__.py`, include:

- `name`, `version`, `summary`, `depends`, `data`, `installable`, `application`
- `depends`: at least `base`, `mail`
- Correct data order (security before views, menus last)

Expected order pattern:

1. `security/*.xml`
2. `security/ir.model.access.csv`
3. `views/*_views.xml`
4. `views/*_menus.xml`

## Validation checklist

- Manifest is valid Python dict
- No missing commas / quotes
- Security files are loaded before UI files
- Menu file is loaded last

## Deliverable

Send:

1. Your module tree
2. `__manifest__.py`
3. Any questions you had while wiring load order
