import { sqliteTable, text, integer, index, uniqueIndex } from 'drizzle-orm/sqlite-core';

export const sessions = sqliteTable('sessions', {
  id: text('id').primaryKey(), owner: text('owner').notNull(), instance: text('instance').notNull(),
  expires: integer('expires').notNull(), heartbeat: integer('heartbeat').notNull(),
  revoked: integer('revoked').notNull().default(0), scope: text('scope'),
  tools: text('tools').notNull().default('[]'), scopeVersion: integer('scope_version').notNull().default(0),
}, t => [index('sessions_owner').on(t.owner, t.expires)]);

export const requests = sqliteTable('requests', {
  id: text('id').primaryKey(), owner: text('owner').notNull(), session: text('session').notNull(),
  instance: text('instance').notNull(), scopeVersion: integer('scope_version').notNull(),
  scopeId: text('scope_id').notNull(), projectId: text('project_id').notNull(),
  name: text('name').notNull(), arguments: text('arguments').notNull(),
  callId: text('call_id').notNull(), fingerprint: text('fingerprint').notNull(),
  status: text('status').notNull(), claim: text('claim'), lease: integer('lease'),
  created: integer('created').notNull(), expires: integer('expires').notNull(), result: text('result'),
}, t => [uniqueIndex('requests_idempotency').on(t.owner, t.session, t.callId), index('requests_queue').on(t.owner, t.session, t.status, t.created)]);
