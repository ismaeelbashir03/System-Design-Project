import type { Config } from 'drizzle-kit';
import 'dotenv/config';

export default {
	schema: 'src/lib/schema.ts',
	out: './migrations',
	driver: 'pg',
	dbCredentials: {
		user: process.env.DATABASE_USER,
		password: process.env.DATABASE_PASSWORD,
		host: process.env.DATABASE_HOST!,
		port: Number(process.env.DATABASE_PORT),
		database: process.env.DATABASE_NAME!
	}
} satisfies Config;
