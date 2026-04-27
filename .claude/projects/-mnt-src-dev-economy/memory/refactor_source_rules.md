---
name: SourceRule Refactorization (Apr 27, 2026)
description: Separated source assignment logic from CategoryRule into dedicated SourceRule entity
type: project
---

## Summary

Refactored the categorization system by separating **source assignment** from **category matching**:

- **Before**: CategoryRule had a nullable `source_id` field (mixing concerns)
- **After**: 
  - CategoryRule: Only handles category matching via regex
  - SourceRule: Handles source suggestions (new table with FK to CategoryRule)

## Why

The original design had `source_id` directly on CategoryRule, which created problems:
- Nullable field = ambiguity
- One rule → one source (not flexible)
- Violates single responsibility principle
- Made it unclear when source is required vs optional

The new design:
- **Separated tables** = clear separation of concerns
- **One-to-many mapping** = one rule can have multiple sources (or none)
- **No nullability** = source_id either exists or the rule has no source suggestion
- **Scalable** = can easily extend with other attributes (priority, etc.)

## Implementation Details

### Backend Changes
- **Model**: Created `SourceRule` (api/models/category_rules/source_rule_model.py)
- **Schema**: Created schemas (api/schemas/category_rules/source_rule_schema.py)
- **Repository**: Created `SourceRuleRepository` with methods to query by category_rule_id
- **Service**: Created `SourceRuleService` with CRUD + validations
- **Router**: Created `source_rules_router` with full REST endpoints
- **Migration**: Alembic migration creates `source_rules` table

### CategorizationService Enhancement
Updated `categorize_transaction_with_flags()` to:
1. Match category rule (as before)
2. **NEW**: Fetch associated source_id from SourceRule
3. Return: `{category_id, source_id, ignore_in_analysis}`

### Frontend Changes
- Service: `SourceRuleService` (mirrors CategoryRuleService pattern)
- Component: `SourceRulesComponent` (full CRUD UI)
- Route: `/source_rules` added to app.routes.ts

## Data Migration Notes
- CategoryRule.source_id was NULL in the current schema (not yet deployed)
- No data migration needed (clean slate)
- If deploying to existing DB: run Alembic migration first

## Testing Endpoints
```
POST   /source_rules
GET    /source_rules
GET    /source_rules/<id>
GET    /source_rules/by_category_rule/<id>
PATCH  /source_rules/<id>
DELETE /source_rules/<id>
```

## Files Changed
- Backend: 7 files (new), 3 files (updated)
- Frontend: 4 files (new), 1 file (updated)
- Migration: 1 file (new)
