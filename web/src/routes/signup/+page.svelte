<script lang="ts">
	import type { ActionData } from './$types';
	import { enhance } from '$app/forms';

	export let form: ActionData;
</script>

<form method="post" use:enhance class="flex flex-col w-full max-w-2xl gap-4 m-auto">
	<h2 class="text-2xl font-bold">Sign Up</h2>

	<input type="text" name="username" placeholder="Username" class="input input-bordered" required />
	<input
		type="password"
		name="password"
		placeholder="Password"
		class="input input-bordered"
		required
	/>
	<input
		type="password"
		name="confirm"
		placeholder="Confirm Password"
		class="input input-bordered"
		required
	/>

	{#if form?.message}
		<div role="alert" class="alert alert-error">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				class="w-6 h-6 stroke-current shrink-0"
				fill="none"
				viewBox="0 0 24 24"
				><path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
				/></svg
			>
			<span>{form.message}</span>
		</div>
	{/if}

	<p>Already have an account? <a href="/login" class="link">Login</a></p>

	<button type="submit" class="btn btn-primary">Sign Up</button>
</form>
