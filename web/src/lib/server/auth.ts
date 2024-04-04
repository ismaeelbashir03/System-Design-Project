import { Lucia } from 'lucia';
import { dev } from '$app/environment';
import { db } from '$lib/server/db';
import { DrizzlePostgreSQLAdapter } from '@lucia-auth/adapter-drizzle';
import { users, sessions } from '$lib/schema';

const adapter = new DrizzlePostgreSQLAdapter(db, sessions, users);

export const auth = new Lucia(adapter, {
	sessionCookie: { attributes: { secure: !dev } },
	getUserAttributes: (user) => ({
		id: user.id,
		username: user.username,
		admin: user.admin,
		position: user.position
	})
});

declare module 'lucia' {
	interface Register {
		Lucia: typeof auth;
		DatabaseUserAttributes: typeof users.$inferSelect;
	}
}
