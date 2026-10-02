import { OrgNodeStatus, PermissionOverrideEffect } from "@prisma/client";
import type { AuthContext } from "./auth";
import {
  AuthorizationError,
  Permission as PermissionCatalog,
  type Permission,
  permissionsForRole,
} from "./permissions";
import { prisma } from "./prisma";

type ScopedOverride = {
  permission: string;
  effect: PermissionOverrideEffect;
  orgNodeId: string | null;
};

export type EffectiveAccess = {
  permissions: ReadonlySet<Permission>;
  accessibleOrgNodeIds: readonly string[];
  primaryOrgNodeId: string | null;
  legacyOrganizationWideScope: boolean;
  scopedOverrides: readonly ScopedOverride[];
  orgNodes: readonly { id: string; parentId: string | null }[];
};

const permissionValues = new Set<string>(Object.values(PermissionCatalog));

function isPermission(value: string): value is Permission {
  return permissionValues.has(value);
}

function permissionsFromJson(value: unknown): Permission[] {
  if (!Array.isArray(value)) return [];
  return value.filter(
    (item): item is Permission => typeof item === "string" && isPermission(item),
  );
}

function descendantsOf(
  roots: readonly string[],
  nodes: readonly { id: string; parentId: string | null }[],
) {
  const children = new Map<string, string[]>();
  for (const node of nodes) {
    if (!node.parentId) continue;
    const current = children.get(node.parentId) ?? [];
    current.push(node.id);
    children.set(node.parentId, current);
  }

  const result = new Set<string>();
  const queue = [...roots];
  while (queue.length) {
    const id = queue.shift();
    if (!id || result.has(id)) continue;
    result.add(id);
    queue.push(...(children.get(id) ?? []));
  }
  return result;
}

export async function getEffectiveAccess(
  context: AuthContext,
): Promise<EffectiveAccess> {
  const now = new Date();
  const organizationId = context.organization.id;

  const [memberships, overrides, nodes] = await Promise.all([
    prisma.orgNodeMembership.findMany({
      where: {
        organizationId,
        userId: context.user.id,
        validFrom: { lte: now },
        OR: [{ validTo: null }, { validTo: { gt: now } }],
        orgNode: { status: OrgNodeStatus.ACTIVE },
      },
      select: {
        orgNodeId: true,
        isPrimary: true,
        roleDefinition: { select: { permissions: true } },
      },
    }),
    prisma.userPermissionOverride.findMany({
      where: {
        organizationId,
        userId: context.user.id,
        validFrom: { lte: now },
        OR: [{ validTo: null }, { validTo: { gt: now } }],
      },
      select: { permission: true, effect: true, orgNodeId: true },
    }),
    prisma.orgNode.findMany({
      where: { organizationId, status: OrgNodeStatus.ACTIVE },
      select: { id: true, parentId: true },
    }),
  ]);

  const permissions = new Set<Permission>(permissionsForRole(context.membership.role));

  for (const membership of memberships) {
    for (const permission of permissionsFromJson(
      membership.roleDefinition?.permissions,
    )) {
      permissions.add(permission);
    }
  }

  // Global user exceptions apply here. Scoped overrides are evaluated against
  // a resource OrgNode in hasEffectivePermission().
  for (const override of overrides) {
    if (override.orgNodeId) continue;
    if (!isPermission(override.permission)) continue;
    if (override.effect === PermissionOverrideEffect.DENY) {
      permissions.delete(override.permission);
    } else {
      permissions.add(override.permission);
    }
  }

  const legacyOrganizationWideScope = memberships.length === 0;
  const roots = memberships.map((membership) => membership.orgNodeId);
  const accessible =
    context.membership.role === "SUPER_ADMIN" ||
    context.membership.role === "ADMIN" ||
    legacyOrganizationWideScope
      ? new Set(nodes.map((node) => node.id))
      : descendantsOf(roots, nodes);

  return {
    permissions,
    accessibleOrgNodeIds: [...accessible],
    primaryOrgNodeId:
      memberships.find((membership) => membership.isPrimary)?.orgNodeId ?? null,
    legacyOrganizationWideScope,
    scopedOverrides: overrides,
    orgNodes: nodes,
  };
}

function isSameOrDescendant(
  access: EffectiveAccess,
  ancestorId: string,
  nodeId: string,
) {
  if (ancestorId === nodeId) return true;
  const parentById = new Map(
    access.orgNodes.map((node) => [node.id, node.parentId] as const),
  );
  let current = parentById.get(nodeId) ?? null;
  while (current) {
    if (current === ancestorId) return true;
    current = parentById.get(current) ?? null;
  }
  return false;
}

function scopedOverrideFor(
  access: EffectiveAccess,
  permission: Permission,
  orgNodeId: string,
) {
  return access.scopedOverrides.filter(
    (override) =>
      override.permission === permission &&
      override.orgNodeId &&
      isSameOrDescendant(access, override.orgNodeId, orgNodeId),
  );
}

export async function hasEffectivePermission(
  context: AuthContext,
  permission: Permission,
  resource?: { orgNodeId?: string | null },
) {
  const access = await getEffectiveAccess(context);
  const orgNodeId = resource?.orgNodeId ?? null;

  if (orgNodeId) {
    if (!access.accessibleOrgNodeIds.includes(orgNodeId)) return false;
    const scoped = scopedOverrideFor(access, permission, orgNodeId);
    if (scoped.some((item) => item.effect === PermissionOverrideEffect.DENY)) {
      return false;
    }
    if (scoped.some((item) => item.effect === PermissionOverrideEffect.ALLOW)) {
      return true;
    }
  }

  return access.permissions.has(permission);
}

export async function requireEffectivePermission(
  context: AuthContext,
  permission: Permission,
  resource?: { orgNodeId?: string | null },
) {
  if (!(await hasEffectivePermission(context, permission, resource))) {
    throw new AuthorizationError();
  }
}
