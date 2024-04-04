import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { maps, users, fullness, events } from '$lib/schema';
import { desc, eq, getTableColumns } from 'drizzle-orm';

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.user || !locals.user.admin) throw error(403, 'Unauthorized');

	const usersList = await db.select().from(users);
	const [map] = await db.select().from(maps).limit(1);

	const eventsList = await db
		.select({ ...getTableColumns(events), username: users.username })
		.from(events)
		.innerJoin(users, eq(events.userId, users.id))
		.orderBy(desc(events.createdAt))
		.limit(5);
	const [fullnessData] = await db.select().from(fullness).limit(1);

	return { users: usersList, map, events: eventsList, fullness: fullnessData };
};
