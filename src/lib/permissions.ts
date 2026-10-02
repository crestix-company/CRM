import { OrganizationRole } from "@prisma/client";

export const Permission = {
  CRM_READ: "crm:read",
  CRM_WRITE: "crm:write",
  CRM_DELETE: "crm:delete",
  MANAGE_PIPELINES: "pipelines:manage",
  MANAGE_MEMBERS: "members:manage",
  MANAGE_ORGANIZATION: "organization:manage",
  MANAGE_CUSTOM_PROPERTIES: "custom-properties:manage",
  MANAGE_KPI: "kpi:manage",
  MANAGE_TARGETS: "targets:manage",
  MANAGE_BUSINESS_CALENDAR: "business-calendar:manage",
  MANAGE_PRODUCTS: "products:manage",
  MANAGE_SALES_SETTINGS: "sales-settings:manage",
  MANAGE_DELIVERY: "delivery:manage",
  VIEW_AUDIT_LOG: "audit:read",
  IMPORT_DATA: "data:import",
  EXPORT_DATA: "data:export",
  READ_ORGANIZATION_STRUCTURE: "organization-structure:read",
  MANAGE_ORGANIZATION_STRUCTURE: "organization-structure:manage",
  READ_HOSPITAL_PROFILE: "hospital-profile:read",
  WRITE_HOSPITAL_PROFILE: "hospital-profile:write",
  READ_APPROVAL: "approval:read",
  REVIEW_APPROVAL: "approval:review",
  APPROVE_APPROVAL: "approval:approve",
  DELEGATE_APPROVAL: "approval:delegate",
  MANAGE_APPROVAL: "approval:admin",
  VIEW_CONTRACT_PDF: "contract-pdf:view",
  DOWNLOAD_CONTRACT_PDF: "contract-pdf:download",
  PROPOSE_SYSTEM_CHANGE: "system-change:propose",
  APPROVE_SYSTEM_CHANGE: "system-change:approve",
} as const;

export type Permission = (typeof Permission)[keyof typeof Permission];

const rolePermissions: Record<OrganizationRole, ReadonlySet<Permission>> = {
  SUPER_ADMIN: new Set(Object.values(Permission)),
  ADMIN: new Set([
    Permission.CRM_READ,
    Permission.CRM_WRITE,
    Permission.CRM_DELETE,
    Permission.MANAGE_PIPELINES,
    Permission.MANAGE_MEMBERS,
    Permission.MANAGE_CUSTOM_PROPERTIES,
    Permission.MANAGE_KPI,
    Permission.MANAGE_TARGETS,
    Permission.MANAGE_BUSINESS_CALENDAR,
    Permission.MANAGE_PRODUCTS,
    Permission.MANAGE_SALES_SETTINGS,
    Permission.MANAGE_DELIVERY,
    Permission.VIEW_AUDIT_LOG,
    Permission.IMPORT_DATA,
    Permission.EXPORT_DATA,
    Permission.READ_ORGANIZATION_STRUCTURE,
    Permission.MANAGE_ORGANIZATION_STRUCTURE,
    Permission.READ_HOSPITAL_PROFILE,
    Permission.WRITE_HOSPITAL_PROFILE,
    Permission.READ_APPROVAL,
    Permission.REVIEW_APPROVAL,
    Permission.APPROVE_APPROVAL,
    Permission.DELEGATE_APPROVAL,
    Permission.MANAGE_APPROVAL,
    Permission.VIEW_CONTRACT_PDF,
    Permission.PROPOSE_SYSTEM_CHANGE,
  ]),
  MANAGER: new Set([
    Permission.CRM_READ,
    Permission.CRM_WRITE,
    Permission.MANAGE_PIPELINES,
    Permission.MANAGE_TARGETS,
    Permission.MANAGE_DELIVERY,
    Permission.IMPORT_DATA,
    Permission.EXPORT_DATA,
    Permission.READ_ORGANIZATION_STRUCTURE,
    Permission.READ_HOSPITAL_PROFILE,
    Permission.WRITE_HOSPITAL_PROFILE,
    Permission.READ_APPROVAL,
    Permission.REVIEW_APPROVAL,
    Permission.VIEW_CONTRACT_PDF,
    Permission.PROPOSE_SYSTEM_CHANGE,
  ]),
  USER: new Set([
    Permission.CRM_READ,
    Permission.CRM_WRITE,
    Permission.IMPORT_DATA,
    Permission.EXPORT_DATA,
    Permission.READ_HOSPITAL_PROFILE,
    Permission.READ_APPROVAL,
  ]),
  READ_ONLY: new Set([
    Permission.CRM_READ,
    Permission.EXPORT_DATA,
    Permission.READ_HOSPITAL_PROFILE,
    Permission.READ_APPROVAL,
  ]),
};

export function permissionsForRole(role: OrganizationRole): ReadonlySet<Permission> {
  return rolePermissions[role];
}

export function hasPermission(role: OrganizationRole, permission: Permission) {
  return permissionsForRole(role).has(permission);
}

export class AuthorizationError extends Error {
  constructor(message = "この操作を行う権限がありません。") {
    super(message);
    this.name = "AuthorizationError";
  }
}

export function requirePermission(
  role: OrganizationRole,
  permission: Permission,
) {
  if (!hasPermission(role, permission)) {
    throw new AuthorizationError();
  }
}
