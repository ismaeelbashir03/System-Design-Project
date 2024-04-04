import type { RequestHandler } from './$types';
import { json, error } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { fullness } from '$lib/schema';

export const POST: RequestHandler = async ({ locals, request }) => {
	const { user } = locals;
	if (!user) throw error(403, 'Unauthorized');

	const { general, recycling } = await request.json();
	if (!general || !recycling) throw error(400, 'Missing fields');

	const [result] = await db
		.insert(fullness)
		.values({ id: 'full', general, recycling })
		.onConflictDoUpdate({ target: [fullness.id], set: { id: 'full', general, recycling } })
		.returning();

	return json(result);
};
