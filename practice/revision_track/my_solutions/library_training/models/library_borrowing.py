from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class LibraryBorrowing(models.Model):
    _name = 'library.borrowing'
    _description = 'Library Borrowing'

    #fields

    book_id = fields.Many2one(
        'library.book',
        required = True,
        index = True,
    )
    borrower_id = fields.Many2one(
        'res.partner',
        required = True,
        index = True,
    )
    #indexing for faster searching 
    borrow_date = fields.Date(
        required = True,
        default = fields.Date.context_today,
    )
    due_date = fields.Date(
        required = True,
    )
    returned_at = fields.Datetime()
    fine_amount = fields.Float()
    # Original attempt (commented for comparison):
    # state = fields.Selection([
    #     ('active','Active'),
    #     ('returned','Returned'),
    #     ('overdue','Overdue'),
    #     default = 'active',
    # ])
    state = fields.Selection(
        [
            ('active', 'Active'),
            ('returned', 'Returned'),
            ('overdue', 'Overdue'),
        ],
        default='active',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='book_id.currency_id',
        store=True,
        readonly=True,
    )
    # Mirrors the book company so borrowing record rules can filter by company_ids.
    company_id = fields.Many2one(
        'res.company',
        related='book_id.company_id',
        store=True,
        readonly=True,
        index=True,
    )

    @api.constrains('borrow_date','due_date')
    def _check_due_date(self):
        for record in self:
            if record.due_date < record.borrow_date:
                raise ValidationError("Due date must be greater than borrow date.")

    @api.constrains('book_id', 'state')
    def _check_one_active_borrowing_per_book(self):
        for record in self:
            if record.state != 'active' or not record.book_id:
                continue
            active_count = self.search_count([
                ('id', '!=', record.id),
                ('book_id', '=', record.book_id.id),
                ('state', '=', 'active'),
            ])
            if active_count:
                raise ValidationError('This book already has an active borrowing.')

    @api.model
    def cron_mark_overdue(self):
        today = fields.Date.context_today(self)
        overdue_borrowings = self.search([
            ('state', '=', 'active'),
            ('due_date', '<', today),
        ])
        overdue_borrowings.write({'state': 'overdue'})
    @api.model
    def get_overdue_partner_names(self):
        # Original attempt (commented for comparison):
        # over_due_partner_names = self.env['res.partner'].search([
        #     ('borrowing_ids.state', '=', 'overdue'),
        # ]).mapped('name')
        # return over_due_partner_names
        overdue_borrowings = self.search([
            ('state', '=', 'overdue'),
        ])
        return overdue_borrowings.mapped('borrower_id.name')

    @api.model 
    def get_overdue_grouped_by_partner(self):
        # Original attempt (commented for comparison):
        # overdue_borrowings = self.search([
        #     ('state', '=', 'overdue'),
        # ])
        # grouped = {}
        # for borrowing in overdue_borrowings:
        #     partner_name = borrowing.borrower_id.name
        #     if partner_name not in grouped:
        #         grouped[partner_name] = []
        #     grouped[partner_name].append(borrowing)
        # return grouped('borrower_id')
        # print({partner_name: count for partner_name, count in grouped.items()})
        overdue_borrowings = self.search([
            ('state', '=', 'overdue'),
        ])
        grouped_borrowings = overdue_borrowings.grouped('borrower_id')
        return {
            partner.name: len(records)
            for partner, records in grouped_borrowings.items()
            if partner
        }

    def action_return(self):
        self.write({
            'state': 'returned',
            'returned_at': fields.Datetime.now(),
        })


#=====onchange methods======
    @api.onchange('book_id')
    def _onchange_book_id(self):
        if self.book_id and not self.book_id.is_available:
            return {
                'warning': {
                    'title': 'Book Unavailable',
                    'message': f'The book "{self.book_id.name}" is currently not available for borrowing.',
                }
            }

    @api.onchange('borrow_date')
    def _onchange_borrow_date(self):
        if self.borrow_date and not self.due_date:
            self.due_date = self.borrow_date + timedelta(days=14)

    @api.onchange('borrower_id')
    def _onchange_borrower_id(self):
        result = {
            'domain': {
                'book_id': [('is_available', '=', True)],
            }
        }
        if self.borrower_id and not self.borrower_id.email:
            result['warning'] = {
                'title': 'Missing Email',
                'message': 'Selected borrower does not have an email set.',
            }
        return result


   