# Stage3 Core Foundation Schema

Status: **review only**. This PR must not be merged into production deployment until preview validation is complete.

## Scope

- OrgNode / RoleDefinition / OrgNodeMembership
- User permission overrides
- CorporateGroup / HospitalProfile
- Approval SLA / Request / Step / Action / Delegation
- AuditLog correlation and approval references

## Fixed decisions

- BusinessUnit remains the CRM operational unit; OrgNode is the hierarchy/permission unit.
- Multiple OrgNode memberships are allowed; exactly one active Primary membership per user/org.
- FS manager: 松岡.
- Amount change/discount: 松岡 review, 縞谷 final approval.
- Proxy approver: 前川.
- Major HR decision final approver: 縞谷.
- Important SLA: reminder after 4 hours; responsible-manager alert at 19:00 Asia/Tokyo.
- Urgent SLA: 1 minute reminder / 5 minute escalation.
- Normal SLA: 24 hour reminder / 48 hour overdue.

## UUID policy

New Stage3 domain entities intentionally have **no database UUID default** in Prisma.
Application services must provide UUIDv7 IDs.
Existing record IDs are never rewritten.

## Security guard

This schema PR does not change current public grants, Data API exposure, or RLS.
Those changes are intentionally separated because the current server application uses Prisma direct PostgreSQL access and must not be broken by a blanket RLS/GRANT change.

## Validation before merge

1. prisma validate
2. prisma generate
3. apply migration to isolated/preview database
4. rollback/recreate test
5. current CRM CRUD smoke test
6. verify partial unique Primary OrgNode index
7. run security advisor after preview migration
8. no production DB apply from this PR
