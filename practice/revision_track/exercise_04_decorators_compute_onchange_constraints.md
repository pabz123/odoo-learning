# Exercise 04 - Decorators, Compute, Onchange, Constraints

## Goal

Practice Topic 5 with decorator-heavy, real behavior.

## Task

Implement these features in your models.

## Required computed fields (`@api.depends`)

### In `library.book`

1. `borrowing_count` (Integer, compute, store=True)
   - count borrowings linked to the book

2. `is_available` (Boolean, compute)
   - True if no `active` borrowing exists

3. `availability_label` (Selection or Char, compute, store=True)
   - `available` if `is_available`
   - `borrowed` otherwise

## Required onchange methods (`@api.onchange`)

### In `library.borrowing`

1. `@api.onchange('book_id')`
   - if selected book is not available, return warning

2. `@api.onchange('borrow_date')`
   - auto-set `due_date` to +14 days when empty

3. `@api.onchange('borrower_id')`
   - optional: enforce domain or warning for missing email

## Required constraints (`@api.constrains`)

1. `due_date` must be >= `borrow_date`
2. cannot create active borrowing if same book already has active borrowing

## Required model methods

1. `@api.model def _cron_archive_lost_books(self):`
   - archive books in state `lost` for more than 30 days

2. `@api.ondelete(at_uninstall=False)` on `library.book`
   - block deletion if borrowing history exists

## Deliverable

Send:

1. field definitions for computed fields
2. all decorator methods
3. brief note: `@api.depends` vs `@api.onchange` in your own words
