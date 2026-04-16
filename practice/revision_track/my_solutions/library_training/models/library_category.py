from odoo import models, fields

class LibraryCategory(models.Model):
    _name = 'library.category'
    _description = 'Library Category'
    _order = 'name ASC'

    #fields
    name = fields.Char(
        string = 'Category Name',
        required=True,
    )
    description = fields.Text()
    book_ids = fields.Many2many('library.book')