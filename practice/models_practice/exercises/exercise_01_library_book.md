# Exercise 1: Library Book Model

## 📋 Objective
Create a simple model to manage books in a library system.

## 📝 Requirements

Create a model called `library.book` with the following:

### Model Attributes:
- Technical name: `library.book`
- Description: "Library Book"
- Default ordering: By title (alphabetically)
- Display name field: `title`

### Fields to Create:

1. **title** (Char)
   - Label: "Book Title"
   - Required: Yes
   - Should be indexed for fast searching

2. **author** (Char)
   - Label: "Author"
   - Required: Yes

3. **isbn** (Char)
   - Label: "ISBN"
   - Size: 13 characters
   - Must be unique (SQL constraint)

4. **pages** (Integer)
   - Label: "Number of Pages"
   - Must be positive (SQL constraint)

5. **publish_date** (Date)
   - Label: "Publication Date"

6. **available** (Boolean)
   - Label: "Available"
   - Default: True

7. **description** (Text)
   - Label: "Description"

8. **language** (Selection)
   - Label: "Language"
   - Options: English, French, Spanish, German
   - Default: English

### SQL Constraints:
1. ISBN must be unique
2. Pages must be greater than 0

### Python Constraint:
- Title must be at least 3 characters long

## 💡 Hints

- Use `models.Model` (permanent storage)
- Import: `from odoo import models, fields, api`
- For ValidationError: `from odoo.exceptions import ValidationError`
- SQL constraints format: `[('name', 'SQL', 'Error message')]`
- Python constraints use `@api.constrains('field_name')`

## 📁 Where to Write

Create your solution in: `my_solutions/exercise_01_library_book.py`

Good luck! 🚀
