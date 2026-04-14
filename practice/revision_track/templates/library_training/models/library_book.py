from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LibraryBook(models.Model):
    _name = "library.book"
    _description = "Library Book"
    _order = "name"

    name = fields.Char(required=True, index=True)
    isbn = fields.Char(index=True)
    author_id = fields.Many2one("library.author", index=True)
    category_ids = fields.Many2many("library.category")
    page_count = fields.Integer(default=1)
    state = fields.Selection(
        [("draft", "Draft"), ("available", "Available"), ("borrowed", "Borrowed"), ("lost", "Lost")],
        default="draft",
    )
    active = fields.Boolean(default=True)
    borrowing_ids = fields.One2many("library.borrowing", "book_id")
    description = fields.Text()

    # TODO: add remaining fields, constraints, computes, methods

    @api.constrains("page_count")
    def _check_page_count(self):
        for record in self:
            if record.page_count <= 0:
                raise ValidationError("Page count must be greater than zero.")
