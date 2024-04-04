import type { RequestHandler } from './$types';
import { json } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { maps } from '$lib/schema';

export const POST: RequestHandler = async ({ request }) => {
	const { center } = await request.json();

	const [map] = await db.update(maps).set({ center }).returning();

	return json({ ...map });
};
