from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LibraryBorrowing(models.Model):
    _name = "library.borrowing"
    _description = "Library Borrowing"
    _order = "borrow_date desc, id desc"

    book_id = fields.Many2one("library.book", required=True, index=True)
    borrower_id = fields.Many2one("res.partner", required=True, index=True)
    borrow_date = fields.Date(default=fields.Date.today, required=True)
    due_date = fields.Date(required=True)
    returned_at = fields.Datetime()
    state = fields.Selection(
        [("active", "Active"), ("returned", "Returned"), ("overdue", "Overdue")],
        default="active",
        required=True,
    )
    note = fields.Text()

    @api.onchange("borrow_date")
    def _onchange_borrow_date(self):
        for record in self:
            if record.borrow_date and not record.due_date:
                record.due_date = record.borrow_date + timedelta(days=14)

    @api.constrains("borrow_date", "due_date")
    def _check_dates(self):
        for record in self:
            if record.borrow_date and record.due_date and record.due_date < record.borrow_date:
                raise ValidationError("Due date must be greater than or equal to borrow date.")

    def action_return(self):
        self.write({"state": "returned", "returned_at": fields.Datetime.now()})
