# CRM-DB-02 — Major Relations / FK Audit

Status: Completed against `main` Prisma schema and relevant migration SQL.

Scope:
- Company
- Contact
- Deal
- Task
- MeetingBooking
- DeliveryProject
- DealLineItem
- DealParticipant
- Activity
- SalesPerformanceEvent
- DeliveryProjectItem
- DeliveryHandoff
- ObjectAssociation
- LegacySourceLink

Important:
- This audit is code/migration based.
- Production Supabase was not directly queried in this task.
- Existing IDs remain unchanged.
- New tables/domains follow the UUIDv7 policy.
- Chronological ordering continues to use `created_at` / `createdAt`.

---

## 1. Major relation map

```text
Organization
├─ BusinessUnit
│  ├─ Pipeline
│  │  └─ PipelineStage
│  └─ Deal
│
├─ Company
├─ Contact
├─ Deal
│  ├─ DealLineItem
│  └─ DealParticipant
│
├─ MeetingBooking
├─ Task
├─ Activity
├─ DeliveryProject
│  ├─ DeliveryProjectItem
│  ├─ DeliveryHandoff
│  ├─ DeliveryProjectStageHistory
│  └─ Task
│
├─ SalesPerformanceEvent
├─ ObjectAssociation
└─ LegacySourceLink
```

Business flow:

```text
Company / Contact
      │
      ▼
     Deal
      │
      ├─ DealLineItem
      ├─ DealParticipant
      └─ MeetingBooking (logical ID link)
      │
      ▼
DeliveryProject (logical sourceDealId link)
      │
      ├─ DeliveryProjectItem
      ├─ DeliveryHandoff
      └─ Task
```

KPI/event flow:

```text
Deal
MeetingBooking
DealLineItem
Referral
FieldVisit
      │
      ▼
SalesPerformanceEvent
      │
      ▼
KPI / Report
```

---

## 2. Strong DB relations (physical FK)

### Company
- `organizationId -> Organization.id` — CASCADE
- `ownerUserId -> User.id` — SET NULL

### Contact
- `organizationId -> Organization.id` — CASCADE
- `ownerUserId -> User.id` — SET NULL
- Reverse Prisma relations exist for FormSubmission / MeetingBooking / Conversation.

### Deal
- `organizationId -> Organization.id` — CASCADE
- `businessUnitId -> BusinessUnit.id` — SET NULL
- `ownerUserId -> User.id` — SET NULL
- `pipelineId -> Pipeline.id` — RESTRICT
- `stageId -> PipelineStage.id` — RESTRICT
- child: DealLineItem
- child: DealParticipant

### DealLineItem
- `organizationId -> Organization.id`
- `dealId -> Deal.id` — CASCADE
- `productId -> Product.id` — SET NULL
- `priceBookEntryId -> PriceBookEntry.id` — SET NULL

### DealParticipant
- `organizationId -> Organization.id`
- `dealId -> Deal.id` — CASCADE

### Task
- `organizationId -> Organization.id` — CASCADE
- `ownerUserId -> User.id` — RESTRICT
- `createdByUserId -> User.id` — RESTRICT
- `deliveryProjectId -> DeliveryProject.id` — CASCADE
- child: TaskReminder

### DeliveryProject children
- `DeliveryProjectItem.deliveryProjectId -> DeliveryProject.id` — CASCADE
- `DeliveryHandoff.deliveryProjectId -> DeliveryProject.id` — CASCADE
- `DeliveryProjectStageHistory.deliveryProjectId -> DeliveryProject.id` — CASCADE
- `Task.deliveryProjectId -> DeliveryProject.id` — CASCADE

### MeetingBooking
- `organizationId -> Organization.id` — CASCADE
- `meetingLinkId -> MeetingLink.id` — CASCADE
- `contactId -> Contact.id` — SET NULL

### Activity
- `organizationId -> Organization.id` — CASCADE
- `actorUserId -> User.id` — SET NULL

### ObjectAssociation
- `organizationId -> Organization.id` — CASCADE
- `sourceObjectId` / `targetObjectId` are intentionally polymorphic IDs and are not physical FK constraints.

### LegacySourceLink
- `organizationId -> Organization.id` — CASCADE
- target object is stored by type + ID rather than a physical FK.

---

## 3. Loose-coupling ID catalog

Definition in this document:
A UUID field used to reference another logical CRM entity, but not expressed as a Prisma `@relation` / physical FK in the current schema.

### Deal
- `forecastCategoryId`
- `primaryLossReasonId`
- `lostByUserId`
- `nextActionOwnerId`
- `originProjectId`
- `originDealId`

### Task
- `sourceDeliveryStageId`

### MeetingBooking
- `companyId`
- `businessUnitId`
- `dealId`
- `formSubmissionId`
- `bookingHoldId`
- `setByUserId`
- `hostUserId`
- `assignedUserId`
- `creditedAppointmentSetterId`
- `submittedByContactId`
- `territoryId`
- `industryId`
- `productId`
- `campaignId`
- `callListId`

### DeliveryProject
The model currently stores its upstream/master references as IDs without Prisma relations:
- `organizationId`
- `businessUnitId`
- `companyId`
- `primaryContactId`
- `sourceDealId`
- `templateId`
- `pipelineId`
- `stageId`
- `ownerUserId`
- `createdByUserId`
- `nextActionOwnerId`

Note: DeliveryProject has strong relations from its child tables, but its own upstream references are loosely coupled in the current Prisma model.

### DealLineItem
- `businessUnitId`
- `lossReasonId`

### DealParticipant
- `userId`

### Activity
- `deliveryProjectId`

### SalesPerformanceEvent
Only `organizationId` is a Prisma relation. The following IDs are deliberately/event-style loose references:
- `businessUnitId`
- `dealId`
- `dealLineItemId`
- `meetingBookingId`
- `referralId`
- `fieldVisitId`
- `metricDefinitionId`
- `creditedUserId`
- `territoryId`
- `industryId`
- `productId`
- `campaignId`
- `callListId`

### DeliveryProjectItem
- `organizationId`
- `businessUnitId`
- `sourceDealLineItemId`
- `productId`

### DeliveryHandoff
- `organizationId`
- `businessUnitId`
- `submittedByUserId`
- `assignedCsUserId`
- `acceptedByUserId`
- `rejectedByUserId`

### ObjectAssociation
- `sourceObjectId`
- `targetObjectId`

These are polymorphic by design and should stay loose unless the association model itself is replaced.

### LegacySourceLink
- `importJobId`
- `targetObjectId` is stored as String and is polymorphic/external-link style.

---

## 4. Relation risk classification

### A. Keep as strong FK
These are core aggregate ownership / hard integrity relations:
- Organization ownership
- BusinessUnit -> Deal / Pipeline classification
- Pipeline -> PipelineStage
- Deal -> DealLineItem
- Deal -> DealParticipant
- DeliveryProject -> child delivery records
- Task -> owner/creator
- MeetingBooking -> MeetingLink
- MeetingBooking -> Contact

### B. Keep loose by design
These are historical/event/polymorphic references where hard deletion blocking is usually undesirable:
- SalesPerformanceEvent source references
- ObjectAssociation source/target IDs
- LegacySourceLink target IDs
- event/audit snapshot style references

### C. Review before AIOS integration
These are business-critical links currently represented only by IDs and may deserve either:
1. physical FK, or
2. an explicit documented logical-reference contract.

High-priority review:
- MeetingBooking.companyId
- MeetingBooking.dealId
- MeetingBooking.businessUnitId
- DeliveryProject.companyId
- DeliveryProject.primaryContactId
- DeliveryProject.sourceDealId
- DeliveryProject.businessUnitId
- Deal.originProjectId
- Deal.originDealId
- DealParticipant.userId
- DeliveryProjectItem.sourceDealLineItemId

Recommendation: do not add FKs immediately. First confirm delete/retention semantics and whether historical records must survive source deletion.

---

## 5. AIOS / future Lead boundary

Future new domains must not write arbitrary IDs directly into existing CRM tables.

Preferred boundary:

```text
Clinic Master
   ↓
Clinic Lead / Lead Campaign
   ↓
explicit conversion/service
   ↓
CRM Company / Deal / MeetingBooking
   ↓
DeliveryProject
   ↓
AIOS reads events + aggregate state
```

For future external-domain links:
- use UUIDv7 for new table PKs;
- keep `created_at` authoritative for chronology;
- use explicit source-system + source-ID link records rather than copying external IDs into multiple CRM tables;
- do not reuse `LegacySourceLink` for new AIOS/Clinic Lead integration unless its legacy-workbook semantics are intentionally expanded by a separate migration/design decision.

---

## 6. Key observations

1. Company and Contact are not directly connected by a dedicated company-contact FK in the current models.
2. Deal also does not carry direct Company/Contact FK fields in the core Deal model; object-level linking can be handled through ObjectAssociation and workflow-specific IDs.
3. MeetingBooking contains many denormalized/logical IDs, but only Organization / MeetingLink / Contact are hard Prisma relations.
4. DeliveryProject acts as a CS aggregate and preserves many upstream CRM IDs without hard Prisma relations.
5. SalesPerformanceEvent is intentionally event-like and highly loosely coupled, which is suitable for immutable KPI attribution/history.
6. ObjectAssociation already provides a generic internal polymorphic association mechanism.
7. LegacySourceLink is import lineage, not the preferred generic future integration contract.

---

## 7. CRM-DB-02 completion criteria

- [x] Company relation/FK reviewed
- [x] Contact relation/FK reviewed
- [x] Deal relation/FK reviewed
- [x] Task relation/FK reviewed
- [x] MeetingBooking relation/FK reviewed
- [x] DeliveryProject relation/FK reviewed
- [x] major child aggregates reviewed
- [x] physical FK vs logical/loose ID separated
- [x] major Relation map completed
- [x] loose-coupling ID list completed
- [x] AIOS / future Lead boundary documented

Next recommended item:
**CRM-DB-03: verify the same structure against the actual Production Supabase schema/data and identify orphan IDs / FK drift / record counts.**
