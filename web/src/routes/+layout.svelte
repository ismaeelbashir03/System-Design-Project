<script lang="ts">
	import type { LayoutServerData } from './$types';
	import 'tailwindcss/tailwind.css';

	export let data: LayoutServerData;
	$: user = data.user;
</script>

<header class="navbar">
	<div class="navbar-start">
		<a href="/" class="text-xl btn btn-ghost">
			<img src="/logo.png" alt="BinButler" class="w-6 h-6" />
			BinButler
		</a>
	</div>
	<div class="navbar-center"></div>
	<div class="navbar-end">
		{#if user}
			<div class="dropdown dropdown-end">
				<div tabindex="0" role="button" class="btn btn-secondary m-1">{user.username}</div>
				<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
				<ul
					tabindex="0"
					class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52"
				>
					{#if user.admin}
						<li><a href="/admin">Admin</a></li>
					{/if}
					<li><a href="/logout">Logout</a></li>
				</ul>
			</div>
		{:else}
			<a href="/login" class="btn btn-primary">Login</a>
		{/if}
	</div>
</header>

<main class="w-full max-w-6xl px-6 mx-auto flex flex-col flex-1">
	<slot />
</main>
