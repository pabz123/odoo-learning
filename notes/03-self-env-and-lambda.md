# Understanding self.env and Lambda Functions in Odoo

## 📚 TABLE OF CONTENTS
1. What is self.env?
2. self.env Components
3. Accessing Models with self.env
4. Context and self.env.context
5. Lambda Functions in Odoo
6. Practical Examples

---

## 🎯 PART 1: What is self.env?

### The Simple Answer

`self.env` is your **gateway to everything in Odoo**. Think of it as your **control panel** that gives you access to:
- 🗄️ All models (database tables)
- 👤 Current user
- 🏢 Current company
- 🔧 Configuration
- 💾 Database cursor
- 📦 Context (settings/variables)

**Simple analogy:** If Odoo is a huge library, `self.env` is the librarian who can get you ANY book!

---

### The Technical Definition

`self.env` is an **Environment object** that holds:
- The database cursor (cr)
- The current user (uid)
- The context (context)
- The registry (all models)

```python
# self.env structure
self.env = Environment(cr, uid, context)
```

Where:
- **cr** = Database cursor (connection to PostgreSQL)
- **uid** = User ID (which user is doing this action)
- **context** = Dictionary of settings/variables

---

## 🔍 PART 2: self.env Components

### 1. **self.env.cr** - Database Cursor

The direct connection to the PostgreSQL database.

**When to use:**
- Execute raw SQL (rare, only for performance)
- Manual transaction control
- Database-specific operations

**Example:**

```python
# Execute raw SQL query
self.env.cr.execute("""
    SELECT name, email FROM res_partner 
    WHERE country_id = %s
""", (country_id,))

results = self.env.cr.fetchall()
# results = [('John Doe', 'john@example.com'), ('Jane Smith', 'jane@example.com')]

# Commit changes manually (usually automatic)
self.env.cr.commit()
```

**⚠️ Warning:** Use ORM instead of raw SQL when possible! Raw SQL bypasses:
- Security rules
- Access rights
- Computed fields
- Triggers

---

### 2. **self.env.uid** - Current User ID

The ID of the user performing the action.

**Example:**

```python
# Get current user ID
current_user_id = self.env.uid
print(current_user_id)  # 2

# Get current user record
current_user = self.env.user
print(current_user.name)      # 'Administrator'
print(current_user.email)     # 'admin@example.com'
print(current_user.company_id.name)  # 'My Company'

# Check if current user is admin
if self.env.uid == 1:  # User ID 1 is always admin
    print("You are admin!")
```

---

### 3. **self.env.user** - Current User Record

Shortcut to get the current user as a record (instead of just ID).

**Example:**

```python
# Access current user information
user = self.env.user

print(user.name)              # User's name
print(user.login)             # Login username
print(user.email)             # Email
print(user.partner_id.phone)  # Phone (from partner)
print(user.company_id.name)   # Company name

# Check user groups
if user.has_group('sales_team.group_sale_manager'):
    print("User is Sales Manager!")

# Create record assigned to current user
order = self.env['sale.order'].create({
    'partner_id': customer.id,
    'user_id': self.env.user.id,  # Assigned to current user
})
```

---

### 4. **self.env.company** - Current Company

Get the current company (for multi-company setups).

**Example:**

```python
# Get current company
company = self.env.company

print(company.name)        # 'My Company Inc.'
print(company.currency_id.name)  # 'USD'
print(company.email)       # 'info@mycompany.com'
print(company.country_id.name)   # 'United States'

# Use in defaults
class SaleOrder(models.Model):
    _name = 'sale.order'
    
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company  # ← Current company
    )
```

---

### 5. **self.env.context** - Context Dictionary

A dictionary that stores temporary settings, variables, and flags.

**What is context?**
- Like "session variables"
- Passed between methods
- Controls behavior
- Temporary (not stored in DB)

**Example:**

```python
# Read context
context = self.env.context
print(context)
# {
#     'lang': 'en_US',
#     'tz': 'America/New_York',
#     'uid': 2,
#     'allowed_company_ids': [1],
#     'active_id': 5,
#     'active_model': 'sale.order',
# }

# Access specific context value
lang = self.env.context.get('lang')  # 'en_US'
active_id = self.env.context.get('active_id')  # 5

# Check if key exists
if 'active_id' in self.env.context:
    print("Active ID exists!")
```

---

### 6. **self.env.ref()** - Get Record by XML ID

Get a specific record by its XML ID (external identifier).

**Example:**

```python
# Get the admin user
admin = self.env.ref('base.user_admin')
print(admin.name)  # 'Administrator'

# Get a specific group
sales_manager_group = self.env.ref('sales_team.group_sale_manager')
print(sales_manager_group.name)  # 'Sales Manager'

# Get a record and use it
uom_unit = self.env.ref('uom.product_uom_unit')
product = self.env['product.template'].create({
    'name': 'New Product',
    'uom_id': uom_unit.id,  # Use the Unit of Measure
})
```

---

## 🗄️ PART 3: Accessing Models with self.env

### The Main Pattern: self.env['model.name']

**This is how you access ANY model in Odoo!**

```python
# Syntax
self.env['model.technical.name']

# Examples
self.env['sale.order']        # Sales Orders
self.env['res.partner']       # Customers/Companies
self.env['product.template']  # Products
self.env['account.move']      # Invoices
self.env['stock.picking']     # Warehouse transfers
self.env['hr.employee']       # Employees
```

---

### Common Operations with self.env

#### **1. CREATE - Add new record**

```python
# Create a customer
customer = self.env['res.partner'].create({
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '1234567890',
    'is_company': False,
})
print(customer.id)  # 42 (new record ID)
```

#### **2. SEARCH - Find records**

```python
# Find all customers in New York
customers = self.env['res.partner'].search([
    ('city', '=', 'New York'),
    ('customer_rank', '>', 0),
])
print(len(customers))  # 15

# Find one record
customer = self.env['res.partner'].search([
    ('email', '=', 'john@example.com')
], limit=1)
```

#### **3. BROWSE - Get record by ID**

```python
# Get customer with ID 42
customer = self.env['res.partner'].browse(42)
print(customer.name)  # 'John Doe'

# Get multiple records by IDs
customers = self.env['res.partner'].browse([42, 43, 44])
for customer in customers:
    print(customer.name)
```

#### **4. SEARCH_COUNT - Count records**

```python
# Count customers in New York
count = self.env['res.partner'].search_count([
    ('city', '=', 'New York'),
    ('customer_rank', '>', 0),
])
print(count)  # 15
```

---

### Real-World Examples

#### **Example 1: Create Sales Order with Lines**

```python
def create_sale_order(self):
    # Get customer
    customer = self.env['res.partner'].search([
        ('name', '=', 'John Doe')
    ], limit=1)
    
    # Get products
    product1 = self.env['product.product'].search([
        ('name', '=', 'Laptop')
    ], limit=1)
    
    product2 = self.env['product.product'].search([
        ('name', '=', 'Mouse')
    ], limit=1)
    
    # Create order
    order = self.env['sale.order'].create({
        'partner_id': customer.id,
        'date_order': fields.Datetime.now(),
        'order_line': [
            (0, 0, {  # Create new line
                'product_id': product1.id,
                'product_uom_qty': 1,
                'price_unit': 1000.0,
            }),
            (0, 0, {  # Create another line
                'product_id': product2.id,
                'product_uom_qty': 2,
                'price_unit': 25.0,
            }),
        ],
    })
    
    return order
```

#### **Example 2: Send Email to All Managers**

```python
def notify_managers(self):
    # Get Sales Manager group
    manager_group = self.env.ref('sales_team.group_sale_manager')
    
    # Get all users in that group
    managers = self.env['res.users'].search([
        ('groups_id', 'in', manager_group.id)
    ])
    
    # Send email to each
    for manager in managers:
        self.env['mail.mail'].create({
            'subject': 'Important Notification',
            'body_html': '<p>Hello, this is important!</p>',
            'email_to': manager.email,
        }).send()
```

---

## 📦 PART 4: Context in Detail

### What is Context Used For?

1. **Language/Localization**
2. **Time Zone**
3. **Passing Data Between Methods**
4. **Controlling Behavior**
5. **Default Values**

---

### Reading Context

```python
def my_method(self):
    # Get entire context
    ctx = self.env.context
    
    # Get specific value (safe way)
    lang = ctx.get('lang', 'en_US')  # Default to 'en_US'
    active_id = ctx.get('active_id')
    
    # Check if key exists
    if 'active_model' in ctx:
        model_name = ctx['active_model']
```

---

### Setting Context

**Method 1: with_context() - Add/Modify Keys**

```python
# Add new context key
new_self = self.with_context(custom_key='custom_value')

# Multiple keys
new_self = self.with_context(
    lang='fr_FR',
    tz='Europe/Paris',
    custom_flag=True,
)

# Use new context
result = new_self.some_method()
```

**Method 2: with_context() - Replace Entire Context**

```python
# Replace entire context
new_self = self.with_context({
    'lang': 'es_ES',
    'active_id': 42,
})
```

**Method 3: Pass in Function Call**

```python
# Pass context when calling
result = self.env['sale.order'].with_context(
    lang='de_DE'
).search([])
```

---

### Context Examples

#### **Example 1: Change Language**

```python
# Get product name in English
product = self.env['product.product'].browse(1)
print(product.name)  # 'Computer'

# Get product name in French
product_fr = product.with_context(lang='fr_FR')
print(product_fr.name)  # 'Ordinateur'

# Get product name in Spanish
product_es = product.with_context(lang='es_ES')
print(product_es.name)  # 'Computadora'
```

#### **Example 2: Skip Email Notifications**

```python
# Normal way - sends email
order.action_confirm()

# Skip email - use context flag
order.with_context(mail_notrack=True).action_confirm()
```

#### **Example 3: Set Default Values**

```python
# When creating from UI, pass default values via context
def action_create_order(self):
    return {
        'type': 'ir.actions.act_window',
        'res_model': 'sale.order',
        'view_mode': 'form',
        'context': {
            'default_partner_id': self.partner_id.id,
            'default_date_order': fields.Date.today(),
        },
    }
```

---

## 🔧 PART 5: Lambda Functions in Odoo

### What is Lambda?

**Lambda** = Anonymous function (function without a name)

**Regular function:**
```python
def get_current_company(self):
    return self.env.company

# Use it
company_id = fields.Many2one('res.company', default=get_current_company)
```

**Lambda (anonymous):**
```python
# Same as above, but inline
company_id = fields.Many2one(
    'res.company',
    default=lambda self: self.env.company
)
```

---

### Why Use Lambda in Odoo?

**Problem:** Field defaults need to be dynamic (calculated at runtime).

**Wrong way:**
```python
# ❌ This evaluates ONCE when module loads
company_id = fields.Many2one('res.company', default=self.env.company)
# Error! self doesn't exist at class definition time
```

**Right way:**
```python
# ✅ This evaluates EVERY TIME a record is created
company_id = fields.Many2one(
    'res.company',
    default=lambda self: self.env.company
)
```

---

### Lambda Syntax

```python
lambda arguments: expression

# Examples:
lambda x: x + 1                    # Add 1 to x
lambda x, y: x * y                 # Multiply x and y
lambda self: self.env.company      # Return current company
lambda self: fields.Date.today()   # Return today's date
```

**Same as:**
```python
def function_name(arguments):
    return expression
```

---

### Common Lambda Uses in Odoo

#### **1. Default Current User**

```python
class SaleOrder(models.Model):
    _name = 'sale.order'
    
    user_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        default=lambda self: self.env.user
    )
```

**What happens:**
```python
# When you create a new order
order = self.env['sale.order'].create({
    'partner_id': customer.id,
    # user_id is automatically set to current user!
})
print(order.user_id.name)  # 'Administrator' (whoever created it)
```

---

#### **2. Default Current Company**

```python
class SaleOrder(models.Model):
    _name = 'sale.order'
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
```

---

#### **3. Default Today's Date**

```python
class SaleOrder(models.Model):
    _name = 'sale.order'
    
    date_order = fields.Date(
        string='Order Date',
        default=lambda self: fields.Date.today()
    )
    
    # Or for Datetime
    date_time = fields.Datetime(
        string='Order DateTime',
        default=lambda self: fields.Datetime.now()
    )
```

---

#### **4. Default from Context**

```python
class SaleOrder(models.Model):
    _name = 'sale.order'
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        default=lambda self: self.env.context.get('default_partner_id')
    )
```

**Usage:**
```python
# Create order with default customer from context
order = self.env['sale.order'].with_context(
    default_partner_id=42
).create({
    'name': 'New Order',
    # partner_id automatically set to 42!
})
```

---

#### **5. Default from Method**

```python
class SaleOrder(models.Model):
    _name = 'sale.order'
    
    name = fields.Char(
        string='Order Reference',
        default=lambda self: self._get_default_name()
    )
    
    def _get_default_name(self):
        # Generate sequence number
        return self.env['ir.sequence'].next_by_code('sale.order') or 'New'
```

---

#### **6. Default Computed Value**

```python
class Task(models.Model):
    _name = 'project.task'
    
    user_id = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user
    )
    
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.user.company_id
    )
    
    date_deadline = fields.Date(
        string='Deadline',
        default=lambda self: fields.Date.today() + timedelta(days=7)
    )
```

---

### Lambda vs Regular Function

**Use Lambda when:**
- ✅ Simple one-line expression
- ✅ Default value for fields
- ✅ Don't need to reuse the logic

**Use Regular Function when:**
- ✅ Complex logic (multiple lines)
- ✅ Need to reuse in multiple places
- ✅ Need proper function name for clarity

**Example - Lambda is good:**
```python
company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
```

**Example - Regular function is better:**
```python
def _get_default_warehouse(self):
    """Get default warehouse for current user."""
    user = self.env.user
    if user.property_warehouse_id:
        return user.property_warehouse_id
    else:
        return self.env['stock.warehouse'].search(
            [('company_id', '=', user.company_id.id)], 
            limit=1
        )

warehouse_id = fields.Many2one(
    'stock.warehouse',
    default=_get_default_warehouse
)
```

---

## 🎓 KEY TAKEAWAYS

### self.env
1. **Gateway to everything** - All models, users, companies, DB
2. **self.env['model.name']** - Access any model
3. **self.env.user** - Current user
4. **self.env.company** - Current company
5. **self.env.context** - Temporary settings/flags
6. **self.env.ref('xml.id')** - Get specific record

### Lambda
1. **Anonymous function** - Function without name
2. **Used for defaults** - Dynamic default values
3. **Syntax:** `lambda self: expression`
4. **Common:** Current user, company, date
5. **Alternative:** Regular function for complex logic

---

**Ready to practice writing models?** Let me know and we'll create practice exercises!
