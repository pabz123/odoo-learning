# Topic 2: BaseModel & ORM - COMPREHENSIVE GUIDE

## 📚 TABLE OF CONTENTS
1. What is ORM? (Deep Understanding)
2. The Three Model Types (Detailed)
3. Essential Model Attributes (With Examples)
4. Understanding `self` and Recordsets
5. How Python Becomes Database Tables
6. Real-World Examples from Odoo

---

## 📋 PART 1: What is ORM? (Complete Explanation)

### 🤔 The Problem ORM Solves

Imagine you're building an application that manages a library. You need to store books, members, and loans.

**WITHOUT ORM (Traditional Way):**

Every operation requires writing SQL queries:

```python
import psycopg2

# Connect to database
conn = psycopg2.connect("dbname=library user=admin")
cursor = conn.cursor()

# Create a book
cursor.execute("""
    INSERT INTO books (title, author, isbn, available, pages, publish_date)
    VALUES (%s, %s, %s, %s, %s, %s)
""", ('Python Basics', 'John Smith', '978-123456', True, 350, '2024-01-15'))
conn.commit()

# Find all available books by an author
cursor.execute("""
    SELECT * FROM books 
    WHERE author = %s AND available = true
    ORDER BY publish_date DESC
""", ('John Smith',))
books = cursor.fetchall()

# Update a book
cursor.execute("""
    UPDATE books 
    SET available = false 
    WHERE isbn = %s
""", ('978-123456',))
conn.commit()

# Delete a book
cursor.execute("DELETE FROM books WHERE isbn = %s", ('978-123456',))
conn.commit()

cursor.close()
conn.close()
```

**Problems:**
1. ❌ Mix of Python and SQL - hard to maintain
2. ❌ SQL injection risks if not careful
3. ❌ Database-specific SQL (PostgreSQL ≠ MySQL)
4. ❌ Manual connection management
5. ❌ No type checking - easy to make mistakes
6. ❌ Repetitive boilerplate code
7. ❌ Manual relationship handling

---

### ✅ WITH ORM (The Odoo Way)

**Step 1: Define your model ONCE**

```python
from odoo import models, fields

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _order = 'publish_date desc'
    
    title = fields.Char('Title', required=True)
    author = fields.Char('Author', required=True)
    isbn = fields.Char('ISBN', size=13)
    available = fields.Boolean('Available', default=True)
    pages = fields.Integer('Number of Pages')
    publish_date = fields.Date('Publication Date')
```

**Step 2: Use it everywhere with simple Python**

```python
# CREATE - Add a new book
book = self.env['library.book'].create({
    'title': 'Python Basics',
    'author': 'John Smith',
    'isbn': '978-123456',
    'available': True,
    'pages': 350,
    'publish_date': '2024-01-15',
})
# ORM automatically converts this to:
# INSERT INTO library_book (title, author, isbn, available, pages, publish_date, create_date, write_date)
# VALUES ('Python Basics', 'John Smith', '978-123456', true, 350, '2024-01-15', NOW(), NOW())

# SEARCH - Find available books by author
books = self.env['library.book'].search([
    ('author', '=', 'John Smith'),
    ('available', '=', True)
])
# ORM converts to:
# SELECT * FROM library_book 
# WHERE author = 'John Smith' AND available = true 
# ORDER BY publish_date DESC

# UPDATE - Mark book as unavailable
book.write({'available': False})
# Or even simpler:
book.available = False
# ORM converts to:
# UPDATE library_book SET available = false, write_date = NOW() WHERE id = <book_id>

# DELETE - Remove the book
book.unlink()
# ORM converts to:
# DELETE FROM library_book WHERE id = <book_id>
```

**Benefits of ORM:**
- ✅ **Pure Python** - No SQL knowledge needed
- ✅ **Safe** - No SQL injection possible
- ✅ **Database agnostic** - Works with PostgreSQL, MySQL, SQLite
- ✅ **Automatic** - Handles connections, transactions, commits
- ✅ **Type-safe** - Python checks types for you
- ✅ **Clean code** - Readable and maintainable
- ✅ **Smart relationships** - ORM handles joins and foreign keys

---

### 🎯 How ORM Works (Visual Explanation)

```
┌─────────────────────────────────────────────────────────────┐
│  YOUR PYTHON CODE                                           │
│  book = self.env['library.book'].create({...})             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  ODOO ORM LAYER                                             │
│  • Validates data                                           │
│  • Builds SQL query                                         │
│  • Handles transactions                                     │
│  • Manages cache                                            │
│  • Applies security rules                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  DATABASE (PostgreSQL)                                      │
│  INSERT INTO library_book (title, author, ...) VALUES ...  │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  RESULT BACK TO PYTHON                                      │
│  book object with all data                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 PART 2: The Three Model Types (In-Depth)

Odoo provides **three fundamental model classes**. Each has a specific purpose.

---

### 1. **models.Model** - Persistent/Regular Models

**Definition:** Models that store data permanently in the database.

**Characteristics:**
- ✅ Creates a real PostgreSQL table
- ✅ Data persists forever (until explicitly deleted)
- ✅ Can have millions of records
- ✅ Includes audit fields (create_date, write_date, create_uid, write_uid)
- ✅ Supports all ORM features

**When to use:**
- Core business entities
- Master data
- Transactional records
- Historical data
- Anything that needs to persist

---

#### Real Example 1: Product Model

```python
from odoo import models, fields

class ProductTemplate(models.Model):
    _name = 'product.template'
    _description = "Product"
    _order = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    
    # Basic Information
    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1)
    description = fields.Html('Description', translate=True)
    
    # Product Type
    type = fields.Selection([
        ('consu', "Goods"),
        ('service', "Service"),
        ('combo', "Combo"),
    ], string="Product Type", required=True, default='consu')
    
    # Pricing
    list_price = fields.Float('Sales Price', default=1.0)
    standard_price = fields.Float('Cost', default=0.0)
    
    # Inventory
    qty_available = fields.Float('Quantity On Hand', compute='_compute_quantities')
    
    # Relations
    categ_id = fields.Many2one('product.category', 'Product Category', required=True)
    company_id = fields.Many2one('res.company', 'Company')
```

**What Odoo does behind the scenes:**

1. **Creates PostgreSQL table** `product_template`:
```sql
CREATE TABLE product_template (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    sequence INTEGER DEFAULT 1,
    description TEXT,
    type VARCHAR NOT NULL DEFAULT 'consu',
    list_price NUMERIC DEFAULT 1.0,
    standard_price NUMERIC DEFAULT 0.0,
    categ_id INTEGER REFERENCES product_category(id),
    company_id INTEGER REFERENCES res_company(id),
    create_date TIMESTAMP DEFAULT NOW(),
    create_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP DEFAULT NOW(),
    write_uid INTEGER REFERENCES res_users(id)
);
```

2. **Creates indexes** for fast searching
3. **Sets up foreign key constraints**
4. **Enables change tracking** through mail.thread

---

#### Real Example 2: Sales Order Model

```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = "Sales Order"
    _order = 'date_order desc, id desc'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    
    # Document Information
    name = fields.Char('Order Reference', required=True, copy=False, default='New')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    # Customer Information
    partner_id = fields.Many2one(
        'res.partner', 
        string='Customer', 
        required=True,
        tracking=1,  # Track changes in chatter
    )
    partner_invoice_id = fields.Many2one('res.partner', 'Invoice Address')
    partner_shipping_id = fields.Many2one('res.partner', 'Delivery Address')
    
    # Dates
    date_order = fields.Datetime('Order Date', required=True, default=fields.Datetime.now)
    commitment_date = fields.Datetime('Delivery Date')
    
    # Order Lines (One2many relationship)
    order_line = fields.One2many('sale.order.line', 'order_id', 'Order Lines')
    
    # Amounts
    amount_untaxed = fields.Monetary('Untaxed Amount', compute='_compute_amounts')
    amount_tax = fields.Monetary('Taxes', compute='_compute_amounts')
    amount_total = fields.Monetary('Total', compute='_compute_amounts')
    
    # Company & Currency
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', 'Currency', related='company_id.currency_id')
    
    @api.depends('order_line.price_total')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })
    
    def action_confirm(self):
        """Confirm the sales order."""
        for order in self:
            order.state = 'sale'
            order.name = self.env['ir.sequence'].next_by_code('sale.order') or 'New'
```

**Real-world usage:**

```python
# Create a sales order
order = self.env['sale.order'].create({
    'partner_id': customer.id,  # customer is a res.partner record
    'date_order': '2024-03-28',
    'order_line': [
        (0, 0, {  # Create new line
            'product_id': product1.id,
            'product_uom_qty': 5.0,
            'price_unit': 100.0,
        }),
        (0, 0, {  # Create another line
            'product_id': product2.id,
            'product_uom_qty': 3.0,
            'price_unit': 50.0,
        }),
    ],
})

# Amounts are automatically computed!
print(order.amount_total)  # 650.0 (5*100 + 3*50)

# Confirm the order
order.action_confirm()
print(order.state)  # 'sale'
print(order.name)  # 'SO001' (from sequence)
```

---

### 2. **models.TransientModel** - Temporary Models (Wizards)

**Definition:** Models that store temporary data for short-lived operations.

**Characteristics:**
- ✅ Creates a PostgreSQL table
- ⚠️ Records are **automatically deleted** after a certain time (default: 1 hour)
- ⚠️ Used for wizards and popup dialogs
- ⚠️ No audit trail (no create_date tracking)
- ✅ Perfect for multi-step forms

**When to use:**
- Wizards (popup dialogs)
- Temporary forms
- Export wizards
- Import wizards
- Configuration wizards
- Any data that's only needed temporarily

---

#### Real Example: Invoice Wizard

```python
from odoo import models, fields, api

class SaleAdvancePaymentInv(models.TransientModel):
    _name = 'sale.advance.payment.inv'
    _description = 'Sales Advance Payment Invoice'
    
    # What type of invoice to create?
    advance_payment_method = fields.Selection([
        ('delivered', 'Regular invoice'),
        ('percentage', 'Down payment (percentage)'),
        ('fixed', 'Down payment (fixed amount)')
    ], string='Create Invoice', default='delivered', required=True)
    
    # Down payment details
    deduct_down_payments = fields.Boolean('Deduct down payments')
    has_down_payments = fields.Boolean('Has down payments', compute='_compute_has_down_payments')
    amount = fields.Float('Down Payment Amount')
    fixed_amount = fields.Monetary('Fixed Amount (per SO)')
    
    # Product to use for down payment
    product_id = fields.Many2one(
        'product.product', 
        'Down Payment Product',
        domain=[('type', '=', 'service')]
    )
    
    currency_id = fields.Many2one('res.currency', 'Currency')
    company_id = fields.Many2one('res.company', 'Company')
    
    @api.depends('advance_payment_method')
    def _compute_has_down_payments(self):
        for wizard in self:
            # Check if related sales orders have down payments
            # ... computation logic ...
            wizard.has_down_payments = False
    
    def create_invoices(self):
        """Create invoices based on wizard settings."""
        # Get active sales orders (from context)
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        
        if self.advance_payment_method == 'delivered':
            # Create regular invoices
            sale_orders._create_invoices()
        elif self.advance_payment_method == 'percentage':
            # Create down payment invoices
            sale_orders._create_invoices(final=False)
        
        # Return action to show invoices
        return sale_orders.action_view_invoice()
```

**How this wizard is used:**

1. User selects one or more Sales Orders
2. Clicks "Create Invoice" button
3. Wizard popup opens (this TransientModel)
4. User fills the form
5. Clicks "Create Invoice"
6. Invoices are created
7. Wizard closes
8. **Wizard record is auto-deleted after 1 hour**

**Key point:** The wizard data isn't important after the invoice is created, so it's automatically cleaned up!

---

#### Real Example 2: Export Wizard

```python
from odoo import models, fields

class IrModelFieldsExport(models.TransientModel):
    _name = 'ir.model.fields.export'
    _description = 'Export Model Fields'
    
    # What to export
    export_format = fields.Selection([
        ('csv', 'CSV'),
        ('xls', 'Excel'),
    ], string='Format', default='csv', required=True)
    
    # Field selection
    field_ids = fields.Many2many(
        'ir.model.fields',
        string='Fields to Export',
        required=True
    )
    
    # Options
    include_archived = fields.Boolean('Include Archived Records')
    
    def action_export(self):
        """Generate and download the export file."""
        # Generate file
        if self.export_format == 'csv':
            data = self._generate_csv()
        else:
            data = self._generate_excel()
        
        # Return download action
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/export_{self.id}?download=true',
            'target': 'self',
        }
```

---

### 3. **models.AbstractModel** - Abstract/Mixin Models

**Definition:** Models that provide reusable functionality but don't create database tables.

**Characteristics:**
- ❌ **Does NOT** create a PostgreSQL table
- ✅ Provides fields and methods to other models
- ✅ Used for code reuse (like inheritance in OOP)
- ✅ Multiple models can inherit from one AbstractModel

**When to use:**
- Mixins (shared functionality)
- Common fields across models
- Utility methods
- Interface definitions

---

#### Real Example 1: mail.thread (Messaging Mixin)

```python
from odoo import models, fields, api

class MailThread(models.AbstractModel):
    _name = 'mail.thread'
    _description = 'Mail Thread'
    
    # Messaging fields
    message_ids = fields.One2many(
        'mail.message', 
        'res_id',
        string='Messages',
        domain=lambda self: [('model', '=', self._name)],
        auto_join=True,
    )
    message_follower_ids = fields.One2many(
        'mail.followers',
        'res_id',
        string='Followers',
        domain=lambda self: [('res_model', '=', self._name)],
    )
    message_partner_ids = fields.Many2many(
        'res.partner',
        string='Followers (Partners)',
        compute='_compute_message_partner_ids',
    )
    
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, body='', subject=None, message_type='notification', **kwargs):
        """Post a message on the record.
        
        Returns the created mail.message
        """
        # Create the message
        values = {
            'body': body,
            'subject': subject,
            'message_type': message_type,
            'model': self._name,
            'res_id': self.id,
        }
        return self.env['mail.message'].create(values)
    
    def message_subscribe(self, partner_ids):
        """Add followers to the record."""
        # Add followers
        for partner_id in partner_ids:
            self.env['mail.followers'].create({
                'res_model': self._name,
                'res_id': self.id,
                'partner_id': partner_id,
            })
```

**How it's used (no table created):**

```python
# Other models inherit from mail.thread
class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['mail.thread']  # ← Inherit messaging features
    
    # Now sale.order has all mail.thread fields and methods!
    # But mail.thread itself has NO table

# Usage
order = self.env['sale.order'].browse(1)
order.message_post(body='Order confirmed!', subject='Confirmation')
order.message_subscribe([partner1.id, partner2.id])
```

**Result:**
- ✅ sale.order has a `sale_order` table
- ✅ sale.order has message_ids, message_follower_ids fields
- ✅ sale.order has message_post(), message_subscribe() methods
- ❌ mail.thread has NO table
- ✅ mail.thread code is reused by 100+ models!

---

#### Real Example 2: portal.mixin (Portal Access)

```python
from odoo import models, fields, api

class PortalMixin(models.AbstractModel):
    _name = 'portal.mixin'
    _description = 'Portal Mixin'
    
    # Portal access URL
    access_url = fields.Char('Portal Access URL', compute='_compute_access_url')
    access_token = fields.Char('Security Token')
    
    def _compute_access_url(self):
        """Compute the access URL for portal users."""
        for record in self:
            record.access_url = f'/my/{record._name}/{record.id}'
    
    def _portal_ensure_token(self):
        """Ensure the record has a security token."""
        if not self.access_token:
            self.access_token = str(uuid.uuid4())
        return self.access_token
    
    def get_portal_url(self):
        """Get the full portal URL with token."""
        self._portal_ensure_token()
        return f'{self.access_url}?access_token={self.access_token}'
```

**Usage:**

```python
class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['portal.mixin']  # ← Inherit portal features
    
    # Now has access_url, access_token fields and methods!

# Generate portal URL for customer
order = self.env['sale.order'].browse(1)
portal_url = order.get_portal_url()
# Result: '/my/sale.order/1?access_token=abc-def-ghi'
```

---

### 📊 Model Types Comparison Table

| Feature | Model | TransientModel | AbstractModel |
|---------|-------|----------------|---------------|
| **Creates DB Table** | ✅ Yes | ✅ Yes | ❌ No |
| **Data Persistence** | ✅ Permanent | ⚠️ Temporary (1 hour) | ❌ N/A |
| **Has Records** | ✅ Yes | ✅ Yes (temporary) | ❌ No |
| **Audit Fields** | ✅ create/write date/uid | ❌ No | ❌ No |
| **Use Case** | Business data | Wizards/dialogs | Mixins/utilities |
| **Table Size** | Can be huge | Always small | None |
| **Real Example** | sale.order | sale.advance.payment.inv | mail.thread |
| **Inherited By** | N/A | N/A | Many models |

---

## 🔑 PART 3: Essential Model Attributes (Deep Dive)

Every model has special attributes that control its behavior. Let's explore each one in detail.

---

### **_name** (REQUIRED)

**Definition:** The technical identifier of your model. This becomes the database table name.

**Rules:**
1. Must be lowercase
2. Use dots (.) to separate words
3. Dots become underscores in database
4. Must be globally unique
5. Cannot start with underscore
6. Follow convention: `module_name.model_name`

**Examples from Odoo:**

```python
# Correct naming
_name = 'sale.order'           # Table: sale_order
_name = 'res.partner'          # Table: res_partner
_name = 'account.move'         # Table: account_move
_name = 'product.template'     # Table: product_template
_name = 'hr.employee'          # Table: hr_employee
_name = 'crm.lead'             # Table: crm_lead

# WRONG naming
_name = 'SaleOrder'            # ❌ Uppercase not allowed
_name = 'sale order'           # ❌ Spaces not allowed
_name = '_sale_order'          # ❌ Cannot start with underscore
_name = 'order'                # ⚠️ Too generic, conflicts possible
```

**Convention:** Module prefix + logical name

```python
# In module 'library_management'
_name = 'library.book'         # ✅ Good
_name = 'library.member'       # ✅ Good
_name = 'library.loan'         # ✅ Good

# NOT like this
_name = 'book'                 # ❌ Too generic
_name = 'my.book'              # ❌ Module name should match
```

---

(Continuing in next message due to length...)

### **_description** (REQUIRED)

**Definition:** Human-readable description of the model. Used in logs, error messages, and UI.

**Best Practices:**
1. Keep it short but descriptive
2. Use proper capitalization
3. Singular form (not plural)
4. Clear and professional

**Examples:**

```python
# Good descriptions
_description = "Sales Order"
_description = "Customer"
_description = "Product Template"
_description = "Invoice"
_description = "Warehouse"

# Bad descriptions
_description = "sales order"      # ❌ Should be capitalized
_description = "Sales Orders"     # ❌ Should be singular
_description = "SO"                # ❌ Too cryptic
_description = "This is a sales order model for managing sales"  # ❌ Too verbose
```

**Why it matters:**

```python
# In error messages, Odoo uses _description
# Bad description:
AccessError: You cannot modify 'so' records

# Good description:
AccessError: You cannot modify 'Sales Order' records
```

---

### **_order** (DEFAULT: 'id')

**Definition:** Default sorting order for records when searching.

**Syntax:** `'field_name direction, field_name2 direction, ...'`
- **direction**: `asc` (ascending, A→Z) or `desc` (descending, Z→A)
- **default**: If no direction specified, uses `asc`

**Examples:**

```python
# Sort by date, newest first
_order = 'date_order desc'

# Sort alphabetically by name
_order = 'name'  # Same as 'name asc'

# Multiple fields: first by sequence, then by name
_order = 'sequence, name'

# Complex: priority desc, then date desc, then id
_order = 'priority desc, date_order desc, id desc'

# With nulls handling
_order = 'sequence nulls last, name'
```

**Real examples from Odoo:**

```python
# Sale Order - newest first
class SaleOrder(models.Model):
    _name = 'sale.order'
    _order = 'date_order desc, id desc'

# Product - by name alphabetically
class ProductTemplate(models.Model):
    _name = 'product.template'
    _order = 'name'

# CRM Lead - by priority and date
class CrmLead(models.Model):
    _name = 'crm.lead'
    _order = 'priority desc, date_deadline, id desc'

# Kanban stages - by sequence
class ProjectStage(models.Model):
    _name = 'project.stage'
    _order = 'sequence, name'
```

**Impact on searches:**

```python
# Without _order specified
records = self.env['sale.order'].search([])
# Returns records in random order (actually by ID)

# With _order = 'date_order desc'
records = self.env['sale.order'].search([])
# Returns records newest first

# You can override at search time
records = self.env['sale.order'].search([], order='name')
# Returns records alphabetically by name
```

---

### **_rec_name** (DEFAULT: 'name')

**Definition:** Which field to use when displaying the record as text (like in dropdowns).

**When it's used:**
- Dropdowns / Selection fields
- Many2one field display
- Breadcrumbs
- Log messages
- Anywhere record needs a "name"

**Example - Default behavior:**

```python
class Customer(models.Model):
    _name = 'res.partner'
    _rec_name = 'name'  # This is default, can be omitted
    
    name = fields.Char('Name')
    email = fields.Char('Email')
```

When displayed in a dropdown, shows: `"John Doe"`

**Example - Custom _rec_name:**

```python
class Product(models.Model):
    _name = 'product.template'
    _rec_name = 'display_name'  # Use display_name instead of name
    
    name = fields.Char('Name')
    code = fields.Char('Internal Reference')
    display_name = fields.Char(compute='_compute_display_name')
    
    def _compute_display_name(self):
        for product in self:
            if product.code:
                product.display_name = f'[{product.code}] {product.name}'
            else:
                product.display_name = product.name
```

Now in dropdowns, shows: `"[PROD001] Laptop Computer"` instead of just `"Laptop Computer"`

**Example - Multiple field display:**

```python
class Account(models.Model):
    _name = 'account.account'
    _rec_name = 'display_name'
    
    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    display_name = fields.Char(compute='_compute_display_name')
    
    def _compute_display_name(self):
        for account in self:
            account.display_name = f'{account.code} {account.name}'
```

Displays: `"100000 Cash"` instead of just the name.

---

### **_inherit** (Extend or Mix)

**Definition:** Extend an existing model or inherit from mixins.

**Two different uses:**

#### **Use 1: Extend Existing Model (NO _name)**

Add fields or methods to an existing model.

```python
# Original model (in 'sale' module)
class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = "Sales Order"
    
    name = fields.Char('Order Reference')
    partner_id = fields.Many2one('res.partner', 'Customer')

# Extend it (in 'sale_custom' module)
class SaleOrderExtend(models.Model):
    _inherit = 'sale.order'  # ← NO _name! We're extending sale.order
    
    # Add new field
    custom_field = fields.Char('Custom Field')
    
    # Add new method
    def custom_method(self):
        return "Hello from extension!"
    
    # Override existing method
    def action_confirm(self):
        # Call original method
        result = super().action_confirm()
        # Add custom logic
        self.custom_field = "Confirmed"
        return result
```

**Result:** The `sale.order` model now has:
- All original fields (name, partner_id)
- New field (custom_field)
- New method (custom_method)
- Modified method (action_confirm)

**One table:** `sale_order` (custom_field is added as a column)

---

#### **Use 2: Inherit from Mixins (WITH _name)**

Create a new model that inherits features from AbstractModels.

```python
# Create new model with messaging features
class MyCustomModel(models.Model):
    _name = 'my.custom.model'  # ← HAS _name! New model
    _description = 'My Custom Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # ← Inherit features
    
    name = fields.Char('Name', tracking=True)
    description = fields.Text('Description')
```

**Result:** New model `my.custom.model` has:
- Its own fields (name, description)
- All mail.thread fields (message_ids, message_follower_ids)
- All mail.thread methods (message_post, message_subscribe)
- All mail.activity.mixin fields and methods

**Two tables:**
- `my_custom_model` (with name, description, and mixin fields)
- mail.thread and mail.activity.mixin have NO tables (they're Abstract)

---

#### **Multiple Inheritance**

You can inherit from multiple models:

```python
class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = [
        'portal.mixin',           # Portal access
        'mail.thread',            # Messaging
        'mail.activity.mixin',    # Activities
        'utm.mixin',              # Marketing tracking
    ]
```

Now sale.order has features from ALL four mixins!

---

### **_inherits** (Delegation Inheritance)

**Definition:** Establish "is-a" relationship with another model.

**How it works:**
1. Creates a Many2one link to parent model
2. All parent fields appear on child model
3. Data is stored in parent table
4. Like delegation in programming

**Syntax:**
```python
_inherits = {
    'parent.model': 'link_field_name',
}
```

**Real Example: User is a Partner**

```python
# Parent model
class Partner(models.Model):
    _name = 'res.partner'
    
    name = fields.Char('Name')
    email = fields.Char('Email')
    phone = fields.Char('Phone')
    street = fields.Char('Street')
    city = fields.Char('City')

# Child model - User IS A Partner
class User(models.Model):
    _name = 'res.users'
    _inherits = {'res.partner': 'partner_id'}  # ← Delegation
    
    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict')
    
    # User-specific fields
    login = fields.Char('Login', required=True)
    password = fields.Char('Password')
    active = fields.Boolean('Active', default=True)
```

**What happens:**

```python
# Create a user
user = self.env['res.users'].create({
    'name': 'John Doe',      # ← Stored in res_partner
    'email': 'john@ex.com',  # ← Stored in res_partner
    'phone': '123456',       # ← Stored in res_partner
    'login': 'johndoe',      # ← Stored in res_users
    'password': 'secret',    # ← Stored in res_users
})

# Access partner fields directly
print(user.name)   # 'John Doe' (from res_partner)
print(user.email)  # 'john@ex.com' (from res_partner)
print(user.login)  # 'johndoe' (from res_users)

# Behind the scenes:
# 1. Created record in res_partner with name, email, phone
# 2. Created record in res_users with partner_id, login, password
```

**Database structure:**

```sql
-- res_partner table
id | name      | email          | phone  | street | city
1  | John Doe  | john@ex.com    | 123456 | NULL   | NULL

-- res_users table
id | partner_id | login    | password | active
1  | 1          | johndoe  | secret   | true
```

**Key point:** User "inherits" Partner fields, but data is actually stored in Partner table!

---

### **_table** (OPTIONAL)

**Definition:** Override the default database table name.

**Default behavior:** `_name` with dots replaced by underscores

```python
_name = 'sale.order'    # Table: sale_order (automatic)
_name = 'res.partner'   # Table: res_partner (automatic)
```

**Custom table name:**

```python
class SaleOrder(models.Model):
    _name = 'sale.order'
    _table = 'sales_orders'  # ← Custom table name
```

**When to use:**
- Rarely needed
- Legacy database migration
- Specific naming requirements
- Usually DON'T override this

---

### **_sql_constraints**

**Definition:** Database-level constraints for data integrity.

**Common constraint types:**
1. **UNIQUE** - No duplicate values
2. **CHECK** - Value must meet condition
3. **FOREIGN KEY** - (Handled automatically by Many2one)

**Syntax:**

```python
_sql_constraints = [
    ('constraint_name', 'CONSTRAINT_SQL', 'Error message'),
]
```

**Example 1: Unique email**

```python
class Partner(models.Model):
    _name = 'res.partner'
    
    email = fields.Char('Email')
    
    _sql_constraints = [
        ('email_unique', 'UNIQUE(email)', 'This email already exists!'),
    ]
```

**Example 2: Positive quantity**

```python
class StockQuant(models.Model):
    _name = 'stock.quant'
    
    quantity = fields.Float('Quantity')
    
    _sql_constraints = [
        ('quantity_positive', 'CHECK(quantity >= 0)', 'Quantity cannot be negative!'),
    ]
```

**Example 3: Multiple constraints**

```python
class AccountAccount(models.Model):
    _name = 'account.account'
    
    code = fields.Char('Code')
    company_id = fields.Many2one('res.company', 'Company')
    
    _sql_constraints = [
        # Code must be unique per company
        ('code_company_unique', 
         'UNIQUE(code, company_id)', 
         'Account code must be unique per company!'),
        
        # Code cannot be empty
        ('code_not_empty',
         "CHECK(code != '')",
         'Account code cannot be empty!'),
    ]
```

---

## 💡 PART 4: Understanding `self` and Recordsets

This is **CRITICAL** to understand for Odoo development!

### What is `self`?

In regular Python:
```python
class MyClass:
    def my_method(self):
        # self = ONE instance of MyClass
        pass
```

In Odoo:
```python
class MyModel(models.Model):
    _name = 'my.model'
    
    def my_method(self):
        # self = RECORDSET (0, 1, or MANY records!)
        pass
```

**Key difference:** In Odoo, `self` is a **recordset**, not a single record!

---

### Recordset Basics

**Recordset** = A collection (set) of 0 or more database records

```python
# Empty recordset (0 records)
empty = self.env['sale.order'].browse([])
print(len(empty))  # 0

# Single record recordset (1 record)
order = self.env['sale.order'].browse(5)
print(len(order))  # 1

# Multiple records recordset (3 records)
orders = self.env['sale.order'].browse([5, 10, 15])
print(len(orders))  # 3

# Search returns recordset
all_orders = self.env['sale.order'].search([])
print(len(all_orders))  # Could be 0, 1, 100, 10000, etc.
```

---

### Working with Recordsets

#### **Looping through records:**

```python
def my_method(self):
    # self might contain multiple records
    for record in self:
        print(record.name)      # Access field of ONE record
        print(record.id)        # Each record has unique ID
        record.action_confirm() # Call method on ONE record
```

#### **Single record access:**

```python
def my_method(self):
    # Ensure self contains ONLY ONE record
    self.ensure_one()  # Raises error if len(self) != 1
    
    # Now safe to access fields directly
    print(self.name)
    print(self.amount_total)
```

#### **Multiple records access:**

```python
def my_method(self):
    # self contains multiple records
    
    # Get all names as list
    names = self.mapped('name')
    # Example: ['Order 1', 'Order 2', 'Order 3']
    
    # Filter records
    draft_orders = self.filtered(lambda r: r.state == 'draft')
    
    # Sort records
    sorted_orders = self.sorted(key=lambda r: r.date_order)
    
    # Check if any record meets condition
    has_draft = any(order.state == 'draft' for order in self)
```

---

### Common Patterns

#### **Pattern 1: Loop and process**

```python
def process_orders(self):
    """Process each order in recordset."""
    for order in self:
        # Process one order at a time
        if order.state == 'draft':
            order.action_confirm()
        elif order.state == 'cancel':
            order.action_draft()
```

#### **Pattern 2: Single record operation**

```python
def confirm_order(self):
    """Confirm THIS order (single record expected)."""
    self.ensure_one()  # Ensure exactly 1 record
    
    self.state = 'confirmed'
    self.date_confirmed = fields.Datetime.now()
    self.message_post(body='Order confirmed')
```

#### **Pattern 3: Batch operation**

```python
def cancel_all(self):
    """Cancel ALL orders in recordset."""
    # No loop needed - operates on entire recordset
    self.write({'state': 'cancel'})
    
    # Or with SQL for performance
    self._cr.execute("""
        UPDATE sale_order 
        SET state = 'cancel' 
        WHERE id IN %s
    """, (tuple(self.ids),))
```

---

## 🔍 PART 5: How Python Becomes Database Tables

Let's see the **complete transformation** from Python to PostgreSQL.

### Example: Library Book Model

**Step 1: Define Python model**

```python
from odoo import models, fields, api

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _order = 'publish_date desc, title'
    _rec_name = 'title'
    
    _sql_constraints = [
        ('isbn_unique', 'UNIQUE(isbn)', 'ISBN must be unique!'),
    ]
    
    # Basic fields
    title = fields.Char('Title', required=True, index=True)
    author = fields.Char('Author', required=True)
    isbn = fields.Char('ISBN', size=13)
    pages = fields.Integer('Number of Pages')
    publish_date = fields.Date('Publication Date')
    available = fields.Boolean('Available', default=True)
    description = fields.Text('Description')
    
    # Relational fields
    category_id = fields.Many2one('library.category', 'Category', ondelete='set null')
    publisher_id = fields.Many2one('res.partner', 'Publisher', domain=[('is_company', '=', True)])
    
    # Computed field
    age_years = fields.Integer('Age (Years)', compute='_compute_age_years', store=True)
    
    @api.depends('publish_date')
    def _compute_age_years(self):
        today = fields.Date.today()
        for book in self:
            if book.publish_date:
                delta = today - book.publish_date
                book.age_years = delta.days // 365
            else:
                book.age_years = 0
    
    # Constraint
    @api.constrains('pages')
    def _check_pages(self):
        for book in self:
            if book.pages < 0:
                raise ValidationError('Pages cannot be negative!')
```

**Step 2: Odoo generates SQL**

```sql
-- Create the table
CREATE TABLE library_book (
    -- Auto-generated ID (primary key)
    id SERIAL PRIMARY KEY,
    
    -- Basic fields
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    isbn VARCHAR(13),
    pages INTEGER,
    publish_date DATE,
    available BOOLEAN DEFAULT TRUE,
    description TEXT,
    
    -- Relational fields (foreign keys)
    category_id INTEGER REFERENCES library_category(id) ON DELETE SET NULL,
    publisher_id INTEGER REFERENCES res_partner(id) ON DELETE SET NULL,
    
    -- Computed field (stored)
    age_years INTEGER,
    
    -- Magic columns (auto-added by Odoo)
    create_date TIMESTAMP DEFAULT NOW(),
    create_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP DEFAULT NOW(),
    write_uid INTEGER REFERENCES res_users(id),
    
    -- SQL constraint
    CONSTRAINT isbn_unique UNIQUE(isbn)
);

-- Create index for title
CREATE INDEX library_book_title_idx ON library_book(title);

-- Create default ordering index
CREATE INDEX library_book_order_idx ON library_book(publish_date DESC, title);
```

**Step 3: Usage examples**

```python
# CREATE
book = self.env['library.book'].create({
    'title': 'Python Programming',
    'author': 'John Smith',
    'isbn': '9781234567890',
    'pages': 450,
    'publish_date': '2024-01-15',
    'available': True,
    'category_id': category.id,
})
# SQL: INSERT INTO library_book (title, author, isbn, ...) VALUES (...)

# READ
books = self.env['library.book'].search([
    ('author', '=', 'John Smith'),
    ('available', '=', True)
])
# SQL: SELECT * FROM library_book WHERE author = 'John Smith' AND available = true 
#      ORDER BY publish_date DESC, title

# UPDATE
book.write({'available': False})
# SQL: UPDATE library_book SET available = false, write_date = NOW() WHERE id = X

# DELETE
book.unlink()
# SQL: DELETE FROM library_book WHERE id = X
```

---

## ✅ PART 6: Complete Real-World Example

Let's build a complete model with everything we learned:

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProjectTask(models.Model):
    """Task Management Model"""
    
    # ========== MODEL DEFINITION ==========
    _name = 'project.task'
    _description = 'Project Task'
    _order = 'priority desc, date_deadline, id desc'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    # ========== SQL CONSTRAINTS ==========
    _sql_constraints = [
        ('task_name_unique', 
         'UNIQUE(name, project_id)', 
         'Task name must be unique within project!'),
    ]
    
    # ========== BASIC FIELDS ==========
    name = fields.Char(
        'Task Title',
        required=True,
        tracking=True,
        index=True,
    )
    description = fields.Html('Description')
    
    # ========== STATUS FIELDS ==========
    state = fields.Selection([
        ('draft', 'New'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], string='Priority', default='1')
    
    # ========== RELATIONAL FIELDS ==========
    project_id = fields.Many2one(
        'project.project',
        'Project',
        required=True,
        ondelete='cascade',  # Delete task if project deleted
        index=True,
    )
    
    user_id = fields.Many2one(
        'res.users',
        'Assigned To',
        tracking=True,
        default=lambda self: self.env.user,  # Current user
    )
    
    tag_ids = fields.Many2many(
        'project.tags',
        'project_task_tag_rel',  # Relation table name
        'task_id',
        'tag_id',
        string='Tags',
    )
    
    # ========== DATE FIELDS ==========
    date_start = fields.Datetime('Start Date')
    date_deadline = fields.Date('Deadline', tracking=True)
    date_done = fields.Datetime('Completion Date', readonly=True)
    
    # ========== NUMERIC FIELDS ==========
    planned_hours = fields.Float('Planned Hours')
    effective_hours = fields.Float('Effective Hours', compute='_compute_effective_hours', store=True)
    progress = fields.Float('Progress (%)', default=0.0)
    
    # ========== COMPUTED FIELDS ==========
    is_overdue = fields.Boolean('Overdue', compute='_compute_is_overdue')
    days_remaining = fields.Integer('Days Remaining', compute='_compute_days_remaining')
    
    # ========== COMPANY FIELD ==========
    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda self: self.env.company,
    )
    
    # ========== COMPUTE METHODS ==========
    @api.depends('date_deadline')
    def _compute_is_overdue(self):
        """Check if task is overdue."""
        today = fields.Date.today()
        for task in self:
            if task.date_deadline and task.state not in ['done', 'cancel']:
                task.is_overdue = task.date_deadline < today
            else:
                task.is_overdue = False
    
    @api.depends('date_deadline')
    def _compute_days_remaining(self):
        """Calculate days until deadline."""
        today = fields.Date.today()
        for task in self:
            if task.date_deadline:
                delta = task.date_deadline - today
                task.days_remaining = delta.days
            else:
                task.days_remaining = 0
    
    @api.depends('timesheet_ids.unit_amount')
    def _compute_effective_hours(self):
        """Sum timesheet hours."""
        for task in self:
            task.effective_hours = sum(task.timesheet_ids.mapped('unit_amount'))
    
    # ========== CONSTRAINTS ==========
    @api.constrains('date_start', 'date_deadline')
    def _check_dates(self):
        """Ensure deadline is after start date."""
        for task in self:
            if task.date_start and task.date_deadline:
                if task.date_deadline < task.date_start.date():
                    raise ValidationError('Deadline must be after start date!')
    
    @api.constrains('progress')
    def _check_progress(self):
        """Ensure progress is between 0 and 100."""
        for task in self:
            if not 0 <= task.progress <= 100:
                raise ValidationError('Progress must be between 0 and 100%!')
    
    # ========== BUSINESS METHODS ==========
    def action_start(self):
        """Start the task."""
        self.ensure_one()
        self.write({
            'state': 'in_progress',
            'date_start': fields.Datetime.now(),
        })
        self.message_post(body='Task started')
    
    def action_complete(self):
        """Mark task as done."""
        self.ensure_one()
        self.write({
            'state': 'done',
            'date_done': fields.Datetime.now(),
            'progress': 100.0,
        })
        self.message_post(body='Task completed')
    
    def action_cancel(self):
        """Cancel the task."""
        for task in self:
            task.state = 'cancel'
            task.message_post(body='Task cancelled')
    
    # ========== CRUD OVERRIDES ==========
    @api.model
    def create(self, vals):
        """Override create to add custom logic."""
        # Generate sequence number if needed
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('project.task')
        
        # Create the record
        task = super().create(vals)
        
        # Send notification
        if task.user_id:
            task.message_subscribe([task.user_id.partner_id.id])
        
        return task
    
    def write(self, vals):
        """Override write to add custom logic."""
        # If assigned user changes, notify
        if 'user_id' in vals:
            # Custom notification logic
            pass
        
        return super().write(vals)
    
    def unlink(self):
        """Override unlink to add checks."""
        # Prevent deletion of completed tasks
        if any(task.state == 'done' for task in self):
            raise ValidationError('Cannot delete completed tasks!')
        
        return super().unlink()
```

This example shows:
- ✅ All three inheritance types (_inherit)
- ✅ All common field types
- ✅ Computed fields with @api.depends
- ✅ SQL constraints
- ✅ Python constraints with @api.constrains
- ✅ Business methods
- ✅ CRUD overrides
- ✅ Proper naming and organization

---

## 💡 KEY TAKEAWAYS

1. **ORM = Python → SQL** - Write Python, Odoo generates SQL
2. **Three model types:**
   - `Model` = Permanent data
   - `TransientModel` = Temporary data (wizards)
   - `AbstractModel` = No table (mixins)
3. **_name is required** - Defines technical model name
4. **self is a recordset** - Can be 0, 1, or many records
5. **Fields become columns** - Python fields → DB columns
6. **Inheritance is powerful** - _inherit extends, _inherits delegates
7. **Magic columns** - id, create_date, write_date auto-added
8. **Constraints ensure data quality** - SQL and Python constraints

---

## 🎓 WHAT'S NEXT?

Now you understand models! Next topics:
- **Field Types** - All field types in detail (Char, Integer, Many2one, etc.)
- **CRUD Operations** - Create, Read, Update, Delete in depth
- **API Decorators** - @api.depends, @api.constrains, @api.onchange

---

**Source:** Odoo 19.0 Core - odoo/orm/models.py
**Examples from:** sale, product, crm, project modules
**Date:** 2026-03-28

