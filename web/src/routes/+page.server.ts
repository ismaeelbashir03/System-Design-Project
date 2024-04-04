import type { PageServerLoad } from './$types';
import { db } from '$lib/server/db';
import { maps } from '$lib/schema';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ locals }) => {
	const { user } = locals;
	if (!user) return redirect(302, '/login');
	const [map] = await db.select().from(maps).limit(1);
	return { map, user };
};
