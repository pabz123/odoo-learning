# 🎯 **TOPIC 5: API DECORATORS - COMPREHENSIVE GUIDE**

**Location:** `/home/precious/Desktop/odoo-19.0/odoo/orm/decorators.py`  
**Core Decorators:** `@api.depends`, `@api.onchange`, `@api.constrains`, `@api.model`, `@api.ondelete`

---

## 🤔 **WHAT ARE DECORATORS?**

Decorators are **special markers** you put above methods to give them **superpowers**!

```python
class SaleOrder(models.Model):
    _name = 'sale.order'
    
    # Without decorator - just a normal method
    def my_method(self):
        pass
    
    # WITH decorator - method has special behavior!
    @api.depends('partner_id')
    def _compute_total(self):
        pass  # This runs automatically when partner_id changes!
```

**Think of decorators as instructions to Odoo:**
- `@api.depends` → "Recalculate this when X changes"
- `@api.onchange` → "Run this in the UI when user changes X"
- `@api.constrains` → "Check this rule before saving"
- `@api.model` → "This method doesn't need a record"
- `@api.ondelete` → "Check this before deleting"

---

## 🔄 **1. @api.depends - Auto-Compute Fields**

**Purpose:** Automatically recalculate computed field values when dependencies change

### **How It Works**

```python
# Define computed field
total = fields.Float(compute='_compute_total')

# Decorator tells Odoo WHEN to recalculate
@api.depends('line_ids.price_subtotal')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('price_subtotal'))
```

**What happens:**
1. User changes a line's `price_subtotal`
2. Odoo sees `@api.depends('line_ids.price_subtotal')`
3. Odoo automatically calls `_compute_total()`
4. Field `total` gets updated!

---

### **Basic @api.depends**

```python
# From: addons/sale/models/sale_order.py
from odoo import api, fields, models

class SaleOrder(models.Model):
    _name = 'sale.order'
    
    # Field definition
    has_archived_products = fields.Boolean(
        compute='_compute_has_archived_products'
    )
    
    # Compute method with @api.depends
    @api.depends('order_line.product_id')
    def _compute_has_archived_products(self):
        for order in self:
            order.has_archived_products = any(
                not product.active 
                for product in order.order_line.product_id
            )
```

**Dependency:** `'order_line.product_id'`
- When `order_line` changes (add/remove lines)
- When `product_id` on any line changes
- → Recalculate `has_archived_products`

---

### **Multiple Dependencies**

```python
# Depends on TWO fields
@api.depends('partner_id', 'company_id')
def _compute_fiscal_position(self):
    for order in self:
        order.fiscal_position_id = self.env['account.fiscal.position'].get_fiscal_position(
            order.partner_id.id,
            order.company_id.id
        )
```

**Triggers when:**
- `partner_id` changes, OR
- `company_id` changes

---

### **Nested Dependencies (Dot Notation)**

```python
# From: addons/sale/models/sale_order.py
@api.depends('order_line.price_subtotal', 'currency_id', 'company_id')
def _compute_amounts(self):
    for order in self:
        order.amount_total = sum(order.order_line.mapped('price_subtotal'))
```

**Dependency breakdown:**
- `order_line.price_subtotal` - If ANY line's subtotal changes
- `currency_id` - If currency changes
- `company_id` - If company changes

**Dot notation works through:**
- One2many: `'order_line.price'` - any line's price
- Many2one: `'partner_id.name'` - partner's name
- Many2many: `'tag_ids.name'` - any tag's name

---

### **Store vs Non-Store Computed Fields**

```python
# NOT STORED - computed on-the-fly (slower queries, saves space)
total = fields.Float(compute='_compute_total')

@api.depends('line_ids.price')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('price'))

# STORED - saved in database (faster queries, uses space)
total = fields.Float(
    compute='_compute_total',
    store=True  # <-- SAVES TO DATABASE!
)

@api.depends('line_ids.price')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('price'))
```

**When to use store=True:**
- ✅ Need to search/filter on this field
- ✅ Field used in reports/views frequently
- ✅ Expensive calculation
- ❌ Value changes very frequently
- ❌ Rarely used

---

### **@api.depends with Context**

```python
# From: addons/sale/models/sale_order.py
@api.depends('partner_id')
@api.depends_context('sale_show_partner_name')
def _compute_display_name(self):
    if not self.env.context.get('sale_show_partner_name'):
        return super()._compute_display_name()
    for order in self:
        name = order.name
        if order.partner_id.name:
            name = f'{name} - {order.partner_id.name}'
        order.display_name = name
```

**Depends on:**
- Field: `partner_id`
- Context key: `sale_show_partner_name`

When context changes, field recalculates!

---

### **Common @api.depends Patterns**

```python
# Pattern 1: Simple field dependency
@api.depends('name')
def _compute_display_name(self):
    for record in self:
        record.display_name = record.name.upper()

# Pattern 2: Multiple fields
@api.depends('quantity', 'price')
def _compute_total(self):
    for record in self:
        record.total = record.quantity * record.price

# Pattern 3: Related model fields
@api.depends('partner_id.country_id')
def _compute_tax_rate(self):
    for record in self:
        record.tax_rate = record.partner_id.country_id.tax_rate

# Pattern 4: One2many lines
@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))

# Pattern 5: Many2many
@api.depends('tag_ids.name')
def _compute_tag_string(self):
    for record in self:
        record.tag_string = ', '.join(record.tag_ids.mapped('name'))

# Pattern 6: Conditional computation
@api.depends('state', 'amount')
def _compute_status(self):
    for record in self:
        if record.state == 'done':
            record.status = 'Completed'
        elif record.amount > 1000:
            record.status = 'High Value'
        else:
            record.status = 'Normal'
```

---

## 🔧 **2. @api.onchange - UI Field Changes**

**Purpose:** React to user changes in the form view (BEFORE saving)

### **How It Works**

```python
@api.onchange('partner_id')
def _onchange_partner(self):
    # Runs in UI when user changes partner_id
    if self.partner_id:
        self.payment_term_id = self.partner_id.payment_term_id
        self.pricelist_id = self.partner_id.pricelist_id
```

**What happens:**
1. User changes `partner_id` in form
2. `@api.onchange('partner_id')` triggers
3. Method runs on the FORM DATA (not saved yet!)
4. Changes are shown to user immediately
5. User can still cancel without saving

---

### **Basic @api.onchange**

```python
# From: addons/sale/models/sale_order.py
@api.onchange('commitment_date', 'expected_date')
def _onchange_commitment_date(self):
    """Warn if commitment date is sooner than expected date"""
    if self.commitment_date and self.expected_date:
        if self.commitment_date < self.expected_date:
            return {
                'warning': {
                    'title': _('Requested date is too soon.'),
                    'message': _("The delivery date is sooner than the expected date. "
                                "You may be unable to honor the delivery date.")
                }
            }
```

**What this does:**
- Monitors `commitment_date` and `expected_date`
- If user changes either field
- Shows WARNING popup if dates don't make sense
- User sees warning BEFORE saving

---

### **@api.onchange with Field Updates**

```python
@api.onchange('partner_id')
def _onchange_partner_id(self):
    """Auto-fill partner-related fields"""
    if not self.partner_id:
        return
    
    # Update multiple fields
    self.partner_invoice_id = self.partner_id
    self.partner_shipping_id = self.partner_id
    self.payment_term_id = self.partner_id.payment_term_id
    self.fiscal_position_id = self.partner_id.fiscal_position_id
    
    # Update domain for another field
    return {
        'domain': {
            'pricelist_id': [('id', 'in', self.partner_id.pricelist_ids.ids)]
        }
    }
```

**What happens:**
1. User selects partner
2. Invoice/shipping addresses auto-filled
3. Payment term auto-filled
4. Fiscal position auto-filled
5. Pricelist dropdown filtered to partner's pricelists

---

### **Return Values from @api.onchange**

```python
# Pattern 1: Show warning
@api.onchange('field_name')
def _onchange_field(self):
    if some_condition:
        return {
            'warning': {
                'title': 'Warning Title',
                'message': 'Warning message text'
            }
        }

# Pattern 2: Show warning as notification (less intrusive)
@api.onchange('field_name')
def _onchange_field(self):
    return {
        'warning': {
            'title': 'Notice',
            'message': 'This is a notification',
            'type': 'notification'  # Shows as notification, not dialog
        }
    }

# Pattern 3: Change domain (filter dropdown options)
@api.onchange('country_id')
def _onchange_country(self):
    return {
        'domain': {
            'state_id': [('country_id', '=', self.country_id.id)]
        }
    }

# Pattern 4: Multiple returns
@api.onchange('product_id')
def _onchange_product(self):
    if not self.product_id:
        return
    
    # Update fields
    self.name = self.product_id.name
    self.price = self.product_id.list_price
    
    # Return domain AND warning
    result = {
        'domain': {
            'uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]
        }
    }
    
    if self.product_id.price > 1000:
        result['warning'] = {
            'title': 'High Price',
            'message': 'This product is expensive!'
        }
    
    return result
```

---

### **@api.onchange vs @api.depends**

| Feature | @api.onchange | @api.depends |
|---------|---------------|--------------|
| **When** | User changes field in UI | Field dependency changes (anytime) |
| **Where** | Form views only | Everywhere (UI, code, API) |
| **Saves** | No (until user clicks Save) | Yes (if store=True) |
| **Can modify fields** | Yes | Yes (computed field only) |
| **Can show warnings** | Yes | No |
| **Works in backend** | No | Yes |

**Example showing difference:**

```python
# Computed field - runs EVERYWHERE
total = fields.Float(compute='_compute_total', store=True)

@api.depends('quantity', 'price')
def _compute_total(self):
    # Runs when quantity or price changes
    # In UI, in code, via API, everywhere!
    for record in self:
        record.total = record.quantity * record.price

# Onchange - runs ONLY in form view
@api.onchange('quantity')
def _onchange_quantity(self):
    # ONLY runs when user changes quantity in form
    # Does NOT run when changed via code!
    if self.quantity > 100:
        return {
            'warning': {
                'title': 'Large Quantity',
                'message': 'Are you sure you want to order this much?'
            }
        }
```

---

### **Common @api.onchange Patterns**

```python
# Pattern 1: Auto-fill related fields
@api.onchange('partner_id')
def _onchange_partner(self):
    if self.partner_id:
        self.email = self.partner_id.email
        self.phone = self.partner_id.phone

# Pattern 2: Validate and warn
@api.onchange('age')
def _onchange_age(self):
    if self.age < 18:
        return {
            'warning': {
                'title': 'Age Warning',
                'message': 'Must be 18 or older'
            }
        }

# Pattern 3: Filter dropdown options
@api.onchange('category_id')
def _onchange_category(self):
    return {
        'domain': {
            'product_id': [('categ_id', '=', self.category_id.id)]
        }
    }

# Pattern 4: Clear dependent fields
@api.onchange('country_id')
def _onchange_country(self):
    if self.country_id != self._origin.country_id:
        self.state_id = False  # Clear state when country changes

# Pattern 5: Calculate preview (not saved)
@api.onchange('discount_percent')
def _onchange_discount(self):
    if self.discount_percent:
        self.preview_price = self.price * (1 - self.discount_percent / 100)
```

---

## ⚠️ **3. @api.constrains - Validation Rules**

**Purpose:** Validate data BEFORE saving to database

### **How It Works**

```python
@api.constrains('age')
def _check_age(self):
    for record in self:
        if record.age < 0:
            raise ValidationError("Age cannot be negative!")
        if record.age > 150:
            raise ValidationError("Age seems unrealistic!")
```

**What happens:**
1. User tries to save record
2. BEFORE saving, Odoo runs ALL `@api.constrains` methods
3. If any raises `ValidationError`, save is BLOCKED
4. Error message shown to user
5. Record NOT saved to database

---

### **Basic @api.constrains**

```python
# From: addons/sale/models/sale_order.py
from odoo.exceptions import ValidationError

@api.constrains('company_id', 'order_line')
def _check_order_line_company_id(self):
    for order in self:
        invalid_companies = order.order_line.product_id.company_id.filtered(
            lambda c: order.company_id not in c._accessible_branches()
        )
        if invalid_companies:
            bad_products = order.order_line.product_id.filtered(
                lambda p: p.company_id and p.company_id in invalid_companies
            )
            raise ValidationError(_(
                "Your quotation contains products from company %(product_company)s "
                "whereas your quotation belongs to company %(quote_company)s. \n "
                "Please change the company of your quotation or remove the products "
                "from other companies.\n\n%(bad_products)s",
                product_company=', '.join(invalid_companies.mapped('display_name')),
                quote_company=order.company_id.display_name,
                bad_products=', '.join(bad_products.mapped('display_name'))
            ))
```

**What this checks:**
- All order lines must belong to same company as order
- If not, raise error with helpful message
- User cannot save until fixed

---

### **Multiple Field Constraints**

```python
@api.constrains('start_date', 'end_date')
def _check_dates(self):
    for record in self:
        if record.start_date and record.end_date:
            if record.end_date < record.start_date:
                raise ValidationError(
                    "End date cannot be before start date!"
                )
```

**Triggers when:**
- User changes `start_date`, OR
- User changes `end_date`

---

### **Common @api.constrains Patterns**

```python
# Pattern 1: Range validation
@api.constrains('discount')
def _check_discount(self):
    for record in self:
        if not (0 <= record.discount <= 100):
            raise ValidationError("Discount must be between 0 and 100!")

# Pattern 2: Required combination
@api.constrains('type', 'account_id')
def _check_account(self):
    for record in self:
        if record.type == 'invoice' and not record.account_id:
            raise ValidationError("Account is required for invoices!")

# Pattern 3: Uniqueness check
@api.constrains('email')
def _check_email_unique(self):
    for record in self:
        if record.email:
            duplicate = self.search([
                ('email', '=', record.email),
                ('id', '!=', record.id)
            ])
            if duplicate:
                raise ValidationError(f"Email {record.email} already exists!")

# Pattern 4: Related field validation
@api.constrains('line_ids')
def _check_lines(self):
    for record in self:
        if not record.line_ids:
            raise ValidationError("Must have at least one line!")

# Pattern 5: Conditional validation
@api.constrains('state', 'invoice_id')
def _check_invoice(self):
    for record in self:
        if record.state == 'invoiced' and not record.invoice_id:
            raise ValidationError("Invoiced orders must have an invoice!")

# Pattern 6: Percentage validation
@api.constrains('prepayment_percent')
def _check_prepayment_percent(self):
    for record in self:
        if record.require_payment and not (0 < record.prepayment_percent <= 1.0):
            raise ValidationError("Prepayment percentage must be between 0 and 100%!")
```

---

### **SQL Constraints vs Python Constraints**

```python
class MyModel(models.Model):
    _name = 'my.model'
    
    # SQL CONSTRAINT - enforced by database
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Name must be unique!'),
        ('age_positive', 'CHECK(age >= 0)', 'Age must be positive!'),
    ]
    
    # PYTHON CONSTRAINT - enforced by Odoo
    @api.constrains('age')
    def _check_age(self):
        for record in self:
            if record.age > 150:
                raise ValidationError("Age must be less than 150!")
```

**SQL Constraints:**
- ✅ Very fast (database level)
- ✅ Cannot be bypassed
- ❌ Simple checks only
- ❌ Generic error messages

**Python Constraints:**
- ✅ Complex logic
- ✅ Custom error messages
- ✅ Can check related records
- ❌ Slightly slower
- ❌ Can be bypassed with `sudo()`

---

## 📝 **4. @api.model - Class Methods**

**Purpose:** Methods that don't need a specific record

### **How It Works**

```python
# WITHOUT @api.model - needs record
def my_method(self):
    # self = recordset (needs records)
    for record in self:
        print(record.name)

# WITH @api.model - doesn't need record
@api.model
def my_method(self):
    # self = empty recordset (no records needed)
    # Usually used for utilities, searches, defaults
    return self.search([('state', '=', 'draft')])
```

---

### **Basic @api.model**

```python
# From: addons/sale/models/sale_order.py
@api.model
def _get_note_url(self):
    return self.env.company.get_base_url()

@api.model
def _cron_send_pending_emails(self):
    """Find and send pending order emails"""
    pending_orders = self.search([
        ('pending_email_template_id', '!=', False)
    ])
    for order in pending_orders:
        order.send_email()
```

**Common uses:**
- Cron jobs (scheduled tasks)
- Default value methods
- Utility functions
- Search/create from external data

---

### **@api.model with create (override)**

```python
# From: addons/sale/models/sale_order.py
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if vals.get('name', _("New")) == _("New"):
            # Generate sequence number
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _("New")
    
    return super().create(vals_list)
```

**What @api.model_create_multi does:**
- Optimizes batch creation
- Allows processing vals_list before save
- Common for auto-numbering

---

### **Common @api.model Patterns**

```python
# Pattern 1: Default value method
@api.model
def _default_currency(self):
    return self.env.company.currency_id

currency_id = fields.Many2one(
    'res.currency',
    default=_default_currency
)

# Pattern 2: Utility/helper method
@api.model
def get_active_partners(self):
    return self.env['res.partner'].search([('active', '=', True)])

# Pattern 3: Cron job
@api.model
def _cron_cleanup_old_records(self):
    cutoff_date = fields.Date.today() - timedelta(days=90)
    old_records = self.search([
        ('create_date', '<', cutoff_date),
        ('state', '=', 'draft')
    ])
    old_records.unlink()

# Pattern 4: External data import
@api.model
def import_from_api(self, data_list):
    for data in data_list:
        existing = self.search([('external_id', '=', data['id'])])
        if existing:
            existing.write(data)
        else:
            self.create(data)

# Pattern 5: Get dropdown help text
@api.model
def get_empty_list_help(self, help_message):
    return super().get_empty_list_help(help_message)
```

---

## 🗑️ **5. @api.ondelete - Pre-Delete Checks**

**Purpose:** Validate BEFORE deleting records

### **How It Works**

```python
@api.ondelete(at_uninstall=False)
def _unlink_except_done(self):
    for record in self:
        if record.state == 'done':
            raise UserError("Cannot delete completed records!")
```

**What happens:**
1. User tries to delete record
2. BEFORE deleting, `@api.ondelete` runs
3. If raises error, deletion BLOCKED
4. If no error, deletion proceeds

---

### **Basic @api.ondelete**

```python
# From: addons/sale/models/sale_order.py
from odoo.exceptions import UserError

@api.ondelete(at_uninstall=False)
def _unlink_except_draft_or_cancel(self):
    for order in self:
        if order.state not in ('draft', 'cancel'):
            raise UserError(_(
                "You cannot delete a sent quotation or a confirmed sales order. "
                "You must first cancel it."
            ))
```

**What this does:**
- User tries to delete order
- If order is confirmed/sent, BLOCK deletion
- Only draft/cancelled orders can be deleted

---

### **at_uninstall Parameter**

```python
# at_uninstall=False - DON'T run during module uninstall
@api.ondelete(at_uninstall=False)
def _check_before_delete(self):
    # Runs during normal delete
    # SKIPPED during module uninstall
    if self.important:
        raise UserError("Cannot delete important records!")

# at_uninstall=True - ALSO run during module uninstall
@api.ondelete(at_uninstall=True)
def _check_before_delete(self):
    # Runs during normal delete
    # ALSO runs during module uninstall
    if self.has_critical_data:
        raise UserError("Cannot delete! Critical data exists!")
```

**When to use:**
- `at_uninstall=False` - Normal business logic (most common)
- `at_uninstall=True` - Critical data integrity

---

### **Common @api.ondelete Patterns**

```python
# Pattern 1: Prevent deletion by state
@api.ondelete(at_uninstall=False)
def _unlink_if_draft(self):
    if any(record.state != 'draft' for record in self):
        raise UserError("Can only delete draft records!")

# Pattern 2: Check for related records
@api.ondelete(at_uninstall=False)
def _unlink_if_no_invoices(self):
    if any(record.invoice_ids for record in self):
        raise UserError("Cannot delete orders with invoices!")

# Pattern 3: Require permission
@api.ondelete(at_uninstall=False)
def _unlink_if_manager(self):
    if not self.env.user.has_group('sales_team.group_sale_manager'):
        raise UserError("Only managers can delete orders!")

# Pattern 4: Archive instead of delete
@api.ondelete(at_uninstall=False)
def _suggest_archive(self):
    raise UserError("Please archive instead of deleting!")
```

---

## 📊 **DECORATOR SUMMARY TABLE**

| Decorator | Purpose | When It Runs | Can Modify Fields | Can Block Action |
|-----------|---------|--------------|-------------------|------------------|
| **@api.depends** | Auto-compute fields | When dependencies change | Yes (computed field) | No |
| **@api.onchange** | React to UI changes | When user changes field (form) | Yes (any field) | No (but can warn) |
| **@api.constrains** | Validate before save | Before write/create | No | Yes (ValidationError) |
| **@api.model** | Class method | When explicitly called | Yes | No |
| **@api.ondelete** | Validate before delete | Before unlink | No | Yes (UserError) |

---

## 🔥 **COMPLETE REAL-WORLD EXAMPLE**

```python
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    
    # === FIELDS ===
    name = fields.Char(required=True)
    isbn = fields.Char(required=True)
    author_id = fields.Many2one('library.author', required=True)
    publisher_id = fields.Many2one('library.publisher')
    
    borrowing_ids = fields.One2many('library.borrowing', 'book_id')
    
    # Computed fields
    borrowing_count = fields.Integer(
        compute='_compute_borrowing_count',
        store=True
    )
    is_available = fields.Boolean(
        compute='_compute_is_available'
    )
    popularity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], compute='_compute_popularity', store=True)
    
    state = fields.Selection([
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('lost', 'Lost'),
    ], default='available')
    
    # === @api.depends - Computed Fields ===
    
    @api.depends('borrowing_ids')
    def _compute_borrowing_count(self):
        """Count how many times book was borrowed"""
        for book in self:
            book.borrowing_count = len(book.borrowing_ids)
    
    @api.depends('borrowing_ids.state')
    def _compute_is_available(self):
        """Check if book is currently available"""
        for book in self:
            # Available if no active borrowings
            active_borrowings = book.borrowing_ids.filtered(
                lambda b: b.state == 'active'
            )
            book.is_available = not active_borrowings
    
    @api.depends('borrowing_count')
    def _compute_popularity(self):
        """Categorize popularity based on borrow count"""
        for book in self:
            if book.borrowing_count > 50:
                book.popularity = 'high'
            elif book.borrowing_count > 20:
                book.popularity = 'medium'
            else:
                book.popularity = 'low'
    
    # === @api.onchange - UI Helpers ===
    
    @api.onchange('author_id')
    def _onchange_author_id(self):
        """Auto-fill publisher from author's usual publisher"""
        if self.author_id and self.author_id.default_publisher_id:
            self.publisher_id = self.author_id.default_publisher_id
    
    @api.onchange('isbn')
    def _onchange_isbn(self):
        """Validate ISBN format and warn about duplicates"""
        if self.isbn:
            # Check format
            if len(self.isbn) not in (10, 13):
                return {
                    'warning': {
                        'title': 'Invalid ISBN',
                        'message': 'ISBN should be 10 or 13 characters long.'
                    }
                }
            
            # Check duplicate
            duplicate = self.search([
                ('isbn', '=', self.isbn),
                ('id', '!=', self.id or 0)
            ])
            if duplicate:
                return {
                    'warning': {
                        'title': 'Duplicate ISBN',
                        'message': f'This ISBN already exists: {duplicate[0].name}'
                    }
                }
    
    # === @api.constrains - Validation ===
    
    @api.constrains('isbn')
    def _check_isbn(self):
        """Ensure ISBN is unique"""
        for book in self:
            if book.isbn:
                duplicate = self.search([
                    ('isbn', '=', book.isbn),
                    ('id', '!=', book.id)
                ])
                if duplicate:
                    raise ValidationError(
                        f"ISBN {book.isbn} already exists for: {duplicate[0].name}"
                    )
    
    @api.constrains('borrowing_ids')
    def _check_single_active_borrowing(self):
        """Ensure book has max one active borrowing"""
        for book in self:
            active_borrowings = book.borrowing_ids.filtered(
                lambda b: b.state == 'active'
            )
            if len(active_borrowings) > 1:
                raise ValidationError(
                    "Book cannot have multiple active borrowings!"
                )
    
    # === @api.model - Utility Methods ===
    
    @api.model
    def _default_publisher(self):
        """Get default publisher"""
        return self.env['library.publisher'].search([], limit=1)
    
    @api.model
    def search_by_isbn(self, isbn):
        """Search book by ISBN (external API)"""
        return self.search([('isbn', '=', isbn)], limit=1)
    
    @api.model
    def _cron_return_overdue_books(self):
        """Cron: Mark overdue borrowings as returned"""
        overdue = self.env['library.borrowing'].search([
            ('state', '=', 'active'),
            ('due_date', '<', fields.Date.today())
        ])
        overdue.write({'state': 'overdue'})
    
    # === @api.ondelete - Delete Protection ===
    
    @api.ondelete(at_uninstall=False)
    def _unlink_if_not_borrowed(self):
        """Prevent deletion if book has borrowing history"""
        for book in self:
            if book.borrowing_ids:
                raise UserError(_(
                    "Cannot delete book '%(book)s' because it has borrowing history. "
                    "Please archive it instead.",
                    book=book.name
                ))
    
    @api.ondelete(at_uninstall=False)
    def _unlink_if_not_lost(self):
        """Prevent deletion if book is currently borrowed"""
        for book in self:
            if book.state == 'borrowed':
                raise UserError(_(
                    "Cannot delete book '%(book)s' because it is currently borrowed!",
                    book=book.name
                ))
```

---

## ✅ **KEY TAKEAWAYS**

1. **@api.depends** - Auto-compute when dependencies change (everywhere)
2. **@api.onchange** - React to UI changes (form views only, before save)
3. **@api.constrains** - Validate before saving (can block with error)
4. **@api.model** - Methods that don't need specific records
5. **@api.ondelete** - Validate before deleting (can block deletion)
6. **Use store=True** on computed fields you need to search
7. **@api.depends triggers everywhere**, @api.onchange only in UI
8. **Constraints block saves**, ondelete blocks deletions
9. **Always loop** `for record in self:` in depends/constrains
10. **ValidationError** for constrains, **UserError** for ondelete

---

## 🎯 **WHAT'S NEXT?**

Now you know:
- ✅ When to use each decorator
- ✅ How to create computed fields
- ✅ How to react to UI changes
- ✅ How to validate data
- ✅ How to protect records from deletion

**Next Topic:** View Types (Form, Tree, Kanban, etc.) - How to display your data!

---

**Study Time:** 60-75 minutes  
**Practice:** Create a model with all decorators  
**Real Files:** Check `addons/sale/models/sale_order.py` for examples

