from odoo import models, fields


class LibraryAuthor(models.Model): 
    _name = 'library.author'
    _description = 'Library Author'
    _order = 'name ASC'
    _rec_name = 'name'

#fields
    name = fields.Char(
        string = 'Author',
        required=True,
        index=True,
    )

    bio = fields.Text()

    book_ids = fields.One2many('library.book','author_id')