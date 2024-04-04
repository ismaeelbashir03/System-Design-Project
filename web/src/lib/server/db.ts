import { env } from '$env/dynamic/private';
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';

const client = postgres({
	username: env.DATABASE_USER,
	password: env.DATABASE_PASSWORD,
	host: env.DATABASE_HOST,
	port: Number(env.DATABASE_PORT),
	database: env.DATABASE_NAME
});

export const db = drizzle(client);
