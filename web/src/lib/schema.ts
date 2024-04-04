import { pgTable, text, timestamp, integer, boolean, real } from 'drizzle-orm/pg-core';
import { generateId } from 'lucia';

const createId = () => generateId(15);

export const users = pgTable('users', {
	id: text('id').primaryKey().$defaultFn(createId),
	username: text('username').notNull().unique(),
	hashedPassword: text('hashed_password').notNull(),
	admin: boolean('admin').notNull().default(false),
	position: real('position').array(),
	createdAt: timestamp('created_at', { withTimezone: true, mode: 'date' }).defaultNow()
});

export const sessions = pgTable('sessions', {
	id: text('id').primaryKey(),
	userId: text('user_id')
		.notNull()
		.references(() => users.id),
	expiresAt: timestamp('expires_at', {
		withTimezone: true,
		mode: 'date'
	}).notNull()
});

export const maps = pgTable('maps', {
	id: text('id').primaryKey().$defaultFn(createId),
	width: integer('width').notNull(),
	height: integer('height').notNull(),
	depth: integer('depth').notNull(),
	data: integer('data').array().array().notNull(),
	center: real('center').notNull().array()
});

export const fullness = pgTable('fullness', {
	id: text('id').primaryKey().$defaultFn(createId),
	general: real('general').notNull().default(0),
	recycling: real('recycling').notNull().default(0)
});

export const events = pgTable('events', {
	id: text('id').primaryKey().$defaultFn(createId),
	action: text('action').notNull(),
	userId: text('user_id')
		.notNull()
		.references(() => users.id),
	createdAt: timestamp('created_at', { withTimezone: true, mode: 'date' }).defaultNow()
});
