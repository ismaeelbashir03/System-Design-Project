import type { Actions, PageServerLoad } from './$types';
import { auth } from '$lib/server/auth';
import { fail, redirect } from '@sveltejs/kit';
import { Argon2id } from 'oslo/password';
import { db } from '$lib/server/db';
import { users } from '$lib/schema';
import { eq } from 'drizzle-orm';

export const load: PageServerLoad = async ({ locals }) => {
	if (locals.user) throw redirect(302, '/');
};

export const actions: Actions = {
	default: async ({ request, cookies }) => {
		const formData = Object.fromEntries(await request.formData()) as Record<string, string>;
		const { username, password } = formData;

		const [user] = await db.select().from(users).where(eq(users.username, username)).limit(1);
		if (!user) return fail(400, { message: 'Invalid username' });

		const validPassword = await new Argon2id().verify(user.hashedPassword, password);
		if (!validPassword) return fail(400, { message: 'Invalid password' });

		const session = await auth.createSession(user.id, {});
		const sessionCookie = auth.createSessionCookie(session.id);
		cookies.set(sessionCookie.name, sessionCookie.value, {
			path: '.',
			...sessionCookie.attributes
		});

		redirect(302, '/');
	}
};
