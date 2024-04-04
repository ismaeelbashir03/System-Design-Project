<script lang="ts">
	import type { PageServerData } from './$types';
	import { onMount } from 'svelte';
	import { Socket } from '$lib/socket';
	import { WS_URL } from '$lib/config';

	export let data: PageServerData;
	let { users, map, fullness, events } = data;

	let canvas: HTMLCanvasElement;
	let socket: Socket;

	let showChangePositionModal = false;

	onMount(() => {
		socket = new Socket(WS_URL);

		socket.on('senseData', (data: { general: number, recycling: number }) => {
			fullness = {...fullness, ...data};
			fetch('/api/fullness', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(data)
			})
		});

		if (map) {
			const { width, height, depth, data: mapData, center } = map;
			drawMap(width, height, depth, mapData, center);
		}
	});

	const drawMap = (
		width: number,
		height: number,
		depth: number,
		mapData: number[][],
		center: number[] | null
	) => {
		const crops = {
			top: 125,
			right: 100,
			bottom: 180,
			left: 180
		};

		width -= crops.left + crops.right;
		height -= crops.top + crops.bottom;

		if (!canvas) return;
		canvas.width = width;
		canvas.height = height;

		const ctx = canvas.getContext('2d');
		if (!ctx) return;

		const imageData = ctx.createImageData(width, height);

		// Map data matrix array to image data array
		for (let y = 0; y < height; y++) {
			for (let x = 0; x < width; x++) {
				const i = (y * width + x) * 4;
				const value = mapData[y + crops.top][x + crops.left];
				if (value <= 0) {
					imageData.data[i] = 67;
					imageData.data[i + 1] = 1;
					imageData.data[i + 2] = 255;
					imageData.data[i + 3] = 255;
				} else {
					imageData.data[i] = 255;
					imageData.data[i + 1] = 255;
					imageData.data[i + 2] = 255;
					imageData.data[i + 3] = 255;
				}
			}
		}

		ctx.putImageData(imageData, 0, 0);

		if (center) {
			console.log(center);
			ctx.fillStyle = 'red';
			ctx.beginPath();
			ctx.rect(center[0] - crops.left, center[1] - crops.top, 2, 2);
			ctx.fill();
		}

		users.forEach((user) => {
			if (user.position) {
				const center = user.position;
				ctx.fillStyle = 'purple';
				ctx.beginPath();
				ctx.rect(center[0] - crops.left, center[1] - crops.top, 2, 2);
				ctx.fill();
			}
		});

		// add mouse event listener
		canvas.addEventListener('click', (e) => {
			ctx.putImageData(imageData, 0, 0);
			const rect = canvas.getBoundingClientRect();
			const scaleX = canvas.width / rect.width;
			const scaleY = canvas.height / rect.height;
			const x = (e.clientX - rect.left) * scaleX;
			const y = (e.clientY - rect.top) * scaleY;
			ctx.fillStyle = 'red';
			ctx.beginPath();
			ctx.rect(x, y, 2, 2);
			ctx.fill();

			// get position in map
			const mapX = x + crops.left;
			const mapY = y + crops.top;

			fetch('/api/maps/center', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ center: [mapX, mapY] })
			})
				.then((res) => res.json())
				.then(console.log);
		});
	};
</script>

<svelte:head>
	<title>Admin</title>
</svelte:head>

<button class="btn btn-primary my-2">Map Environment</button>
<button on:click={() => (showChangePositionModal = true)} class="btn btn-primary my-2"
	>Set Center</button
>

<div class="rounded-box bg-base-100 shadow border p-6 my-6 flex flex-col gap-4">
	<h2 class="text-2xl font-bold">Fullnesss</h2>

	<div class="flex items-center gap-4">
		<span class="w-24 font-bold">General</span>
		<progress class="h-5 progress progress-primary" value={fullness.general} max="100"></progress>
	</div>
	<div class="flex items-center gap-4">
		<span class="w-24 font-bold">Recycling</span>
		<progress class="h-5 progress progress-primary" value={fullness.recycling} max="100"></progress>
	</div>
</div>

<div class="rounded-box bg-base-100 shadow border p-6 my-6 flex flex-col gap-4">
	<h2 class="text-2xl font-bold">Events</h2>
	<table class="table my-4">
		<!-- head -->
		<thead>
			<tr>
				<th>User</th>
				<th>Action</th>
				<th>Date</th>
			</tr>
		</thead>
		<tbody>
			{#each events as { username, action, createdAt }, i}
				<tr>
					<td>{username}</td>
					<td>{action}</td>
					<td>{createdAt?.toDateString()}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<div class="rounded-box bg-base-100 shadow border p-6 my-6 flex flex-col gap-4">
	<h2 class="text-2xl font-bold">Users</h2>
	<table class="table my-4">
		<!-- head -->
		<thead>
			<tr>
				<th>Username</th>
				<th>Admin</th>
				<th>Joined</th>
			</tr>
		</thead>
		<tbody>
			{#each users as user, i}
				<tr>
					<td>{user.username}</td>
					<td>{user.admin ? 'Yes' : 'No'}</td>
					<td>{user.createdAt?.toDateString()}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<!-- Modals -->

<!-- Change Position -->
<dialog class="modal" class:modal-open={showChangePositionModal}>
	<div class="modal-box">
		<h3 class="font-bold text-lg">Change Position</h3>
		<canvas bind:this={canvas} class="w-full"></canvas>
		<div class="modal-action">
			<button on:click={() => (showChangePositionModal = false)} class="btn">Confirm</button>
		</div>
	</div>
</dialog>
