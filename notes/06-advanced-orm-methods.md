# 🚀 **TOPIC 6: ADVANCED ORM METHODS - COMPREHENSIVE GUIDE**

**Location:** `/home/precious/Desktop/odoo-19.0/odoo/orm/models.py`  
**Core Methods:** `mapped()`, `filtered()`, `filtered_domain()`, `sorted()`, `grouped()`, `exists()`, `ensure_one()`, `name_get()`, `name_search()`

---

## 🎯 **WHAT ARE ADVANCED ORM METHODS?**

These are **powerful tools** built into Odoo recordsets that let you:
- **Extract values** → `mapped()`
- **Filter records** → `filtered()`, `filtered_domain()`
- **Sort records** → `sorted()`
- **Group records** → `grouped()`
- **Check existence** → `exists()`, `ensure_one()`
- **Display names** → `name_get()`, `name_search()`

**Think of them as Swiss Army knives for recordsets!**

---

## 🗺️ **1. mapped() - Extract Values**

**Purpose:** Extract field values or apply function to each record

### **How It Works**

```python
# Get list of names from partners
partners = self.env['res.partner'].search([])
names = partners.mapped('name')
# Result: ['John', 'Jane', 'Bob']

# Get list of IDs
ids = partners.mapped('id')
# Result: [1, 2, 3]

# Get related records (Many2one)
countries = partners.mapped('country_id')
# Result: recordset of country records
```

---

### **Basic mapped() - Field Names**

```python
# From: addons/sale/models/sale_order.py
# Get all product IDs from order lines
product_ids = order.order_line.mapped('product_id')
# Returns: recordset of products

# Get list of prices
prices = order.order_line.mapped('price_unit')
# Returns: [10.0, 20.0, 15.0]

# Get list of names
names = partners.mapped('name')
# Returns: ['Customer A', 'Customer B']
```

**Key Points:**
- For **simple fields** (Char, Integer, Float, etc.) → returns **list**
- For **relational fields** (Many2one, Many2many) → returns **recordset**
- Automatically removes duplicates for recordsets
- Returns empty list for empty recordset

---

### **Nested mapped() - Dot Notation**

```python
# Get country codes from partners
country_codes = partners.mapped('country_id.code')
# Returns: ['US', 'UK', 'CA']

# Get all invoices from order lines
invoices = orders.mapped('order_line.invoice_lines.move_id')
# Returns: recordset of invoices

# Get all tags from products in order lines
tags = order.mapped('order_line.product_id.tag_ids')
# Returns: recordset of all unique tags

# Three levels deep!
cities = partners.mapped('company_id.partner_id.city')
# Returns: list of cities
```

**How it works:**
1. Start with `partners`
2. Follow `country_id` → get countries
3. From countries, get `code` → get codes

---

### **mapped() with Lambda Function**

```python
# Custom calculation
totals = order_lines.mapped(lambda line: line.quantity * line.price_unit)
# Returns: [50.0, 100.0, 75.0]

# String manipulation
upper_names = partners.mapped(lambda p: p.name.upper())
# Returns: ['JOHN DOE', 'JANE SMITH']

# Conditional logic
statuses = orders.mapped(lambda o: 'Paid' if o.invoice_status == 'invoiced' else 'Unpaid')
# Returns: ['Paid', 'Unpaid', 'Paid']

# Complex calculation
discounts = lines.mapped(lambda l: l.price_unit * l.discount / 100)
# Returns: [2.0, 5.0, 1.5]
```

---

### **Real-World mapped() Examples**

```python
# From: addons/sale/models/sale_order.py

# Example 1: Get all invoice IDs
invoice_ids = order.order_line.mapped('invoice_lines.move_id')

# Example 2: Sum all line totals
total = sum(order.order_line.mapped('price_subtotal'))
# Same as: sum(line.price_subtotal for line in order.order_line)

# Example 3: Get unique products
products = orders.mapped('order_line.product_id')
# Returns: recordset of unique products across all orders

# Example 4: Get email addresses
emails = partners.mapped('email')
# Returns: ['john@example.com', 'jane@example.com', False]

# Example 5: Filter then map
active_partner_names = partners.filtered('active').mapped('name')
# Returns: names of active partners only

# Example 6: Map through Many2many
tag_names = product.mapped('tag_ids.name')
# Returns: ['Sale', 'Featured', 'New']
```

---

### **mapped() Performance Tips**

```python
# ❌ SLOW - Loop and build list
names = []
for partner in partners:
    names.append(partner.name)

# ✅ FAST - Use mapped
names = partners.mapped('name')

# ❌ SLOW - Nested loops
all_tags = []
for product in products:
    for tag in product.tag_ids:
        all_tags.append(tag)

# ✅ FAST - Use mapped with dot notation
all_tags = products.mapped('tag_ids')

# ❌ SLOW - Multiple database queries
totals = []
for order in orders:
    total = sum(line.price_subtotal for line in order.order_line)
    totals.append(total)

# ✅ FAST - Prefetch and map
orders.mapped('order_line.price_subtotal')  # Prefetch
totals = [sum(order.order_line.mapped('price_subtotal')) for order in orders]
```

---

## 🔍 **2. filtered() - Filter Records**

**Purpose:** Keep only records that match a condition

### **How It Works**

```python
# Get only active partners
active_partners = partners.filtered(lambda p: p.active)

# Get orders over $1000
big_orders = orders.filtered(lambda o: o.amount_total > 1000)

# Get draft orders
drafts = orders.filtered(lambda o: o.state == 'draft')
```

---

### **filtered() with Lambda**

```python
# From: addons/sale/models/sale_order.py

# Example 1: Filter by state
confirmed_orders = self.filtered(lambda so: so.state == 'sale')

# Example 2: Filter by boolean field
active_partners = partners.filtered(lambda p: p.active)

# Example 3: Filter by related field
us_partners = partners.filtered(lambda p: p.country_id.code == 'US')

# Example 4: Filter with multiple conditions
large_us_orders = orders.filtered(
    lambda o: o.amount_total > 1000 and o.partner_id.country_id.code == 'US'
)

# Example 5: Filter with NOT condition
non_draft = orders.filtered(lambda o: o.state != 'draft')

# Example 6: Filter by existence
with_invoice = orders.filtered(lambda o: o.invoice_ids)

# Example 7: Filter by One2many
orders_with_lines = orders.filtered(lambda o: o.order_line)
```

---

### **filtered() with Field Name (Shorthand)**

```python
# For boolean fields, you can use field name directly

# Using lambda (verbose)
active_partners = partners.filtered(lambda p: p.active)

# Using field name (shorthand)
active_partners = partners.filtered('active')
# Same result, cleaner syntax!

# For related boolean fields with dot notation
partners_in_eu = partners.filtered('country_id.is_eu')

# Examples
published_products = products.filtered('is_published')
archived_records = records.filtered('active')  # Wait, this gets active=True!

# Note: This ONLY works for boolean fields!
```

**Important:** `filtered('active')` returns records where `active=True`, not `active=False`!

---

### **filtered() with Domain (Advanced)**

```python
# You can pass a domain directly!
from odoo.fields import Domain

# Filter with domain
active_us_partners = partners.filtered(Domain([
    ('active', '=', True),
    ('country_id.code', '=', 'US')
]))

# But usually, filtered_domain() is clearer
active_us_partners = partners.filtered_domain([
    ('active', '=', True),
    ('country_id.code', '=', 'US')
])
```

---

### **Real-World filtered() Examples**

```python
# From: addons/sale/models/sale_order.py

# Example 1: Get priced lines (not display-only)
def _get_priced_lines(self):
    return self.order_line.filtered(lambda x: not x.display_type)

# Example 2: Get invoices only
invoices = order.order_line.invoice_lines.move_id.filtered(
    lambda r: r.move_type in ('out_invoice', 'out_refund')
)

# Example 3: Filter by computed field
authorized_transactions = order.transaction_ids.filtered(
    lambda t: t.state == 'authorized'
)

# Example 4: Complex business logic
special_lines = invoiceable_lines.filtered(
    lambda sol: not sol._can_be_invoiced_alone()
)

# Example 5: Filter by state
draft_orders = orders.filtered(lambda o: o.state == 'draft')
duplicate_orders = draft_orders._fetch_duplicate_orders()

# Example 6: Filter records with related data
orders_with_client_ref = orders.filtered(lambda order: order.id and order.client_order_ref)

# Example 7: Combine filtered and mapped
active_partner_names = partners.filtered('active').mapped('name')
```

---

## 🎯 **3. filtered_domain() - Filter with Domain**

**Purpose:** Filter recordset using search domain (more efficient than lambda)

### **How It Works**

```python
# Instead of lambda
active_partners = partners.filtered(lambda p: p.active and p.customer_rank > 0)

# Use filtered_domain (FASTER!)
active_partners = partners.filtered_domain([
    ('active', '=', True),
    ('customer_rank', '>', 0)
])
```

---

### **Why filtered_domain() is Better**

```python
# ❌ SLOW - Python filtering (loops through ALL records)
big_orders = orders.filtered(lambda o: o.amount_total > 1000)

# ✅ FAST - Domain filtering (optimized evaluation)
big_orders = orders.filtered_domain([('amount_total', '>', 1000)])
```

**Performance:**
- `filtered(lambda)` - Evaluates EVERY record in Python
- `filtered_domain()` - Optimized domain evaluation

---

### **Real-World filtered_domain() Examples**

```python
# From: addons/sale/models/sale_order.py

# Example 1: Filter invoiceable lines
invoiceable_domain = [
    ('is_downpayment', '=', False),
    ('display_type', '=', False),
    ('invoice_status', '=', 'to invoice')
]
invoiceable_lines = order.order_line.filtered_domain(invoiceable_domain)

# Example 2: Complex domain
lines = order.order_line.filtered_domain([
    '|',
        ('product_id.type', '=', 'service'),
        ('product_id.type', '=', 'consu'),
    ('qty_to_invoice', '>', 0)
])

# Example 3: Filter by related fields
us_orders = orders.filtered_domain([
    ('partner_id.country_id.code', '=', 'US'),
    ('state', 'in', ['sale', 'done'])
])
```

---

## 🔢 **4. sorted() - Sort Records**

**Purpose:** Sort recordset by field or function

### **How It Works**

```python
# Sort by name
sorted_partners = partners.sorted('name')

# Sort by date (newest first)
sorted_orders = orders.sorted('date_order', reverse=True)

# Sort by custom function
sorted_partners = partners.sorted(lambda p: p.name.lower())
```

---

### **sorted() with Field Name**

```python
# Sort ascending (A-Z)
partners_by_name = partners.sorted('name')

# Sort descending (Z-A)
partners_by_name_desc = partners.sorted('name', reverse=True)

# Sort by date (oldest first)
orders_by_date = orders.sorted('create_date')

# Sort by date (newest first)
orders_by_date_desc = orders.sorted('create_date', reverse=True)

# Sort by integer
products_by_price = products.sorted('list_price')

# Examples
sorted_by_ref = orders.sorted('name')
sorted_by_total = orders.sorted('amount_total', reverse=True)
```

---

### **sorted() with Lambda**

```python
# Sort by calculated value
orders_by_line_count = orders.sorted(lambda o: len(o.order_line))

# Sort by related field
partners_by_country = partners.sorted(lambda p: p.country_id.name)

# Sort with multiple criteria (tuple)
orders_sorted = orders.sorted(lambda o: (o.date_order, o.name))

# Sort by lowercase name (case-insensitive)
partners_sorted = partners.sorted(lambda p: p.name.lower())

# Sort by complex calculation
lines_sorted = lines.sorted(lambda l: l.quantity * l.price_unit)

# Examples
# Sort products by stock quantity, then by name
products_sorted = products.sorted(
    lambda p: (-p.qty_available, p.name)  # Negative for descending
)
```

---

### **sorted() with SQL Order String**

```python
# Sort by multiple fields with SQL syntax
partners_sorted = partners.sorted('country_id, name ASC')

# Sort with NULLS handling
orders_sorted = orders.sorted('commitment_date NULLS LAST, name')

# Sort descending
orders_sorted = orders.sorted('amount_total DESC, name ASC')

# Examples
# Complex SQL ordering
records_sorted = records.sorted('priority DESC, date_order ASC NULLS FIRST')
```

---

### **sorted() Default (Model's _order)**

```python
# If model has _order defined
class SaleOrder(models.Model):
    _name = 'sale.order'
    _order = 'date_order desc, id desc'

# Calling sorted() without arguments uses _order
sorted_orders = orders.sorted()
# Same as: orders.sorted('date_order desc, id desc')
```

---

## 📦 **5. grouped() - Group Records**

**Purpose:** Group recordset by field value

### **How It Works**

```python
# Group partners by country
partners_by_country = partners.grouped('country_id')
# Returns: {country_1: recordset, country_2: recordset, ...}

# Group orders by state
orders_by_state = orders.grouped('state')
# Returns: {'draft': recordset, 'sent': recordset, 'sale': recordset, ...}
```

---

### **grouped() with Field Name**

```python
# Group by Many2one
partners_by_country = partners.grouped('country_id')
for country, partner_group in partners_by_country.items():
    print(f"{country.name}: {len(partner_group)} partners")

# Group by Selection field
orders_by_state = orders.grouped('state')
for state, order_group in orders_by_state.items():
    print(f"{state}: {len(order_group)} orders")

# Group by boolean
products_by_active = products.grouped('active')
active_products = products_by_active.get(True, self.env['product.product'])
archived_products = products_by_active.get(False, self.env['product.product'])
```

---

### **grouped() with Lambda**

```python
# Group by calculated value
partners_by_first_letter = partners.grouped(lambda p: p.name[0].upper())
# Returns: {'A': recordset, 'B': recordset, ...}

# Group by related field
orders_by_country = orders.grouped(lambda o: o.partner_id.country_id)

# Group by range
orders_by_size = orders.grouped(lambda o: 'small' if o.amount_total < 100 else 'large')

# Group by boolean expression
orders_by_paid = orders.grouped(lambda o: o.invoice_status == 'invoiced')
# Returns: {True: paid_orders, False: unpaid_orders}
```

---

### **Real-World grouped() Examples**

```python
# Group products by category
products_by_category = products.grouped('categ_id')
for category, product_group in products_by_category.items():
    print(f"{category.name}: {len(product_group)} products")
    # Process each group
    category.write({'product_count': len(product_group)})

# Group orders by salesperson
orders_by_user = orders.grouped('user_id')
for user, user_orders in orders_by_user.items():
    total = sum(user_orders.mapped('amount_total'))
    print(f"{user.name}: {len(user_orders)} orders, ${total} total")

# Group invoices by month
from datetime import datetime
invoices_by_month = invoices.grouped(
    lambda inv: inv.invoice_date.strftime('%Y-%m') if inv.invoice_date else 'no_date'
)
```

---

## ✅ **6. exists() - Check Record Existence**

**Purpose:** Return only records that still exist in database

### **How It Works**

```python
# Get records by IDs (some might not exist)
partners = self.env['res.partner'].browse([1, 2, 999, 1000])
print(len(partners))  # 4

# Filter to only existing records
existing = partners.exists()
print(len(existing))  # 2 (only 1 and 2 exist)
```

---

### **When to Use exists()**

```python
# Scenario 1: After potential deletions
partners = self.env['res.partner'].browse([1, 2, 3])
# ... some code that might delete records ...
existing_partners = partners.exists()
# Process only records that still exist

# Scenario 2: Validating external IDs
partner_ids = [1, 5, 10, 50]  # From API or import
partners = self.env['res.partner'].browse(partner_ids)
valid_partners = partners.exists()
if len(valid_partners) != len(partner_ids):
    print("Some partners don't exist!")

# Scenario 3: Clean up recordset
record = self.env['sale.order'].browse(order_id)
if record.exists():
    record.action_confirm()
else:
    raise UserError("Order not found!")
```

---

## 🎯 **7. ensure_one() - Ensure Single Record**

**Purpose:** Verify recordset has exactly ONE record, raise error if not

### **How It Works**

```python
# Get one partner
partner = self.env['res.partner'].search([('id', '=', 1)])
partner.ensure_one()  # OK if found, error if 0 or >1

# Use the partner
return partner.name
```

---

### **When to Use ensure_one()**

```python
# Scenario 1: Button methods (expect single record)
def action_confirm(self):
    self.ensure_one()  # Button clicked on ONE order
    self.state = 'sale'

# Scenario 2: After search
partner = self.env['res.partner'].search([('email', '=', email)], limit=1)
partner.ensure_one()  # Ensure we found exactly one
return partner.id

# Scenario 3: Accessing fields safely
def get_partner_info(self, partner_id):
    partner = self.env['res.partner'].browse(partner_id)
    partner.ensure_one()  # Ensure valid
    return {
        'name': partner.name,
        'email': partner.email,
    }

# Scenario 4: Method that expects singleton
def _get_report_filename(self):
    self.ensure_one()
    return f"Order_{self.name}.pdf"
```

**Error messages:**
- 0 records: `ValueError: Expected singleton: res.partner()`
- 2+ records: `ValueError: Expected singleton: res.partner(1, 2)`

---

## 🏷️ **8. name_get() - Display Names**

**Purpose:** Get display name for records (shown in dropdowns, breadcrumbs)

### **Default name_get()**

```python
# Default implementation returns [(id, display_name)]
partners = self.env['res.partner'].browse([1, 2])
result = partners.name_get()
# Returns: [(1, 'John Doe'), (2, 'Jane Smith')]
```

---

### **Override name_get() for Custom Display**

```python
# Example: Show more info in dropdown
def name_get(self):
    result = []
    for record in self:
        # Customize what shows in dropdowns
        name = f"{record.name} ({record.email})"
        result.append((record.id, name))
    return result
# Dropdown shows: "John Doe (john@example.com)"

# Example: Different format based on context
def name_get(self):
    result = []
    for record in self:
        if self.env.context.get('show_address'):
            name = f"{record.name} - {record.street}, {record.city}"
        else:
            name = record.name
        result.append((record.id, name))
    return result
```

---

### **Real-World name_get() Examples**

```python
# Example 1: Sale Order - show partner name
def name_get(self):
    result = []
    for order in self:
        name = order.name
        if self.env.context.get('show_partner'):
            name = f"{name} - {order.partner_id.name}"
        result.append((order.id, name))
    return result

# Example 2: Product - show reference and name
def name_get(self):
    result = []
    for product in self:
        name = product.name
        if product.default_code:
            name = f"[{product.default_code}] {name}"
        result.append((product.id, name))
    return result

# Example 3: Invoice - show number and amount
def name_get(self):
    result = []
    for invoice in self:
        name = invoice.name
        if invoice.state == 'posted':
            name = f"{name} - ${invoice.amount_total:.2f}"
        result.append((invoice.id, name))
    return result
```

---

## 🔍 **9. name_search() - Search by Name**

**Purpose:** Search records by display name (used in dropdowns with autocomplete)

### **Default name_search()**

```python
# Search partners by name
partners = self.env['res.partner'].name_search('John')
# Returns: [(1, 'John Doe'), (2, 'John Smith')]

# With limit
partners = self.env['res.partner'].name_search('John', limit=5)

# With domain
partners = self.env['res.partner'].name_search(
    'John',
    domain=[('country_id.code', '=', 'US')],
    limit=10
)
```

---

### **Override name_search() for Custom Search**

```python
# Example: Search by email too
@api.model
def name_search(self, name='', domain=None, operator='ilike', limit=100):
    domain = domain or []
    
    if name:
        # Search by name OR email
        domain = [
            '|',
                ('name', operator, name),
                ('email', operator, name)
        ] + domain
    
    return super().name_search(name='', domain=domain, operator=operator, limit=limit)

# Example: Search by reference code
@api.model
def name_search(self, name='', domain=None, operator='ilike', limit=100):
    domain = domain or []
    
    if name:
        # Search by name OR default_code
        domain = [
            '|',
                ('name', operator, name),
                ('default_code', operator, name)
        ] + domain
    
    return super().name_search(name='', domain=domain, operator=operator, limit=limit)
```

---

## 📊 **METHODS COMPARISON TABLE**

| Method | Purpose | Returns | Performance |
|--------|---------|---------|-------------|
| **mapped('field')** | Extract values | List or recordset | ⚡⚡⚡ Fast |
| **mapped(lambda)** | Apply function | List or recordset | ⚡⚡ Medium |
| **filtered(lambda)** | Filter records | Recordset | ⚡⚡ Medium |
| **filtered_domain()** | Filter with domain | Recordset | ⚡⚡⚡ Fast |
| **sorted('field')** | Sort records | Recordset | ⚡⚡⚡ Fast |
| **sorted(lambda)** | Sort by function | Recordset | ⚡⚡ Medium |
| **grouped('field')** | Group records | Dict | ⚡⚡⚡ Fast |
| **grouped(lambda)** | Group by function | Dict | ⚡⚡ Medium |
| **exists()** | Check existence | Recordset | ⚡⚡⚡ Fast |
| **ensure_one()** | Verify singleton | None (or error) | ⚡⚡⚡ Fast |
| **name_get()** | Display names | List of tuples | ⚡⚡ Medium |
| **name_search()** | Search by name | List of tuples | ⚡⚡ Medium |

---

## 🔥 **COMPLETE REAL-WORLD EXAMPLE**

```python
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _name = 'sale.order'
    
    name = fields.Char()
    partner_id = fields.Many2one('res.partner')
    order_line = fields.One2many('sale.order.line', 'order_id')
    amount_total = fields.Float()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('sale', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ])
    
    # === USING mapped() ===
    
    def get_all_products(self):
        """Get unique products across all orders"""
        return self.mapped('order_line.product_id')
    
    def get_total_by_product(self):
        """Calculate total sold by product"""
        products = self.mapped('order_line.product_id')
        result = {}
        for product in products:
            # Filter lines for this product, then sum
            product_lines = self.mapped('order_line').filtered(
                lambda l: l.product_id == product
            )
            result[product.name] = sum(product_lines.mapped('price_subtotal'))
        return result
    
    # === USING filtered() ===
    
    def get_confirmed_orders(self):
        """Get only confirmed orders"""
        return self.filtered(lambda o: o.state == 'sale')
    
    def get_large_orders(self, threshold=1000):
        """Get orders above threshold"""
        return self.filtered(lambda o: o.amount_total > threshold)
    
    def get_us_orders(self):
        """Get orders from US customers"""
        return self.filtered(lambda o: o.partner_id.country_id.code == 'US')
    
    # === USING filtered_domain() ===
    
    def get_pending_orders(self):
        """Get orders pending invoice (domain filtering)"""
        return self.filtered_domain([
            ('state', '=', 'sale'),
            ('invoice_status', '!=', 'invoiced')
        ])
    
    # === USING sorted() ===
    
    def get_orders_by_date(self):
        """Get orders sorted by date (newest first)"""
        return self.sorted('date_order', reverse=True)
    
    def get_orders_by_total(self):
        """Get orders sorted by amount"""
        return self.sorted(lambda o: o.amount_total, reverse=True)
    
    # === USING grouped() ===
    
    def get_orders_by_salesperson(self):
        """Group orders by salesperson"""
        orders_by_user = self.grouped('user_id')
        
        report = []
        for user, user_orders in orders_by_user.items():
            report.append({
                'salesperson': user.name,
                'order_count': len(user_orders),
                'total_amount': sum(user_orders.mapped('amount_total')),
            })
        return report
    
    def get_orders_by_state(self):
        """Group orders by state"""
        return self.grouped('state')
    
    # === USING exists() and ensure_one() ===
    
    def validate_and_process(self):
        """Validate orders exist and process"""
        # Check all records still exist
        existing = self.exists()
        if len(existing) != len(self):
            raise ValidationError("Some orders no longer exist!")
        
        # Process each
        for order in existing:
            order.ensure_one()  # Safety check
            order.action_confirm()
    
    # === OVERRIDE name_get() ===
    
    def name_get(self):
        """Customize display name"""
        result = []
        for order in self:
            # Show order number and partner
            name = order.name
            if self.env.context.get('show_partner_name'):
                name = f"{name} - {order.partner_id.name}"
            result.append((order.id, name))
        return result
    
    # === OVERRIDE name_search() ===
    
    @api.model
    def name_search(self, name='', domain=None, operator='ilike', limit=100):
        """Search by order number OR partner name"""
        domain = domain or []
        
        if name:
            domain = [
                '|',
                    ('name', operator, name),
                    ('partner_id.name', operator, name)
            ] + domain
        
        return super().name_search(
            name='',
            domain=domain,
            operator=operator,
            limit=limit
        )
    
    # === COMBINING METHODS ===
    
    def generate_sales_report(self):
        """Complex report using multiple methods"""
        # Get confirmed orders only
        confirmed = self.filtered(lambda o: o.state == 'sale')
        
        # Sort by date
        sorted_orders = confirmed.sorted('date_order', reverse=True)
        
        # Group by month
        from datetime import datetime
        orders_by_month = sorted_orders.grouped(
            lambda o: o.date_order.strftime('%Y-%m')
        )
        
        report = []
        for month, month_orders in orders_by_month.items():
            # Get unique customers
            customers = month_orders.mapped('partner_id')
            
            # Calculate totals
            total = sum(month_orders.mapped('amount_total'))
            
            report.append({
                'month': month,
                'order_count': len(month_orders),
                'customer_count': len(customers),
                'total_amount': total,
                'avg_order': total / len(month_orders),
            })
        
        return report
```

---

## ✅ **KEY TAKEAWAYS**

1. **mapped()** - Extract field values or apply functions (returns list or recordset)
2. **filtered()** - Keep records matching condition (lambda or field name)
3. **filtered_domain()** - Filter with domain (FASTER than lambda)
4. **sorted()** - Sort records (by field, lambda, or SQL string)
5. **grouped()** - Group records into dictionary by key
6. **exists()** - Return only records that exist in database
7. **ensure_one()** - Verify exactly one record (error if 0 or >1)
8. **name_get()** - Customize display names (dropdowns, breadcrumbs)
9. **name_search()** - Customize search behavior (autocomplete)
10. **Chain methods** for powerful data processing pipelines

---

## 🎯 **PERFORMANCE RULES**

1. Use `filtered_domain()` over `filtered(lambda)` when possible
2. Use `mapped('field')` over loops
3. Chain methods efficiently: `records.filtered().sorted().mapped()`
4. Use `grouped()` instead of manual grouping loops
5. Call `exists()` before processing potentially deleted records

---

## 🎯 **WHAT'S NEXT?**

Now you know:
- ✅ How to extract and transform data (mapped)
- ✅ How to filter efficiently (filtered, filtered_domain)
- ✅ How to sort and group records
- ✅ How to validate recordsets (exists, ensure_one)
- ✅ How to customize display (name_get, name_search)

**Next Topic:** Security System (ir.model.access, ir.rule, groups) - Control who can see and do what!

---

**Study Time:** 60-75 minutes  
**Practice:** Chain multiple methods together  
**Real Files:** Check `addons/sale/models/sale_order.py` for examples

