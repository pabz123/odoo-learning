from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _order = 'name ASC'

    #fields
    name = fields.Char(
        string = 'Name',
        required=True,
        index=True,
    )

    isbn = fields.Char(
        string = 'ISBN',
        required = True,
        index = True,

    )
    ''' Used indexing for faster searching '''
    author_id = fields.Many2one(
        'library.author',
        required = True, index = True,)
    category_ids = fields.Many2many('library.category')
    page_count = fields.Integer()
    price = fields.Monetary(
        string='Price',
        currency_field='currency_id',
    )
    publish_date = fields.Date(
        string = 'Publication Date'
    )
    cover_image = fields.Binary(
        string = 'Cover Photo'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('lost','Lost'),
    ])
    active = fields.Boolean(
        default = True,
    )
    borrowing_ids = fields.One2many('library.borrowing','book_id')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id.id,
    )
    # Required by security record rules to scope visibility by allowed companies.
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )


    _sql_constraints = [
        ('isbn_unique', 'UNIQUE(isbn)', 'This ISBN already exists!!!'),
        ('Pages_positive', 'CHECK(page_count > 0)', 'Number of pages has to be greater than 0'),

    ]

    # Computed fields

    borrowing_count = fields.Integer(
        compute='_compute_borrowing_count',
        store=True,
    )

    is_available = fields.Boolean(
        compute='_compute_is_available',
    )

    availability_label = fields.Char(
        compute='_compute_availability_label',
        store=True,
    )

    @api.depends('borrowing_ids')
    def _compute_borrowing_count(self):
        for record in self:
            record.borrowing_count = len(record.borrowing_ids)

    @api.depends('borrowing_ids.state')
    def _compute_is_available(self):
        for record in self:
            has_active_borrowing = any(b.state == 'active' for b in record.borrowing_ids)
            record.is_available = not has_active_borrowing

    @api.depends('is_available')
    def _compute_availability_label(self):
        for record in self:
            record.availability_label = 'available' if record.is_available else 'borrowed'

    # Business methods

    @api.model
    def create_demo_books(self):
        # Original attempt (commented for comparison):
        # for book in self:
        #     book = self.env['library.book'].create([
        #         {"name":"Gulliver's travels","isbn":"FAT001","author_id":"AUTH001",
        #         "category_ids":"FTA","page_count": 800," price ":"5100"},
        #         {"name":"Gulliver's travels","isbn":"FAT001","author_id":"AUTH001",
        #         "category_ids":"FTA","page_count": 800," price ":"5100"},,
        #         {"name":"Gulliver's travels","isbn":"FAT001","author_id":"AUTH001",
        #         "category_ids":"FTA","page_count": 800," price ":"5100"},
        #     ])
        # Corrected version (uses bulk create with valid data):
        self.create([
            {
                'name': "Gulliver's Travels",
                'isbn': 'ISBN-001',
                'author_id': 1,
                'page_count': 800,
                'price': 5100.0,
                'state': 'available',
            },
            {
                'name': 'The Great Gatsby',
                'isbn': 'ISBN-002',
                'author_id': 1,
                'page_count': 180,
                'price': 1200.0,
                'state': 'available',
            },
            {
                'name': 'Moby Dick',
                'isbn': 'ISBN-003',
                'author_id': 1,
                'page_count': 635,
                'price': 2500.0,
                'state': 'available',
            },
        ])
    
    def action_mark_lost(self):
        # Original attempt (commented for comparison):
        # self.ensure_one()
        # if self.state != 'borrowed':
        #     raise UserError('Only borrowed books can be marked as lost.')
        # self.write({'state': 'lost'})
        # Corrected version (same logic, now properly imported):
        self.ensure_one()
        if self.state != 'borrowed':
            raise UserError('Only borrowed books can be marked as lost.')
        self.write({'state': 'lost'})

    @api.model 
    def get_books_by_category(self, category_name):
        # Original attempt (commented for comparison):
        # category = self.env['library.category'].search([('name', '=', category_name)], limit=1)
        # if not category:
        #     return self.env['library.book'].filtered_domain([('category_ids', 'in', category.id)])
        # return category.book_ids
        # Corrected version (uses search + filtered_domain on books):
        books = self.search([])
        return books.filtered_domain([('category_ids.name', '=', category_name)])


    @api.model
    def get_top_5_expensive_books(self):
        # Original attempt (commented for comparison):
        # for price in self:
        #     price = self.env['library.book'].search([], order='price desc', limit=5)
        #     return self.env['library.book'].sorted(lambda b: b.price, reverse=True)[:5]
        # Corrected version (uses search + sorted + slicing):
        books = self.search([])
        return books.sorted(key=lambda b: b.price or 0.0, reverse=True)[:5]

    @api.model
    def _cron_archive_lost_books(self):
        cutoff = fields.Datetime.now() - timedelta(days=30)
        lost_books = self.search([
            ('state', '=', 'lost'),
            ('active', '=', True),
            ('write_date', '<', cutoff),
        ])
        lost_books.write({'active': False})

    @api.ondelete(at_uninstall=False)
    def _check_borrowing_history(self):
        for record in self:
            if record.borrowing_ids:
                raise ValidationError('Cannot delete a book with borrowing history.')
