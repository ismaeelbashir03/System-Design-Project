import type { Actions, PageServerLoad } from './$types';
import { auth } from '$lib/server/auth';
import { fail, redirect } from '@sveltejs/kit';
import { Argon2id } from 'oslo/password';
import { db } from '$lib/server/db';
import { users } from '$lib/schema';

export const load: PageServerLoad = async ({ locals }) => {
	if (locals.user) throw redirect(302, '/');
};

export const actions: Actions = {
	default: async ({ request, cookies }) => {
		const formData = Object.fromEntries(await request.formData()) as Record<string, string>;
		const { username, password, confirm } = formData;

		if (username.length < 3 || username.length > 20 || !/^[a-z0-9_-]+$/.test(username))
			return fail(400, { message: 'Invalid username' });
		if (password !== confirm) return fail(400, { message: 'Passwords do not match' });

		const hashedPassword = await new Argon2id().hash(password);

		try {
			const [existingUser] = await db.select().from(users).limit(1);
			const admin = !existingUser;

			const [user] = await db.insert(users).values({ username, hashedPassword, admin }).returning();

			const session = await auth.createSession(user.id, {});
			const sessionCookie = auth.createSessionCookie(session.id);
			cookies.set(sessionCookie.name, sessionCookie.value, {
				path: '.',
				...sessionCookie.attributes
			});
		} catch (error) {
			return fail(400, { message: 'Username already taken' });
		}

		redirect(302, '/');
	}
};
