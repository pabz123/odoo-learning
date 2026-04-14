# Exercise 05 - Security: Groups, ACLs, and Record Rules

## Goal

Practice Topic 7 by designing production-style security.

## Task

Create these files:

1. `security/library_security.xml`
2. `security/ir.model.access.csv`

## Groups to create

1. `library_training.group_library_user`
2. `library_training.group_library_manager`

Rules:

- manager group implies user group
- user group implies `base.group_user`

## ACL requirements

### `library.book`

- user: read only
- manager: full CRUD

### `library.borrowing`

- user: read/create/write, no unlink
- manager: full CRUD

## Record rule requirements

1. Multi-company rule for both models using `company_ids`
2. User rule: users can only see/edit borrowings where `create_uid = user.id` OR `borrower_id.user_ids` includes current user
3. Manager rule: manager sees all (`[(1, '=', 1)]`)
4. Portal/public should not get internal model access

## Advanced check

Set operation-specific rule permissions in at least one rule, e.g.:

- allow read
- deny write/create/unlink

## Deliverable

Send both files exactly as written in your solution.

I will grade for:

1. correctness of XML/CSV syntax
2. correct external IDs (`model_id`, `group_id`)
3. domain quality and safety
4. operation permission logic
