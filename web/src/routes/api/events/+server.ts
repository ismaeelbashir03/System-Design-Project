import type { RequestHandler } from './$types';
import { json, error } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { events } from '$lib/schema';

export const POST: RequestHandler = async ({ locals, request }) => {
	const { user } = locals;
	if (!user) throw error(403, 'Unauthorized');

	const { action } = await request.json();
	if (!action) throw error(400, 'Missing fields');

	const [result] = await db.insert(events).values({ action, userId: user.id }).returning();

	return json(result);
};
