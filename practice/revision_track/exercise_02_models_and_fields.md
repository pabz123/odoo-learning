# Exercise 02 - Models, Fields, and Relationships

## Goal

Practice Topics 2-3 deeply: model design, field types, indexing, and relations.

## Task

Create these models inside `my_solutions/library_training/models/`:

1. `library.author`
2. `library.category`
3. `library.book`
4. `library.borrowing`

## Minimum field coverage

You must use all of these across the models:

- `Char`, `Text`, `Integer`, `Float`, `Monetary`, `Boolean`
- `Date`, `Datetime`, `Selection`, `Binary`
- `Many2one`, `One2many`, `Many2many`

## Required modeling rules

### `library.author`

- `name` (required, indexed)
- `bio` (Text)
- `book_ids` (One2many to `library.book`)

### `library.category`

- `name` (required)
- `description` (Text)
- `book_ids` (Many2many to `library.book`)

### `library.book`

- `name` (required, indexed)
- `isbn` (required, unique SQL constraint, indexed)
- `author_id` (Many2one, required, indexed)
- `category_ids` (Many2many)
- `page_count` (Integer, positive SQL constraint)
- `price` (Monetary + `currency_id`)
- `publish_date` (Date)
- `cover_image` (Binary)
- `state` (Selection: draft/available/borrowed/lost)
- `active` (Boolean, default True)
- `borrowing_ids` (One2many to `library.borrowing`)

### `library.borrowing`

- `book_id` (Many2one, required, indexed)
- `borrower_id` (Many2one to `res.partner`, required, indexed)
- `borrow_date` (Date, default today)
- `due_date` (Date, required)
- `returned_at` (Datetime)
- `fine_amount` (Float or Monetary)
- `state` (Selection: active/returned/overdue, default active)

## Required constraints

1. ISBN unique (`_sql_constraints`)
2. Page count > 0 (`_sql_constraints`)
3. Python constraint: `due_date >= borrow_date`

## Deliverable

Send:

1. Full model code
2. Your `_sql_constraints`
3. One short note: where you used indexing and why
