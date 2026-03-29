# 📚 **TOPIC 3: FIELD TYPES IN ODOO - COMPREHENSIVE GUIDE**

**Location:** `/home/precious/Desktop/odoo-19.0/odoo/orm/fields*.py`  
**Related Files:**
- `odoo/orm/fields.py` - Base Field class (89,893 lines)
- `odoo/orm/fields_textual.py` - Char, Text, Html (36,288 lines)
- `odoo/orm/fields_numeric.py` - Integer, Float, Monetary (13,082 lines)
- `odoo/orm/fields_temporal.py` - Date, Datetime (11,889 lines)
- `odoo/orm/fields_selection.py` - Selection (11,654 lines)
- `odoo/orm/fields_relational.py` - Many2one, One2many, Many2many (80,654 lines)
- `odoo/orm/fields_binary.py` - Binary (15,736 lines)

---

## 🎯 **WHAT ARE FIELDS?**

Fields are the **columns in your database table**. Each field you define in your model becomes a column that stores specific types of data.

```python
# In Python Model:
name = fields.Char(string="Customer Name")
age = fields.Integer(string="Age")

# Becomes in PostgreSQL database:
# Table: res_partner
# Columns:
#   - name (VARCHAR)
#   - age (INTEGER)
```

---

## 📋 **FIELD CATEGORIES**

Odoo has **3 main categories** of fields:

### **1. Simple Fields** (Store data directly)
- **Char, Text, Html** - Text data
- **Integer, Float, Monetary** - Numbers
- **Boolean** - True/False
- **Date, Datetime** - Dates and times
- **Binary** - Files and images
- **Selection** - Dropdown choices

### **2. Relational Fields** (Connect to other models)
- **Many2one** - Links to ONE record (e.g., Invoice → Customer)
- **One2many** - Links to MANY records (e.g., Invoice → Invoice Lines)
- **Many2many** - Links to MANY and back (e.g., Product ↔ Categories)

### **3. Computed Fields** (Calculate values)
- Fields that **compute** their value from other fields
- Can be **stored** in database or calculated **on-the-fly**

---

## 🔤 **1. SIMPLE FIELDS**

---

## **A. TEXT FIELDS**

### **`fields.Char` - Short Text (max 255 characters)**

**When to use:** Names, codes, references, emails, phone numbers

```python
# From: addons/sale/models/sale_order.py (line 54)
name = fields.Char(
    string="Order Reference",        # Label shown in UI
    required=True,                    # Cannot be empty
    copy=False,                       # Don't copy when duplicating
    readonly=False,                   # User can edit
    index='trigram',                  # Fast text search
    default=lambda self: _('New')     # Default value
)

# From: addons/product/models/product_product.py (line 33)
default_code = fields.Char(
    'Internal Reference',
    index=True                        # Create database index for speed
)

# From: addons/sale/models/sale_order.py (line 84)
client_order_ref = fields.Char(
    string="Customer Reference",
    copy=False
)
```

**Key Attributes:**
- `string` - Label in UI
- `required=True` - Field cannot be empty
- `index=True` - Create database index (faster searches)
- `index='trigram'` - Special index for partial text search
- `copy=False` - Don't copy value when duplicating record
- `readonly=True` - User cannot edit (computed fields often use this)
- `default='value'` or `default=lambda self: ...` - Default value
- `translate=True` - Field can be translated to different languages
- `help="..."` - Tooltip shown to user

---

### **`fields.Text` - Long Text (unlimited length)**

**When to use:** Descriptions, notes, comments, long content

```python
# From: addons/product/models/product_template.py
description = fields.Text(
    'Description',
    translate=True                    # Can translate to other languages
)

# Example: Notes field
notes = fields.Text(
    string="Internal Notes",
    help="Private notes for internal use only"
)
```

**Difference from Char:**
- **Char:** Max ~255 characters, shown as single-line input
- **Text:** Unlimited, shown as multi-line textarea

---

### **`fields.Html` - HTML Content**

**When to use:** Rich text with formatting (bold, colors, images)

```python
# Example from mail module
description = fields.Html(
    'Description',
    sanitize=True,                    # Remove dangerous HTML/scripts
    sanitize_attributes=False,        # Keep all attributes
    strip_classes=True                # Remove CSS classes
)

# Email template body
body_html = fields.Html(
    string='Body',
    translate=True,
    sanitize=False                    # Allow full HTML in templates
)
```

**Key Attributes:**
- `sanitize=True` - **IMPORTANT FOR SECURITY!** Removes dangerous HTML (scripts, iframes)
- `sanitize_attributes` - Keep/remove HTML attributes (style, class, etc)
- `strip_classes` - Remove CSS classes

---

## **B. NUMERIC FIELDS**

### **`fields.Integer` - Whole Numbers**

**When to use:** Quantities, counts, IDs, years

```python
# From: addons/product/models/product_product.py (line 77)
product_document_count = fields.Integer(
    string="Documents Count",
    compute='_compute_product_document_count'
)

# Example: Stock quantity
quantity = fields.Integer(
    string="Quantity",
    required=True,
    default=1
)

# Age in years
age = fields.Integer(
    string="Age",
    help="Age in years"
)
```

---

### **`fields.Float` - Decimal Numbers**

**When to use:** Prices, weights, measurements, percentages

```python
# From: addons/product/models/product_product.py (line 60-61)
volume = fields.Float(
    'Volume',
    digits='Volume'                   # Precision from settings (e.g., 2 decimals)
)

weight = fields.Float(
    'Weight',
    digits='Stock Weight'             # Precision for weights
)

# From: addons/product/models/product_product.py (line 23)
price_extra = fields.Float(
    'Variant Price Extra',
    compute='_compute_product_price_extra',
    min_display_digits='Product Price',  # Minimum decimals to show
    help="This is the sum of the extra price of all attributes"
)

# Example: Discount percentage
discount = fields.Float(
    string="Discount (%)",
    digits=(16, 2),                   # Total 16 digits, 2 after decimal
    default=0.0
)
```

**Key Attributes:**
- `digits='DecimalPrecisionName'` - Use predefined precision from settings
- `digits=(total, decimal)` - Fixed precision (e.g., (16,2) = 99999999999999.99)
- `min_display_digits` - Minimum decimals to display in UI

---

### **`fields.Monetary` - Currency Amounts**

**When to use:** Money amounts that should respect currency formatting

```python
# Example from invoice
amount_total = fields.Monetary(
    string="Total",
    currency_field='currency_id',     # REQUIRED: points to currency field
    compute='_compute_amount'
)

# The currency field (Many2one)
currency_id = fields.Many2one(
    'res.currency',
    string="Currency",
    required=True
)

# Example: Product price
price = fields.Monetary(
    'Price',
    currency_field='currency_id',
    required=True,
    default=0.0
)
```

**Why use Monetary instead of Float?**
- Automatically formats according to currency ($ vs € vs ₹)
- Respects currency decimal places (JPY has 0, USD has 2)
- Shows correct currency symbol in UI

**IMPORTANT:** Monetary field MUST have a `currency_id` field in same model!

---

## **C. BOOLEAN FIELD**

### **`fields.Boolean` - True/False Checkbox**

**When to use:** Yes/No, Active/Inactive, flags

```python
# From: addons/sale/models/sale_order.py (line 77)
locked = fields.Boolean(
    help="Locked orders cannot be modified.",
    default=False,
    copy=False,
    tracking=True                     # Track changes in chatter
)

# From: addons/product/models/product_product.py (line 37)
active = fields.Boolean(
    'Active',
    default=True,
    help="If unchecked, it will allow you to hide the product without removing it."
)

# Example: Feature flags
is_published = fields.Boolean(
    string="Published",
    default=False,
    help="Make this visible on website"
)
```

**Default:** If you don't set `default`, it's `False`

---

## **D. DATE & TIME FIELDS**

### **`fields.Date` - Date Only (no time)**

**When to use:** Birthdays, deadlines, start dates

```python
# Example: Due date
date_due = fields.Date(
    string="Due Date",
    required=True,
    default=fields.Date.today          # Today's date
)

# Example: Birth date
birth_date = fields.Date(
    string="Date of Birth"
)
```

**Default values:**
- `fields.Date.today` - Today
- `fields.Date.today()` - Today (function call)
- `lambda self: fields.Date.today()` - Today (dynamic)

---

### **`fields.Datetime` - Date AND Time**

**When to use:** Timestamps, appointments, logs

```python
# From: addons/sale/models/sale_order.py (line 85-86)
create_date = fields.Datetime(
    string="Creation Date",
    index=True,
    readonly=True
)

# From: addons/sale/models/sale_order.py (line 92-96)
date_order = fields.Datetime(
    string="Order Date",
    required=True,
    copy=False,
    help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.",
    default=fields.Datetime.now       # Current date and time
)

# Example: Meeting
meeting_datetime = fields.Datetime(
    string="Meeting Time",
    required=True
)
```

**Default values:**
- `fields.Datetime.now` - Current date and time
- `fields.Datetime.today` - Today at midnight
- `lambda self: fields.Datetime.now()` - Current time (dynamic)

**Datetime vs Date:**
- **Date:** Only stores day (2024-03-15)
- **Datetime:** Stores day + time (2024-03-15 14:30:00)

---

## **E. BINARY FIELD**

### **`fields.Binary` - Files and Images**

**When to use:** File uploads, images, documents, attachments

```python
# From: addons/hr/models/hr_employee.py
id_card = fields.Binary(
    string="ID Card Copy",
    groups="hr.group_hr_user"         # Only HR users can see
)

driving_license = fields.Binary(
    string="Driving License",
    groups="hr.group_hr_user"
)

# Example: Product image
image = fields.Binary(
    string="Image",
    attachment=True,                  # Store in ir_attachment table (better for large files)
    help="Upload product image"
)

# Document upload
document = fields.Binary(
    string="Document",
    attachment=True
)

# Filename field (goes with Binary field)
document_name = fields.Char(
    string="Filename"
)
```

**Key Attributes:**
- `attachment=True` - Store file in `ir_attachment` table (recommended for large files)
- `attachment=False` - Store file directly in field (faster but makes table huge)

**Best Practice:** Always have a filename field alongside Binary field!

---

## **F. SELECTION FIELD**

### **`fields.Selection` - Dropdown with Fixed Options**

**When to use:** Status, types, categories with limited choices

```python
# From: addons/sale/models/sale_order.py (line 70-76)
state = fields.Selection(
    selection=SALE_ORDER_STATE,       # List of tuples or function
    string="Status",
    readonly=True,
    copy=False,
    index=True,
    tracking=3,                       # Track in chatter, priority 3
    group_expand=True,                # Show all options in kanban
    default='draft'
)

# Where SALE_ORDER_STATE is defined at top of file:
SALE_ORDER_STATE = [
    ('draft', "Quotation"),
    ('sent', "Quotation Sent"),
    ('sale', "Sales Order"),
    ('cancel', "Cancelled"),
]

# Example: Priority field
priority = fields.Selection(
    [
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ],
    string='Priority',
    default='1'
)

# Example: Dynamic selection (method)
def _get_certificate_selection(self):
    return [
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
    ]

certificate = fields.Selection(
    selection='_get_certificate_selection',  # Method name as string
    string='Certificate Level',
    tracking=True
)
```

**Selection format:**
```python
[
    ('value_stored_in_db', 'Label Shown to User'),
    ('draft', 'Draft'),
    ('done', 'Done'),
]
```

**Key Attributes:**
- `selection=[...]` - List of (value, label) tuples
- `selection='_method_name'` - Dynamic options from method
- `group_expand=True` - Show all options as columns in kanban view
- `default='value'` - Default selection

---

## 🔗 **2. RELATIONAL FIELDS**

These fields create **relationships between models** (database tables).

---

## **A. Many2one - Link to ONE Record**

**Concept:** "This record belongs to ONE other record"

**Examples:**
- Invoice → Customer (one invoice has ONE customer)
- Employee → Company (one employee works for ONE company)
- Order Line → Order (one line belongs to ONE order)

```python
# From: addons/sale/models/sale_order.py (line 60-63)
company_id = fields.Many2one(
    comodel_name='res.company',       # Model to link to
    required=True,
    index=True,                       # ALWAYS index Many2one!
    default=lambda self: self.env.company
)

# From: addons/sale/models/sale_order.py (line 64-69)
partner_id = fields.Many2one(
    comodel_name='res.partner',       # Model to link to
    string="Customer",                # Custom label
    required=True,
    change_default=True,              # Trigger onchange methods
    index=True,                       # Index for fast queries
    tracking=1,                       # Track in chatter, priority 1
    check_company=True                # Ensure same company
)

# From: addons/product/models/product_product.py (line 40-42)
product_tmpl_id = fields.Many2one(
    'product.template',               # Can omit comodel_name=
    'Product Template',
    bypass_search_access=True,        # Skip access rights check in search
    index=True,
    ondelete="cascade",               # Delete this record if related is deleted
    required=True
)

# Example: Teacher field in Student model
teacher_id = fields.Many2one(
    'school.teacher',
    string='Teacher',
    ondelete='set null',              # Set to null if teacher deleted
    domain=[('active', '=', True)],   # Only show active teachers
    help='Assign a teacher to this student'
)
```

**Key Attributes:**
- `comodel_name='model.name'` - **REQUIRED** - Which model to link to
- `index=True` - **ALWAYS USE THIS** - Makes queries fast
- `required=True` - Field cannot be empty
- `ondelete='cascade'` - Delete this record when related record deleted
- `ondelete='set null'` - Set to null when related record deleted
- `ondelete='restrict'` - Prevent deletion if records linked
- `domain=[...]` - Filter which records can be selected
- `check_company=True` - Auto-check company matches
- `tracking=N` - Track changes in chatter

**Database:** Creates a column with foreign key to other table
```sql
-- Many2one field
partner_id INTEGER REFERENCES res_partner(id)
```

---

## **B. One2many - Link to MANY Records**

**Concept:** "This record owns MANY other records"

**Examples:**
- Order → Order Lines (one order has MANY lines)
- Customer → Invoices (one customer has MANY invoices)
- Teacher → Students (one teacher has MANY students)

```python
# From: addons/sale/models/sale_order.py
order_line = fields.One2many(
    comodel_name='sale.order.line',   # REQUIRED: Related model
    inverse_name='order_id',          # REQUIRED: Many2one field in related model
    string="Order Lines",
    copy=True,                        # Copy lines when duplicating order
    bypass_search_access=True
)

# In sale.order.line model, there MUST be:
# order_id = fields.Many2one('sale.order', ...)

# From: addons/product/models/product_product.py (line 63-70)
pricelist_rule_ids = fields.One2many(
    string="Pricelist Rules",
    comodel_name='product.pricelist.item',
    inverse_name='product_id',        # Field in pricelist.item pointing back
    compute='_compute_pricelist_rule_ids',
    inverse='_inverse_pricelist_rule_ids',
    readonly=False
)

# Example: Teacher → Students
student_ids = fields.One2many(
    'school.student',                 # Related model
    'teacher_id',                     # Many2one field in student model
    string='Students'
)
# In school.student model there MUST be:
# teacher_id = fields.Many2one('school.teacher', ...)
```

**IMPORTANT RULES:**
1. One2many does NOT create a database column
2. It reads the inverse Many2one field in the related model
3. The `inverse_name` MUST exist in the `comodel_name` model

**Visualization:**
```
sale.order (has One2many order_line)
  ↓
sale.order.line (has Many2one order_id)
  - order_id points back to sale.order
  - One2many order_line reads all lines where order_id = this order
```

**Key Attributes:**
- `comodel_name='model.name'` - **REQUIRED** - Related model
- `inverse_name='field'` - **REQUIRED** - Many2one field in related model
- `copy=True` - Copy related records when duplicating
- `copy=False` - Don't copy related records (common for invoices, logs)

---

## **C. Many2many - Link MANY to MANY**

**Concept:** "This record can link to MANY records AND be linked from MANY records"

**Examples:**
- Product ↔ Categories (one product has many categories, one category has many products)
- Student ↔ Courses (one student takes many courses, one course has many students)
- Order ↔ Tags (one order has many tags, one tag on many orders)

```python
# From: addons/sale/models/sale_order.py (line 232-238)
invoice_ids = fields.Many2many(
    comodel_name='account.move',      # Related model
    string="Invoices",
    compute='_get_invoiced',
    search='_search_invoice_ids',
    copy=False
)

# From: addons/sale/models/sale_order.py (more explicit)
transaction_ids = fields.Many2many(
    comodel_name='payment.transaction',
    relation='sale_order_transaction_rel',     # Junction table name
    column1='sale_order_id',                   # Column for this model
    column2='transaction_id',                  # Column for related model
    string="Transactions",
    groups='account.group_account_invoice',
    copy=False,
    readonly=True
)

# From: addons/sale/models/sale_order.py
tag_ids = fields.Many2many(
    comodel_name='crm.tag',
    relation='sale_order_tag_rel',     # Custom junction table
    column1='order_id',                # This side
    column2='tag_id',                  # Other side
    groups="sales_team.group_sale_salesman",
    string="Tags"
)

# From: addons/product/models/product_product.py (line 47-48)
product_template_attribute_value_ids = fields.Many2many(
    'product.template.attribute.value',
    relation='product_variant_combination',    # Junction table
    string="Attribute Values",
    ondelete='restrict'                        # Prevent deletion
)

# Example: Student ↔ Courses
course_ids = fields.Many2many(
    'school.course',
    relation='student_course_rel',     # Optional: custom table name
    column1='student_id',
    column2='course_id',
    string='Courses'
)
```

**Database:** Creates a junction table
```sql
-- Many2many creates a middle table:
CREATE TABLE student_course_rel (
    student_id INTEGER REFERENCES school_student(id),
    course_id INTEGER REFERENCES school_course(id),
    PRIMARY KEY (student_id, course_id)
);
```

**Key Attributes:**
- `comodel_name='model.name'` - **REQUIRED** - Related model
- `relation='table_name'` - Junction table name (optional, auto-generated if omitted)
- `column1='field'` - Column for this model (optional)
- `column2='field'` - Column for related model (optional)
- `ondelete='cascade'/'restrict'` - What happens when records deleted

**When to specify relation/columns:**
- **Must specify** if you have multiple Many2many to same model
- Optional otherwise (Odoo auto-generates names)

---

## 📊 **RELATIONSHIP SUMMARY**

| Field Type | Creates DB Column? | Example | Database Structure |
|------------|-------------------|---------|-------------------|
| **Many2one** | ✅ Yes | Invoice → Customer | `partner_id INTEGER` |
| **One2many** | ❌ No | Order → Lines | Reads inverse Many2one |
| **Many2many** | ❌ No | Product ↔ Tags | Creates junction table |

---

## ⚙️ **3. COMPUTED FIELDS**

Computed fields **calculate their value** from other fields.

### **Basic Computed Field**

```python
# From: addons/sale/models/sale_order.py (line 82)
has_archived_products = fields.Boolean(
    compute="_compute_has_archived_products"   # Method that calculates value
)

# The compute method:
@api.depends('order_line.product_id.active')   # Recalculate when these change
def _compute_has_archived_products(self):
    for order in self:
        order.has_archived_products = any(
            not line.product_id.active
            for line in order.order_line
        )
```

### **Stored Computed Field**

```python
# From: addons/sale/models/sale_order.py (line 111-115)
require_signature = fields.Boolean(
    string="Online signature",
    compute='_compute_require_signature',
    store=True,                        # STORE in database
    readonly=False,                    # User CAN edit
    precompute=True,                   # Compute before saving
    help="Request a online signature from the customer to confirm the order."
)

@api.depends('company_id.portal_confirmation_sign')
def _compute_require_signature(self):
    for order in self:
        order.require_signature = order.company_id.portal_confirmation_sign
```

**Key Attributes:**
- `compute='_method_name'` - **REQUIRED** - Method that calculates value
- `store=True` - Save value in database (faster queries, uses space)
- `store=False` - Calculate on-the-fly (slower queries, saves space)
- `readonly=True` - User cannot edit (default for computed fields)
- `readonly=False` - User CAN edit (needs `store=True`)
- `precompute=True` - Calculate before record created

**When to use store=True:**
- ✅ Need to search/filter on this field
- ✅ Value used in reports/dashboards
- ✅ Expensive calculation
- ❌ Rarely used value
- ❌ Changes frequently

---

## 🎨 **COMMON FIELD ATTRIBUTES (ALL TYPES)**

These attributes work on ANY field type:

| Attribute | What It Does | Example |
|-----------|--------------|---------|
| `string='...'` | Label in UI | `string='Customer Name'` |
| `required=True` | Cannot be empty | `required=True` |
| `readonly=True` | User cannot edit | `readonly=True` |
| `copy=True/False` | Copy when duplicating | `copy=False` |
| `index=True` | Database index | `index=True` |
| `default=value` | Default value | `default=0` |
| `default=lambda self: ...` | Dynamic default | `default=lambda self: self.env.user` |
| `help='...'` | Tooltip | `help='Enter customer name'` |
| `groups='group.name'` | Only visible to group | `groups='sales_team.group_sale_manager'` |
| `tracking=True` | Track in chatter | `tracking=True` |
| `company_dependent=True` | Different value per company | `company_dependent=True` |
| `translate=True` | Can translate | `translate=True` (Char/Text/Html only) |

---

## 📝 **FIELD DEFINITION PATTERNS**

### **Pattern 1: Simple Field**
```python
name = fields.Char(string="Name", required=True)
```

### **Pattern 2: Field with Default**
```python
active = fields.Boolean(default=True)
date = fields.Date(default=fields.Date.today)
user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
```

### **Pattern 3: Field with Domain (Filter)**
```python
partner_id = fields.Many2one(
    'res.partner',
    domain=[('customer_rank', '>', 0)]  # Only customers
)
```

### **Pattern 4: Relational Field**
```python
# Many2one
order_id = fields.Many2one('sale.order', required=True, index=True)

# One2many
line_ids = fields.One2many('sale.order.line', 'order_id', string="Lines")

# Many2many
tag_ids = fields.Many2many('product.tag', string="Tags")
```

### **Pattern 5: Computed Field**
```python
total = fields.Float(compute='_compute_total', store=True)

@api.depends('line_ids.price_subtotal')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('price_subtotal'))
```

---

## 🎓 **WHEN TO USE WHICH FIELD?**

| Need | Field Type | Example |
|------|------------|---------|
| Name, code, short text | `Char` | Customer name, product code |
| Long text | `Text` | Description, notes |
| Formatted text | `Html` | Email body, rich description |
| Number without decimals | `Integer` | Quantity, age, year |
| Number with decimals | `Float` | Weight, volume, percentage |
| Money | `Monetary` | Price, total, tax |
| Yes/No | `Boolean` | Active, published |
| Date only | `Date` | Birth date, deadline |
| Date + time | `Datetime` | Created at, meeting time |
| File/image | `Binary` | Photo, document, PDF |
| Fixed choices | `Selection` | Status, priority, type |
| Link to one | `Many2one` | Customer, company, category |
| Has many | `One2many` | Order lines, comments |
| Belongs to many | `Many2many` | Tags, categories |
| Calculate value | `compute=` | Total, count, status |

---

## 🔥 **REAL-WORLD COMPLETE EXAMPLE**

```python
from odoo import api, fields, models

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _order = 'name'

    # TEXT FIELDS
    name = fields.Char(
        string='Title',
        required=True,
        index='trigram'
    )
    isbn = fields.Char(
        string='ISBN',
        required=True,
        index=True,
        copy=False
    )
    description = fields.Text(
        string='Description',
        translate=True
    )
    
    # NUMERIC FIELDS
    pages = fields.Integer(
        string='Number of Pages',
        default=0
    )
    price = fields.Monetary(
        string='Price',
        currency_field='currency_id',
        required=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # BOOLEAN
    active = fields.Boolean(
        default=True,
        help='Archive instead of delete'
    )
    available = fields.Boolean(
        string='Available',
        default=True
    )
    
    # DATE
    publish_date = fields.Date(
        string='Publish Date'
    )
    
    # SELECTION
    state = fields.Selection([
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('lost', 'Lost'),
    ], string='Status', default='draft')
    
    # MANY2ONE - Links to ONE author
    author_id = fields.Many2one(
        'library.author',
        string='Author',
        required=True,
        index=True,
        ondelete='restrict'
    )
    
    # MANY2ONE - Links to ONE category
    category_id = fields.Many2one(
        'library.category',
        string='Category',
        index=True
    )
    
    # ONE2MANY - Has MANY borrowing records
    borrowing_ids = fields.One2many(
        'library.borrowing',
        'book_id',
        string='Borrowing History'
    )
    
    # MANY2MANY - Can have MANY tags
    tag_ids = fields.Many2many(
        'library.tag',
        string='Tags'
    )
    
    # COMPUTED FIELDS
    borrowing_count = fields.Integer(
        string='Times Borrowed',
        compute='_compute_borrowing_count'
    )
    
    is_popular = fields.Boolean(
        string='Popular',
        compute='_compute_is_popular',
        store=True
    )
    
    @api.depends('borrowing_ids')
    def _compute_borrowing_count(self):
        for book in self:
            book.borrowing_count = len(book.borrowing_ids)
    
    @api.depends('borrowing_count')
    def _compute_is_popular(self):
        for book in self:
            book.is_popular = book.borrowing_count > 10
```

---

## ✅ **KEY TAKEAWAYS**

1. **Simple fields** store data directly (Char, Integer, Boolean, Date, etc.)
2. **Many2one** = Link to ONE record (creates database column)
3. **One2many** = Has MANY records (reads inverse Many2one, no column)
4. **Many2many** = Links MANY ↔ MANY (creates junction table)
5. **Computed fields** calculate values from other fields
6. **Always index Many2one** fields for performance
7. **Monetary needs currency_id** in same model
8. **One2many needs Many2one** in related model
9. **Use `store=True`** on computed fields you need to search/filter
10. **Use `copy=False`** for unique fields (sequence numbers, dates)

---

## 🎯 **WHAT'S NEXT?**

Now you know:
- ✅ All field types
- ✅ When to use each type
- ✅ How relationships work
- ✅ How to create computed fields

**Next Topic:** Field Attributes & Constraints (required, domain, ondelete, _sql_constraints, etc.)

---

**Study Time:** 45-60 minutes  
**Practice:** Try creating models with different field types  
**Real Files:** Check `addons/sale/models/sale_order.py` and `addons/product/models/product_product.py`

