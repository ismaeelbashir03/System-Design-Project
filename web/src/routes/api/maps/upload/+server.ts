import type { RequestHandler } from './$types';
import { json } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { maps } from '$lib/schema';

export const POST: RequestHandler = async ({ request }) => {
	const { width, height, depth, data, center } = await request.json();

	const [map] = await db
		.insert(maps)
		.values({
			width,
			height,
			depth,
			data,
			center
		})
		.returning();

	return json({ ...map });
};
