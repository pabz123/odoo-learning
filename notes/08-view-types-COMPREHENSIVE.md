# Topic 8: View Types in Odoo (Comprehensive)

## Scope of this topic

You are learning how Odoo displays model data in the UI using XML views.

This topic covers:

1. Form view
2. List view (tree)
3. Kanban view
4. Search view
5. Pivot view
6. Graph view
7. Calendar view
8. View inheritance (`inherit_id`, `xpath`, `position`)
9. `priority`, `mode`, and `arch`

---

## Core files studied

- `/home/precious/Desktop/odoo-19.0/addons/sale/views/sale_order_views.xml`
- `/home/precious/Desktop/odoo-19.0/addons/sale/report/sale_report_views.xml`
- `/home/precious/Desktop/odoo-19.0/addons/sale_margin/views/sale_order_views.xml`
- `/home/precious/Desktop/odoo-19.0/addons/project/views/project_task_views.xml`

---

## 1) What a view is in Odoo

A view is an `ir.ui.view` record with:

- `model`: which model it displays
- `arch` (XML architecture): how it displays it
- optional `inherit_id`: which existing view it extends

Basic pattern:

```xml
<record id="view_model_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form>
            ...
        </form>
    </field>
</record>
```

`arch` is the most important part: it is the actual XML layout.

---

## 2) How actions connect to views

Views are usually opened via window actions (`ir.actions.act_window`).

Example from sale:

```xml
<record id="action_orders" model="ir.actions.act_window">
    <field name="res_model">sale.order</field>
    <field name="view_mode">list,kanban,form,calendar,pivot,graph,activity</field>
</record>
```

This tells Odoo:

- model = `sale.order`
- available tabs/views = list, kanban, form, calendar, pivot, graph, activity

You can also force view ordering with `ir.actions.act_window.view` records and `sequence`.

---

## 3) Form view

Form view is for creating/updating one record.

From `sale_order_views.xml`:

- root tag: `<form>`
- common structure: `<header>`, `<sheet>`, `<notebook>`, `<chatter/>`

Example pattern:

```xml
<form string="Sales Order">
    <header>
        <button name="action_confirm" type="object" string="Confirm"/>
        <field name="state" widget="statusbar" statusbar_visible="draft,sent,sale"/>
    </header>
    <sheet>
        <group>
            <field name="partner_id"/>
            <field name="date_order"/>
        </group>
    </sheet>
    <chatter/>
</form>
```

### Form view features to know

1. Header buttons (`type="object"` or `type="action"`)
2. Statusbar widget for workflow state
3. Notebook pages (`<notebook><page>`)
4. Groups for layout (`<group>`)
5. Dynamic UI with `invisible`, `readonly`, `required`
6. Chatter integration (`<chatter/>`)

---

## 4) List view (tree)

In newer Odoo versions, XML tag is `<list>` (historically called tree view).

From sale:

```xml
<list string="Sales Orders" sample="1" decoration-muted="state == 'cancel'">
    <field name="name"/>
    <field name="date_order"/>
    <field name="partner_id"/>
    <field name="amount_total" widget="monetary" sum="Total Tax Included"/>
    <field name="state" widget="badge"/>
</list>
```

### List view features to know

1. `decoration-*` for conditional row styling
2. `optional="show/hide"` for user-column toggles
3. `sum`, `avg` on numeric columns
4. inline editing (`editable="top"` or `editable="bottom"`)
5. drag handle (`widget="handle"`)
6. activity widget in list (`widget="list_activity"`)

---

## 5) Kanban view

Kanban is card-based display, often grouped by stage/status.

From sale:

```xml
<kanban class="o_kanban_mobile" sample="1" quick_create="false">
    <field name="currency_id"/>
    <progressbar field="activity_state"
        colors='{"planned": "success", "today": "warning", "overdue": "danger"}'/>
    <templates>
        <t t-name="card">
            <field name="partner_id"/>
            <field name="amount_total" widget="monetary"/>
            <field name="state" widget="label_selection"/>
        </t>
    </templates>
</kanban>
```

### Kanban features to know

1. `<templates>` with QWeb card template (`t-name="card"`)
2. `progressbar` for visual grouped status
3. card widgets like badges, activity icons, monetary
4. `quick_create`, `records_draggable`, `group_create` control behavior
5. attributes can be inherited/modified using `position="attributes"`

---

## 6) Search view

Search view controls filters, search fields, and group-by options.

From sale:

```xml
<search string="Search Sales Order">
    <field name="name" filter_domain="['|', ('name', 'ilike', self), ('client_order_ref', 'ilike', self)]"/>
    <field name="partner_id" operator="child_of"/>
    <filter name="my_sale_orders_filter" string="My Orders" domain="[('user_id', '=', uid)]"/>
    <group>
        <filter name="salesperson" string="Salesperson" context="{'group_by': 'user_id'}"/>
        <filter name="customer" string="Customer" context="{'group_by': 'partner_id'}"/>
    </group>
</search>
```

### Search view features to know

1. `<field>` with `filter_domain`
2. `<filter>` with static `domain`
3. date filters (`date="field_name"`)
4. group-by filters via `context="{'group_by': 'field'}"`
5. separators and nested groups for cleaner UX
6. `searchpanel` (seen in some modules) for side filtering

---

## 7) Pivot view

Pivot is multidimensional aggregation/analysis.

From sale:

```xml
<pivot string="Sales Orders" sample="1">
    <field name="date_order" type="row"/>
    <field name="amount_total" type="measure"/>
</pivot>
```

From sale report:

```xml
<pivot string="Sales Analysis" sample="1">
    <field name="team_id" type="col"/>
    <field name="date" interval="month" type="row"/>
    <field name="product_uom_qty" type="measure"/>
</pivot>
```

### Pivot features to know

1. `type="row"`, `type="col"`, `type="measure"`
2. date interval grouping: `interval="day|week|month|quarter|year"`
3. works best with stored/groupable fields
4. often used with report models (`sale.report`, `account.move.line`, etc.)

---

## 8) Graph view

Graph is visual analytics (bar/line/pie).

From sale:

```xml
<graph string="Sales Orders" sample="1">
    <field name="partner_id"/>
    <field name="amount_total" type="measure"/>
</graph>
```

From sale report:

```xml
<graph string="Sales Analysis" type="line" sample="1">
    <field name="date" interval="month"/>
    <field name="product_uom_qty" type="measure"/>
</graph>
```

### Graph features to know

1. `type="bar|line|pie"`
2. measures marked with `type="measure"`
3. group dimensions are regular `<field>` entries
4. can be inherited to switch chart type (example in sale report pie/bar variants)

---

## 9) Calendar view

Calendar displays records on timeline/month/week/day.

From sale:

```xml
<calendar string="Sales Orders" mode="month" date_start="activity_date_deadline" color="state" event_limit="5" quick_create="0">
    <field name="partner_id"/>
    <field name="amount_total" widget="monetary"/>
</calendar>
```

From project tasks:

```xml
<calendar date_start="date_deadline" string="Tasks" mode="month" ... />
```

### Calendar features to know

1. `date_start` is required
2. optional `date_stop` for duration events
3. `color` groups visual event colors
4. `event_limit` controls max visible events per day cell
5. `quick_create` toggles quick add behavior

---

## 10) View inheritance (critical for real modules)

You usually extend existing views instead of rewriting them.

## A) Inherit by `inherit_id`

```xml
<record id="my_view_inherit" model="ir.ui.view">
    <field name="model">sale.order</field>
    <field name="inherit_id" ref="sale.view_order_form"/>
    <field name="arch" type="xml">
        ...
    </field>
</record>
```

## B) Use `xpath` and `position`

From `sale_margin`:

```xml
<xpath expr="//field[@name='order_line']//list//field[@name='price_unit']" position="after">
    <field name="purchase_price"/>
</xpath>
```

From project views:

```xml
<xpath expr="//field[@name='project_id']" position="attributes">
    <attribute name="invisible">True</attribute>
</xpath>
```

### Common `position` values

1. `inside`
2. `before`
3. `after`
4. `replace`
5. `attributes`

`attributes` is heavily used to change existing element properties without replacing full blocks.

---

## 11) `mode`, `priority`, and primary view variants

You will see:

- `<field name="mode">primary</field>`
- `<field name="priority">...</field>`

### What they do

1. `mode="primary"` can define alternative "main" variants for same base view (used in sale graph pie/bar variants and search/list variants).
2. `priority` helps resolve order/selection when multiple inherited/primary variants exist.
3. Lower and higher priorities influence application order; use carefully when many modules inherit same base view.

---

## 12) `arch` details and best practices

`arch` is XML, so:

1. must be valid XML
2. escape symbols properly (`&lt;`, `&gt;`, `&amp;`)
3. field names must exist on model
4. avoid huge full-copy view overrides; prefer surgical `xpath`

### Good pattern

- inherit base view
- add only your needed fields/buttons
- avoid replacing entire large blocks

---

## 13) Real-world action + view stack pattern

From project and sale, the standard stack is:

```text
view_mode: kanban,list,form,calendar,pivot,graph,activity
```

Then explicit `ir.actions.act_window.view` records control tab order:

1. kanban
2. list
3. form
4. calendar
5. pivot
6. graph
7. activity

This gives better UX than relying on implicit default ordering.

---

## 14) Common mistakes (and fixes)

## Mistake 1: Wrong root tag or invalid XML

Fix: validate XML syntax and correct root (`form`, `list`, `kanban`, etc.).

## Mistake 2: Field not found in view

Fix: confirm field exists in model and module dependency is loaded.

## Mistake 3: XPath not matching any node

Fix: inspect final inherited view and make xpath more stable/precise.

## Mistake 4: Heavy replace of full sections

Fix: prefer small `position="after"` or `position="attributes"` patches.

## Mistake 5: Security mismatch in views

Fix: apply `groups` where needed and ensure ACL/rules support the view.

## Mistake 6: Loading order issues

Fix: manifest should load base views before menu entries; inherited views after their parents.

---

## 15) Mini reference snippets by type

## Form

```xml
<form>
    <header>...</header>
    <sheet>...</sheet>
    <notebook>...</notebook>
    <chatter/>
</form>
```

## List

```xml
<list editable="bottom" decoration-muted="state == 'cancel'">
    <field name="name"/>
</list>
```

## Kanban

```xml
<kanban>
    <templates><t t-name="card">...</t></templates>
</kanban>
```

## Search

```xml
<search>
    <field name="name"/>
    <filter name="mine" domain="[('user_id', '=', uid)]"/>
</search>
```

## Pivot

```xml
<pivot>
    <field name="date" type="row" interval="month"/>
    <field name="amount_total" type="measure"/>
</pivot>
```

## Graph

```xml
<graph type="bar">
    <field name="team_id"/>
    <field name="amount_total" type="measure"/>
</graph>
```

## Calendar

```xml
<calendar date_start="date_deadline" color="user_id"/>
```

---

## 16) Practice tasks for this topic

1. Create `library.book` list, form, and search views.
2. Add kanban with custom card showing title + author + status badge.
3. Add calendar for borrowings using `due_date`.
4. Add graph/pivot for borrowings by state and month.
5. Create inherited view that inserts one new field using `xpath`.

---

## 17) Key takeaways

1. Views are `ir.ui.view` records with XML `arch`.
2. Actions (`ir.actions.act_window`) decide which views are available.
3. Use `list` for tabular data, `form` for editing, `kanban` for card workflows.
4. `search` controls filters/group-by UX.
5. `pivot` and `graph` are analytics views.
6. `calendar` is timeline-based planning.
7. Real customization is mostly view inheritance with `xpath`.
8. Keep overrides small and stable.

---

## Next topic in the learning path

After View Types, continue with:

- `automated-actions` (automation/server actions), then
- `external-api` (integration)
