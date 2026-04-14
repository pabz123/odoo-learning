# Exercise 06 - Capstone (Topics 1-7 Integration)

## Goal

Integrate everything learned so far into one mini-module.

## Build

Module name: `library_training`

You must include:

1. clean module structure and manifest
2. models with broad field coverage
3. relationships between core models
4. CRUD and ORM helper methods
5. computed/onchange/constrains methods
6. groups + ACL + record rules
7. basic views/menus for books and borrowings

## Required models

1. `library.author`
2. `library.book`
3. `library.borrowing`

## Required behavior

1. Borrowing creation should prevent double active borrowing for same book
2. Due-date logic should be automatic and validated
3. Overdue cron method should update states
4. Book availability should be computed from borrowing records
5. Security should clearly separate normal users and managers

## Required files (minimum)

```text
library_training/
  __init__.py
  __manifest__.py
  models/__init__.py
  models/library_author.py
  models/library_book.py
  models/library_borrowing.py
  security/library_security.xml
  security/ir.model.access.csv
  views/library_book_views.xml
  views/library_borrowing_views.xml
  views/library_menus.xml
```

## Self-review checklist

- model names and relation fields are consistent
- all XML IDs are valid
- ACL rows match model external IDs
- rule domains use valid fields
- no syntax errors
- methods support multi-record where needed

## Submission format

Send in 3 parts:

1. Python models
2. Security files
3. Manifest + views/menus

I will then grade:

- Architecture (20)
- Field/model quality (20)
- ORM/decorator usage (20)
- Security correctness (25)
- Code quality and consistency (15)
