# Exercise 03 - CRUD, Recordsets, and Advanced ORM Methods

## Goal

Practice Topics 4 and 6 by writing practical methods that manipulate data efficiently.

## Task

In your `library.book` and `library.borrowing` models, implement the methods below.

## Methods to implement

### A) `library.book` methods

1. `@api.model def create_demo_books(self):`
   - create at least 3 books using one bulk `create([...])`
   - use realistic values

2. `def action_mark_lost(self):`
   - `self.ensure_one()`
   - set state to `lost` only if currently `borrowed`

3. `@api.model def get_books_by_category(self, category_name):`
   - use `search` + `filtered_domain`
   - return a recordset

4. `@api.model def get_top_5_expensive_books(self):`
   - use `search` + `sorted(..., reverse=True)` + slicing

### B) `library.borrowing` methods

1. `@api.model def cron_mark_overdue(self):`
   - find active borrowings where `due_date < today`
   - write state = `overdue`

2. `@api.model def get_overdue_partner_names(self):`
   - return partner names using `mapped`

3. `@api.model def get_overdue_grouped_by_partner(self):`
   - return grouped data using `grouped('borrower_id')`
   - output a Python dict like `{partner_name: count}`

4. `def action_return(self):`
   - supports multi-record `self`
   - set `state='returned'` and `returned_at=fields.Datetime.now()`

## Mandatory usage checklist

Your code must use all of these at least once:

- `search`, `create`, `write`
- `filtered` or `filtered_domain`
- `mapped`
- `sorted`
- `grouped`
- `ensure_one`

## Deliverable

Send the method implementations only (you can paste model snippets).
