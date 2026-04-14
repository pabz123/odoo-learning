from odoo import fields, models


class LibraryAuthor(models.Model):
    _name = "library.author"
    _description = "Library Author"
    _order = "name"

    name = fields.Char(required=True, index=True)
    bio = fields.Text()
    active = fields.Boolean(default=True)
    book_ids = fields.One2many("library.book", "author_id")
