Copilot Instructions - Economy App (AI Optimized)

Version: 3.5
Mode: Incremental Enhancement (DO NOT REFACTOR EXISTING CODE)
Date: April 2026

--------------------------------------------------

0. CORE RULE (CRITICAL)

This is an EXISTING project (≈90% complete).

DO NOT:
- Rewrite existing modules
- Change architecture drastically
- Rename files unnecessarily
- Break working flows

DO:
- Extend existing code
- Reuse patterns already present
- Follow current structure
- Improve incrementally

If conflict:
→ FOLLOW EXISTING IMPLEMENTATION

--------------------------------------------------

1. SOURCE OF TRUTH

Database schema:

./er.sql

RULES:

- NEVER invent fields
- NEVER assume relations
- ALWAYS check er.sql
- Match SQLAlchemy models exactly

--------------------------------------------------

2. ARCHITECTURE (RESPECT EXISTING)

Current flow:

Router → UserService → BaseService → UserRepository → BaseRepository → DB

RULES:

- DO NOT skip layers
- DO NOT move logic between layers
- DO NOT refactor structure unless explicitly asked

--------------------------------------------------

3. SAFE EXTENSION RULE

When adding new functionality:

1. Check similar existing feature
2. Copy its structure
3. Adapt minimally

Priority:

EXISTING CODE > INSTRUCTIONS

--------------------------------------------------

4. SQLAlchemy RULES

- Use select()
- NEVER use .query()

- Reuse existing repositories
- Do NOT duplicate queries

Transactions:

- Respect existing session handling
- Use:

with session.begin():

ONLY where already consistent

--------------------------------------------------

5. SERVICE LAYER (STRICT)

- Business logic ONLY here
- Reuse BaseService if exists
- Do NOT duplicate logic already implemented

When adding logic:

CHECK:
- Is it already in another service?
→ reuse it

--------------------------------------------------

6. REPOSITORY LAYER

- DB access ONLY
- No validation
- No business logic

Reuse existing methods before creating new ones

--------------------------------------------------

7. CATEGORIZATION SYSTEM (DO NOT BREAK)

Current direction:

- Move logic to backend

RULES:

- If frontend rules exist → DO NOT delete blindly
- Replace gradually
- Maintain compatibility during transition

Flow:

rules → AI → null

--------------------------------------------------

8. IMPORT SYSTEM (CRITICAL - DO NOT BREAK)

- Existing import must continue working

Enhancements:

- Add transaction safety
- Add categorization step

BUT:

- Do NOT rewrite parser if already working
- Do NOT change file format handling

--------------------------------------------------

9. FRONTEND RULES (ANGULAR 21)

- DO NOT refactor entire frontend
- DO NOT migrate everything to signals if already mixed

INSTEAD:

- Use Signals in NEW components
- Keep existing components as-is

--------------------------------------------------

10. API CONTRACT (STRICT)

- DO NOT break existing endpoints
- DO NOT change response format if already used

Only:

- Extend responses
- Add optional fields

--------------------------------------------------

11. PERFORMANCE SAFE MODE

- Do NOT optimize prematurely
- Only fix:
  - clear N+1 issues
  - obvious inefficiencies

--------------------------------------------------

12. LOGGING

- Add logs only where missing
- Do NOT flood logs
- Follow existing logging style

--------------------------------------------------

13. ALEMBIC

- Only create new migrations
- NEVER modify old ones
- Ensure compatibility with current DB

--------------------------------------------------

14. SECURITY

Apply ONLY if missing:

- JWT validation
- Rate limiting
- Password hashing

Do NOT rewrite auth system if already working

--------------------------------------------------

15. ANTI-BREAKAGE RULES

Before generating code, ALWAYS:

1. Check if similar code exists
2. Reuse patterns
3. Avoid duplication
4. Maintain naming consistency

--------------------------------------------------

16. CODE GENERATION MODE

When asked to create something:

Follow this order:

1. Look for existing feature
2. Mirror structure
3. Reuse services/repositories
4. Only add missing pieces

--------------------------------------------------

17. DO / DON'T SUMMARY

DO:

- Extend existing code
- Reuse patterns
- Respect architecture
- Follow er.sql

DON'T:

- Rewrite modules
- Introduce new patterns globally
- Duplicate logic
- Break API

--------------------------------------------------

18. GOLDEN RULE

This is NOT a greenfield project.

Act as a senior developer joining an existing codebase:

- Understand first
- Modify carefully
- Improve incrementally

--------------------------------------------------

END