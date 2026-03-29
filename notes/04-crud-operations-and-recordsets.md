# 🎯 **TOPIC 4: CRUD OPERATIONS & RECORDSETS - COMPREHENSIVE GUIDE**

**Location:** `/home/precious/Desktop/odoo-19.0/odoo/orm/models.py`  
**Core Methods:** `create()`, `search()`, `write()`, `unlink()`, `browse()`

---

## 🤔 **WHAT IS A RECORDSET?**

A **recordset** is Odoo's way of representing database records in Python. It's like a **smart list** of records.

```python
# A recordset can contain:
partners = self.env['res.partner']        # Empty recordset (0 records)
partner = self.env['res.partner'].browse(1)  # One record
partners = self.env['res.partner'].search([])  # Many records

# You can loop through it:
for partner in partners:
    print(partner.name)

# Check if empty:
if partners:
    print("Has partners!")

# Get count:
count = len(partners)
```

**Key Points:**
- Recordset = Collection of 0 or more records
- Even ONE record is a recordset (length 1)
- Empty recordset has length 0
- You can loop, filter, map, sort recordsets

---

## 📖 **UNDERSTANDING `self`**

In Odoo models, `self` is **ALWAYS a recordset**!

```python
class SaleOrder(models.Model):
    _name = 'sale.order'
    
    def my_method(self):
        # self is a recordset!
        print(len(self))           # How many records?
        
        for order in self:         # Loop through each record
            print(order.name)      # Access fields
```

**Three scenarios:**

### **1. Button Click (UI) → self = ONE record**
```python
def action_confirm(self):
    # User clicked button on ONE order
    # self = recordset with 1 order
    self.state = 'sale'
    self.date_confirm = fields.Datetime.now()
```

### **2. Server Action (Multi-select) → self = MANY records**
```python
def action_cancel(self):
    # User selected MANY orders and clicked "Cancel"
    # self = recordset with multiple orders
    for order in self:
        order.state = 'cancel'
```

### **3. Automated Action / Code → Can be ANY**
```python
def _cron_send_emails(self):
    # Called by scheduled action
    # self = empty recordset (must search)
    orders = self.search([('state', '=', 'draft')])
    for order in orders:
        order.send_email()
```

**ALWAYS remember:**
- `self` can have 0, 1, or many records
- Use `for record in self:` if you need single records
- Use `if self:` to check if recordset is not empty

---

## 🔍 **1. SEARCH - Finding Records**

**Purpose:** Find records matching criteria

### **Basic Search**

```python
# From: odoo/orm/models.py (line 1363)
# search(domain, offset=0, limit=None, order=None)

# Find all active partners
partners = self.env['res.partner'].search([('active', '=', True)])

# Find customers (not suppliers)
customers = self.env['res.partner'].search([('customer_rank', '>', 0)])

# Find draft orders
orders = self.env['sale.order'].search([('state', '=', 'draft')])
```

### **Search with Limit and Order**

```python
# Get first 10 partners, sorted by name
partners = self.env['res.partner'].search(
    [('active', '=', True)],
    limit=10,
    order='name ASC'
)

# Get newest 5 orders
orders = self.env['sale.order'].search(
    [],                      # Empty domain = all records
    limit=5,
    order='create_date DESC'
)

# Skip first 20, get next 10 (pagination)
partners = self.env['res.partner'].search(
    [],
    offset=20,
    limit=10
)
```

### **Domain Operators**

A **domain** is a list of conditions: `[('field', 'operator', 'value')]`

```python
# COMPARISON OPERATORS
[('age', '=', 25)]           # Equal
[('age', '!=', 25)]          # Not equal
[('age', '>', 18)]           # Greater than
[('age', '>=', 18)]          # Greater or equal
[('age', '<', 65)]           # Less than
[('age', '<=', 65)]          # Less or equal

# TEXT OPERATORS
[('name', 'like', 'John')]        # Contains "John" (case insensitive)
[('name', 'ilike', 'john')]       # Contains "john" (case insensitive)
[('name', '=like', 'John%')]      # Starts with "John"
[('name', '=ilike', 'john%')]     # Starts with "john"
[('name', 'not like', 'Test')]    # Doesn't contain "Test"

# LIST OPERATORS
[('id', 'in', [1, 2, 3])]         # ID is 1, 2, or 3
[('id', 'not in', [1, 2])]        # ID is not 1 or 2
[('state', 'in', ['draft', 'done'])]  # State is draft or done

# NULL OPERATORS
[('parent_id', '=', False)]       # No parent (NULL)
[('parent_id', '!=', False)]      # Has parent (NOT NULL)

# BOOLEAN
[('active', '=', True)]           # Active is true
[('active', '=', False)]          # Active is false
```

### **Combining Conditions (AND / OR / NOT)**

```python
# AND (implicit) - all conditions must match
domain = [
    ('active', '=', True),
    ('customer_rank', '>', 0),
    ('country_id.code', '=', 'US')
]
# Means: active=True AND customer_rank>0 AND country=US

# OR - any condition can match
domain = [
    '|',                           # OR operator
    ('state', '=', 'draft'),
    ('state', '=', 'sent')
]
# Means: state=draft OR state=sent

# OR with 3 conditions (need 2 OR operators)
domain = [
    '|', '|',                      # Two OR operators for 3 conditions
    ('state', '=', 'draft'),
    ('state', '=', 'sent'),
    ('state', '=', 'sale')
]
# Means: state=draft OR state=sent OR state=sale

# NOT - negate a condition
domain = [
    '!',                           # NOT operator
    ('state', '=', 'cancel')
]
# Means: NOT (state=cancel) → state is anything except cancel

# COMPLEX: (active=True) AND (state=draft OR state=sent)
domain = [
    ('active', '=', True),         # AND is implicit
    '|',                           # Start OR
    ('state', '=', 'draft'),
    ('state', '=', 'sent')
]

# COMPLEX: (customer=True AND country=US) OR (supplier=True AND country=UK)
domain = [
    '|',                                    # Main OR
        '&',                                # First AND group
            ('customer_rank', '>', 0),
            ('country_id.code', '=', 'US'),
        '&',                                # Second AND group
            ('supplier_rank', '>', 0),
            ('country_id.code', '=', 'GB')
]
```

**Domain Rules:**
- Default is **AND** (all conditions must match)
- Use `'|'` for **OR**
- Use `'!'` for **NOT**
- Use `'&'` for explicit **AND**
- Operators apply to the next 2 conditions
- For 3 conditions with OR, need 2 `'|'` operators

### **Real-World Examples**

```python
# From: addons/sale/models/sale_order.py
# Find if company has active pricelists
active_pricelist = self.env['product.pricelist'].search(
    [
        ('company_id', 'in', (False, order.company_id.id)),
        ('active', '=', True)
    ],
    limit=1,
)

# Find pending email orders
pending_orders = self.search([
    ('pending_email_template_id', '!=', False)
])

# Find draft orders for specific partner
orders = self.env['sale.order'].search([
    ('partner_id', '=', partner.id),
    ('state', '=', 'draft')
])
```

### **Search Count**

```python
# Just count, don't return records (faster!)
count = self.env['sale.order'].search_count([
    ('state', '=', 'draft')
])
print(f"Found {count} draft orders")
```

### **Ensure One**

```python
# Make sure recordset has exactly ONE record
partner = self.env['res.partner'].search([('id', '=', 1)])
partner.ensure_one()  # Raises error if not exactly 1 record

# Common pattern:
partner = self.env['res.partner'].browse(partner_id)
partner.ensure_one()
return partner.name
```

---

## ➕ **2. CREATE - Adding New Records**

**Purpose:** Create new records in database

### **Basic Create**

```python
# From: odoo/orm/models.py (line 4611)
# create(vals_list) → returns created recordset

# Create ONE partner
partner = self.env['res.partner'].create({
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '+1234567890'
})
# Returns: recordset with 1 new partner
print(partner.id)  # Database ID of new record

# Create ONE order
order = self.env['sale.order'].create({
    'partner_id': partner.id,
    'date_order': fields.Datetime.now(),
})
```

### **Create Multiple Records**

```python
# Create MANY partners at once (faster!)
partners = self.env['res.partner'].create([
    {'name': 'John Doe', 'email': 'john@example.com'},
    {'name': 'Jane Smith', 'email': 'jane@example.com'},
    {'name': 'Bob Johnson', 'email': 'bob@example.com'},
])
# Returns: recordset with 3 new partners
print(len(partners))  # 3
```

### **Create with Many2one Relationships**

```python
# Get existing record
partner = self.env['res.partner'].search([('name', '=', 'John')], limit=1)

# Create order linked to that partner
order = self.env['sale.order'].create({
    'partner_id': partner.id,      # Many2one: use ID
    'date_order': fields.Date.today(),
})
```

### **Create with One2many/Many2many (Commands)**

```python
# From: odoo/fields.py - Command class
# Command.create(vals)  - Create new related record
# Command.link(id)      - Link existing record
# Command.unlink(id)    - Unlink record (don't delete)
# Command.delete(id)    - Delete related record
# Command.update(id, vals) - Update related record
# Command.set(ids)      - Replace all with these IDs
# Command.clear()       - Remove all links

# Create order with order lines (One2many)
order = self.env['sale.order'].create({
    'partner_id': partner.id,
    'order_line': [
        Command.create({
            'product_id': 1,
            'product_uom_qty': 5,
            'price_unit': 10.0,
        }),
        Command.create({
            'product_id': 2,
            'product_uom_qty': 3,
            'price_unit': 20.0,
        }),
    ]
})

# Create with Many2many tags
product = self.env['product.product'].create({
    'name': 'My Product',
    'tag_ids': [
        Command.link(1),     # Link existing tag with id=1
        Command.link(2),     # Link existing tag with id=2
        Command.create({'name': 'New Tag'}),  # Create new tag
    ]
})

# Create with Many2many using set (replace all)
product = self.env['product.product'].create({
    'name': 'My Product',
    'tag_ids': [Command.set([1, 2, 3])]  # Link tags 1, 2, 3
})
```

### **Real-World Example**

```python
# From: addons/sale/models/sale_order.py
# Override create to auto-generate sequence
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if vals.get('name', _("New")) == _("New"):
            seq_date = fields.Datetime.context_timestamp(
                self, fields.Datetime.to_datetime(vals.get('date_order'))
            ) if vals.get('date_order') else None
            vals['name'] = self.env['ir.sequence'].with_company(
                vals.get('company_id')
            ).next_by_code('sale.order', sequence_date=seq_date) or _("New")
    
    return super().create(vals_list)
```

---

## ✏️ **3. WRITE - Updating Records**

**Purpose:** Update existing records

### **Basic Write**

```python
# From: odoo/orm/models.py (line 4334)
# write(vals) → returns True

# Update ONE partner
partner = self.env['res.partner'].browse(1)
partner.write({
    'email': 'newemail@example.com',
    'phone': '+9876543210'
})

# Shorthand (direct assignment) - ONLY for single record!
partner = self.env['res.partner'].browse(1)
partner.email = 'newemail@example.com'
partner.phone = '+9876543210'
```

### **Update Multiple Records**

```python
# Find multiple records and update them
orders = self.env['sale.order'].search([('state', '=', 'draft')])
orders.write({
    'state': 'cancel'
})
# Updates ALL draft orders to cancelled

# Update with loop (when values differ per record)
for order in orders:
    order.write({
        'note': f'Order {order.name} was processed'
    })
```

### **Update Many2one**

```python
# Change partner on order
order = self.env['sale.order'].browse(1)
new_partner = self.env['res.partner'].browse(5)

order.write({
    'partner_id': new_partner.id  # Many2one: use ID
})

# Shorthand
order.partner_id = new_partner
```

### **Update One2many/Many2many (Commands)**

```python
# Update order lines (One2many)
order = self.env['sale.order'].browse(1)

order.write({
    'order_line': [
        Command.create({'product_id': 1, 'product_uom_qty': 5}),  # Add new line
        Command.update(10, {'product_uom_qty': 10}),  # Update line id=10
        Command.delete(11),  # Delete line id=11
    ]
})

# Update tags (Many2many)
product = self.env['product.product'].browse(1)

product.write({
    'tag_ids': [
        Command.link(5),      # Add tag id=5
        Command.unlink(3),    # Remove tag id=3 (don't delete tag itself)
        Command.set([1,2,4]), # Replace all tags with 1,2,4
    ]
})

# Clear all tags
product.write({
    'tag_ids': [Command.clear()]
})

# Set specific tags (replace all)
product.write({
    'tag_ids': [Command.set([1, 2, 3])]
})
```

### **Command Reference**

| Command | One2many | Many2many | Description |
|---------|----------|-----------|-------------|
| `Command.create(vals)` | ✅ | ✅ | Create new related record |
| `Command.update(id, vals)` | ✅ | ❌ | Update related record |
| `Command.delete(id)` | ✅ | ❌ | Delete related record from DB |
| `Command.unlink(id)` | ✅ | ✅ | Remove link (don't delete) |
| `Command.link(id)` | ❌ | ✅ | Add link to existing record |
| `Command.set(ids)` | ✅ | ✅ | Replace all with these IDs |
| `Command.clear()` | ✅ | ✅ | Remove all links |

---

## 🗑️ **4. UNLINK - Deleting Records**

**Purpose:** Delete records from database

### **Basic Unlink**

```python
# From: odoo/orm/models.py (line 4194)
# unlink() → returns True

# Delete ONE partner
partner = self.env['res.partner'].browse(1)
partner.unlink()  # Record deleted from database!

# Delete MULTIPLE orders
orders = self.env['sale.order'].search([('state', '=', 'cancel')])
orders.unlink()  # All cancelled orders deleted
```

### **Safe Deletion with Checks**

```python
# From: addons/sale/models/sale_order.py
@api.ondelete(at_uninstall=False)
def _unlink_except_draft_or_cancel(self):
    for order in self:
        if order.state not in ('draft', 'cancel'):
            raise UserError(_(
                "You can only delete draft or cancelled orders!"
            ))

# This prevents deletion of confirmed orders
```

### **Using `active` Instead of Delete**

```python
# DON'T delete - archive instead!
partner.write({'active': False})
# or
partner.active = False

# Record still in database but hidden
# Can be restored: partner.active = True
```

**Best Practice:** Use `active=False` instead of `unlink()` to preserve history!

---

## 🔎 **5. BROWSE - Get Records by ID**

**Purpose:** Get recordset from known IDs

```python
# From: odoo/orm/models.py (line 5881)
# browse(ids) → returns recordset

# Get ONE record
partner = self.env['res.partner'].browse(1)
print(partner.name)

# Get MULTIPLE records
partners = self.env['res.partner'].browse([1, 2, 3])
for partner in partners:
    print(partner.name)

# Empty browse
empty = self.env['res.partner'].browse()
print(len(empty))  # 0
```

**Difference from search:**
- `browse(ids)` - You already know the IDs
- `search(domain)` - You need to find IDs matching conditions

---

## 🎨 **RECORDSET METHODS**

Recordsets have powerful methods for filtering, mapping, sorting:

### **`filtered()` - Filter Records**

```python
# From: addons/sale/models/sale_order.py
# Get only sale orders (not drafts)
confirmed_orders = self.filtered(lambda so: so.state == 'sale')

# Get only lines that are not downpayments
normal_lines = order.order_line.filtered(
    lambda line: not line.is_downpayment
)

# Get active partners
active_partners = partners.filtered(lambda p: p.active)

# Using field name (shorthand for boolean fields)
active_partners = partners.filtered('active')
```

### **`filtered_domain()` - Filter with Domain**

```python
# Filter recordset with domain (more efficient than lambda)
invoiceable_lines = order.order_line.filtered_domain([
    ('invoice_status', '=', 'to invoice'),
    ('display_type', '=', False)
])
```

### **`mapped()` - Extract Values**

```python
# Get list of names
names = partners.mapped('name')
# Result: ['John', 'Jane', 'Bob']

# Get list of IDs
ids = partners.mapped('id')
# Result: [1, 2, 3]

# Get related records (Many2one)
countries = partners.mapped('country_id')
# Result: recordset of countries

# Get through relationship
country_codes = partners.mapped('country_id.code')
# Result: ['US', 'UK', 'CA']

# Complex mapping
emails = partners.mapped(lambda p: p.email.lower() if p.email else '')
```

### **`sorted()` - Sort Records**

```python
# Sort by name
sorted_partners = partners.sorted(lambda p: p.name)

# Sort by name (shorthand)
sorted_partners = partners.sorted('name')

# Sort descending
sorted_partners = partners.sorted('name', reverse=True)

# Sort by multiple fields
sorted_orders = orders.sorted(lambda o: (o.date_order, o.name))
```

### **`exists()` - Check if Records Exist**

```python
# Check if records still exist in database
partners = self.env['res.partner'].browse([1, 2, 999])
existing = partners.exists()  # Returns only 1, 2 (999 doesn't exist)
```

### **`ensure_one()` - Ensure Single Record**

```python
# Raise error if not exactly ONE record
partner = self.env['res.partner'].search([('id', '=', 1)])
partner.ensure_one()  # OK if 1 record, error if 0 or >1

# Common in button methods
def action_confirm(self):
    self.ensure_one()  # Button methods expect single record
    self.state = 'confirmed'
```

### **Recordset Operations**

```python
# Union (combine)
all_partners = partners1 | partners2

# Intersection (common records)
common = partners1 & partners2

# Difference (in first, not in second)
unique = partners1 - partners2

# Check membership
if partner in partners:
    print("Found!")

# Length
count = len(partners)

# Boolean check (empty or not)
if partners:
    print("Has records")
else:
    print("Empty recordset")

# First record
first = partners[:1]  # Safe (returns empty if no records)
first = partners[0]   # DANGEROUS (error if empty)

# Last record
last = partners[-1:]  # Safe
```

---

## 🔥 **COMPLETE REAL-WORLD EXAMPLES**

### **Example 1: Create Order with Lines**

```python
def create_sample_order(self):
    # Find customer
    partner = self.env['res.partner'].search([
        ('name', '=', 'John Doe')
    ], limit=1)
    
    if not partner:
        # Create if doesn't exist
        partner = self.env['res.partner'].create({
            'name': 'John Doe',
            'email': 'john@example.com',
        })
    
    # Create order with lines
    order = self.env['sale.order'].create({
        'partner_id': partner.id,
        'date_order': fields.Datetime.now(),
        'order_line': [
            Command.create({
                'product_id': 1,
                'product_uom_qty': 5,
                'price_unit': 10.0,
            }),
            Command.create({
                'product_id': 2,
                'product_uom_qty': 2,
                'price_unit': 25.0,
            }),
        ]
    })
    
    return order
```

### **Example 2: Update Multiple Records**

```python
def cancel_old_draft_orders(self):
    # Find old draft orders
    cutoff_date = fields.Datetime.now() - timedelta(days=30)
    old_orders = self.env['sale.order'].search([
        ('state', '=', 'draft'),
        ('create_date', '<', cutoff_date)
    ])
    
    # Cancel them
    old_orders.write({'state': 'cancel'})
    
    return len(old_orders)
```

### **Example 3: Complex Search and Process**

```python
def process_pending_orders(self):
    # Find orders ready to invoice
    orders = self.env['sale.order'].search([
        ('state', '=', 'sale'),
        ('invoice_status', '=', 'to invoice')
    ])
    
    # Process each
    invoices_created = self.env['account.move']
    for order in orders:
        # Check if order has invoiceable lines
        invoiceable_lines = order.order_line.filtered(
            lambda l: l.qty_to_invoice > 0
        )
        
        if invoiceable_lines:
            invoice = order._create_invoices()
            invoices_created |= invoice  # Union operator
    
    return invoices_created
```

### **Example 4: Safe Record Access**

```python
def get_order_total(self, order_id):
    # Safe way to get record
    order = self.env['sale.order'].browse(order_id)
    
    # Check if exists
    if not order.exists():
        return 0.0
    
    # Ensure exactly one
    order.ensure_one()
    
    # Calculate total
    total = sum(order.order_line.mapped('price_subtotal'))
    
    return total
```

---

## 📊 **CRUD OPERATIONS SUMMARY**

| Operation | Method | Purpose | Returns |
|-----------|--------|---------|---------|
| **Create** | `create(vals)` | Add new records | New recordset |
| **Read** | `search(domain)` | Find records | Recordset matching domain |
| **Read** | `browse(ids)` | Get by IDs | Recordset with those IDs |
| **Update** | `write(vals)` | Modify records | True |
| **Delete** | `unlink()` | Delete records | True |

---

## 🎯 **RECORDSET METHODS SUMMARY**

| Method | Purpose | Example |
|--------|---------|---------|
| `filtered(func)` | Filter records | `orders.filtered(lambda o: o.state == 'draft')` |
| `filtered_domain(domain)` | Filter with domain | `lines.filtered_domain([('qty', '>', 0)])` |
| `mapped(field)` | Extract values | `partners.mapped('name')` |
| `sorted(key)` | Sort records | `partners.sorted('name')` |
| `exists()` | Check existence | `partner.exists()` |
| `ensure_one()` | Ensure single | `order.ensure_one()` |

---

## ⚡ **PERFORMANCE TIPS**

### **1. Batch Operations**
```python
# ❌ SLOW - creates one at a time
for data in dataset:
    self.env['model'].create(data)

# ✅ FAST - creates all at once
self.env['model'].create(dataset)
```

### **2. Use filtered_domain over filtered with lambda**
```python
# ❌ SLOWER - Python filtering
lines.filtered(lambda l: l.qty > 0 and l.price > 10)

# ✅ FASTER - Database filtering
lines.filtered_domain([('qty', '>', 0), ('price', '>', 10)])
```

### **3. Use mapped instead of loops**
```python
# ❌ SLOW
totals = []
for order in orders:
    totals.append(order.amount_total)

# ✅ FAST
totals = orders.mapped('amount_total')
```

### **4. Search with limit**
```python
# ❌ SLOW - loads all records
partners = self.env['res.partner'].search([])
if partners:
    first = partners[0]

# ✅ FAST - loads only one
partner = self.env['res.partner'].search([], limit=1)
if partner:
    ...
```

### **5. Use search_count for counting**
```python
# ❌ SLOW - loads all records
orders = self.env['sale.order'].search([('state', '=', 'draft')])
count = len(orders)

# ✅ FAST - just counts
count = self.env['sale.order'].search_count([('state', '=', 'draft')])
```

---

## ✅ **KEY TAKEAWAYS**

1. **self is ALWAYS a recordset** (can be 0, 1, or many records)
2. **search()** finds records by domain
3. **create()** adds new records (can create multiple at once)
4. **write()** updates existing records
5. **unlink()** deletes records (consider `active=False` instead)
6. **browse()** gets records by known IDs
7. **Use Commands** for One2many/Many2many in create/write
8. **filtered/mapped/sorted** are powerful recordset tools
9. **Batch operations** are much faster than loops
10. **Always check if recordset is empty** before accessing

---

## 🎯 **WHAT'S NEXT?**

Now you know:
- ✅ What recordsets are
- ✅ How to search for records (domains)
- ✅ How to create records (with relationships)
- ✅ How to update records (Commands)
- ✅ How to delete records safely
- ✅ How to filter, map, sort recordsets

**Next Topic:** API Decorators (`@api.depends`, `@api.onchange`, `@api.constrains`)

---

**Study Time:** 60-75 minutes  
**Practice:** Try CRUD operations in Python console  
**Real Files:** Check `addons/sale/models/sale_order.py` for real examples

