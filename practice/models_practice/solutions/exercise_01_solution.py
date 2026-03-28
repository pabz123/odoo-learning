# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryBook(models.Model):
    """Model for managing library books."""
    
    # ========== MODEL DEFINITION ==========
    _name = 'library.book'
    _description = 'Library Book'
    _order = 'title'  # Alphabetical by title
    _rec_name = 'title'  # Use title for display
    
    # ========== SQL CONSTRAINTS ==========
    _sql_constraints = [
        ('isbn_unique', 
         'UNIQUE(isbn)', 
         'This ISBN already exists! Each book must have a unique ISBN.'),
        
        ('pages_positive',
         'CHECK(pages > 0)',
         'Number of pages must be greater than 0!'),
    ]
    
    # ========== FIELDS ==========
    title = fields.Char(
        string='Book Title',
        required=True,
        index=True,  # Index for fast searching
        help='The title of the book',
    )
    
    author = fields.Char(
        string='Author',
        required=True,
        help='The author of the book',
    )
    
    isbn = fields.Char(
        string='ISBN',
        size=13,
        help='International Standard Book Number (13 digits)',
    )
    
    pages = fields.Integer(
        string='Number of Pages',
        help='Total number of pages in the book',
    )
    
    publish_date = fields.Date(
        string='Publication Date',
        help='The date when the book was published',
    )
    
    available = fields.Boolean(
        string='Available',
        default=True,
        help='Whether the book is available for borrowing',
    )
    
    description = fields.Text(
        string='Description',
        help='A brief description of the book content',
    )
    
    language = fields.Selection([
        ('english', 'English'),
        ('french', 'French'),
        ('spanish', 'Spanish'),
        ('german', 'German'),
    ], string='Language', default='english', help='The language of the book')
    
    # ========== PYTHON CONSTRAINTS ==========
    @api.constrains('title')
    def _check_title_length(self):
        """Ensure title has at least 3 characters."""
        for book in self:
            if book.title and len(book.title) < 3:
                raise ValidationError(
                    'Book title must be at least 3 characters long! '
                    f'Current title "{book.title}" has only {len(book.title)} characters.'
                )
