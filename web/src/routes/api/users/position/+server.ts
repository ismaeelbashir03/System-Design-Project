import type { RequestHandler } from './$types';
import { error, json } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { users } from '$lib/schema';
import { eq } from 'drizzle-orm';

export const POST: RequestHandler = async ({ request, locals }) => {
	const { user } = locals;
	if (!user) throw error(401, 'Unauthorized');
	const { position } = await request.json();

	const [updatedUser] = await db
		.update(users)
		.set({ position })
		.where(eq(users.id, user.id))
		.returning();

	return json({ ...updatedUser });
};
