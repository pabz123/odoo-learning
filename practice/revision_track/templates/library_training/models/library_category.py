from odoo import fields, models


class LibraryCategory(models.Model):
    _name = "library.category"
    _description = "Library Category"
    _order = "name"

    name = fields.Char(required=True, index=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
    book_ids = fields.Many2many("library.book")
