from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LibraryBook(models.Model):
    _name='library.book,
    _description='Library Book'
    _order='title'
    _rec_name='title'
    
    
    _sql_constraints=[
         ('isbn_unique', 'UNIQUE(isbn)','This ISBN already exists! Each book must have a unique ISBN'),
         ('pages_positive','CHECK(pages > 0)','Number of pages must be greater than 0!'),
         ]
   #fields
    title=fields.Char(
        string='Book Title',
        required=True, index
    
        )
        
    author=fields.Char(
         string='Author',
         required=True,
         )
        
    pages=fields.Integer(
        string='Number of pages',
        )
         
    publish_date=fields.Date(
         string='Publication Date',
         )
         
     available=fields.Boolean(
           string='Available'
           default=True,
           )
           
     @api.constrains('title')
     def _check_title_length(self):
         for book in self
            if book.title and len(book.title) < 3:
               raise ValidationError(
                 'Book title must be at least 3 characters long!'
                 f'Current title "{book.title}" has only {len(book.title)} characters'
                 )
         
    
