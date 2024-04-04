import type { RequestHandler } from './$types';
import { auth } from '$lib/server/auth';
import { redirect } from '@sveltejs/kit';

export const GET: RequestHandler = async ({ locals, cookies }) => {
	const { session } = locals;
	if (!session) throw redirect(302, '/login');
	await auth.invalidateSession(session.id);
	const sessionCookie = auth.createBlankSessionCookie();
	cookies.set(sessionCookie.name, sessionCookie.value, { path: '.', ...sessionCookie.attributes });
	throw redirect(302, '/login');
};
