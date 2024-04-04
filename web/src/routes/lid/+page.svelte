<script lang="ts">
	import type { PageServerData } from './$types';
	import { Socket } from '$lib/socket';
	import { onMount } from 'svelte';
	import { WS_URL } from '$lib/config';

	export let data: PageServerData;
	$: ({ map, user } = data);

	// status can be home, moving, arrived or failed
	let showChangePositionModal = false;
	let showScanItemModal = false;
	let showSummonModal = false;
	let status = 'home';
	let queue: string[] = [];
	let classification = {
		requested: false,
		cup: false,
		material: '',
		recyclable: false
	};
	$: hasRequested = queue.includes(user?.username);
	let lidOpen = false;

	let canvas: HTMLCanvasElement;
	let socket: Socket;

	const materialToRecyclable = (material: string) => {
		switch (material) {
			case 'plastic':
				return true;
			case 'paper':
				return true;
			case 'metal':
				return true;
			case 'glass':
				return true;
			case 'cardboard':
				return true;
			case 'ewaste':
				return false;
			default:
				return false;
		}
	};

	const materialToDescription = (material: string) => {
		switch (material) {
			case 'plastic':
				return {
					description:
						'Plastic is a versatile and durable material made from petroleum-based products. It is widely used in various industries, from packaging to construction.',
					funFact:
						'Recycling just one ton of plastic bottles can energize an average American home for a whopping four months; talk about a light bulb moment!'
				};
			case 'paper':
				return {
					description:
						'Paper is a thin material made from plant fibers, primarily from trees. It is widely used for writing, printing, and packaging.',
					funFact:
						'Recycling a stack of newspapers just 3 feet high saves a tree. Think of it as trading paper skyscrapers for actual trees.'
				};
			case 'metal':
				return {
					description:
						'Metal is a solid material that is typically hard, malleable, and a good conductor of heat and electricity. Common metals include iron, aluminum, and copper.',
					funFact:
						"Aluminum can be recycled forever without losing quality. So that soda can you just drank from could have been part of a knight's armor in another life"
				};
			case 'glass':
				return {
					description:
						'Glass is a non-crystalline, amorphous solid material made from a mixture of silica, soda ash, and limestone. It is commonly used for containers, windows, and decorative objects.',
					funFact:
						'Glass recycling is so efficient, a bottle can go from a recycling bin back to the shelf in as little as 30 days. Speedy glass, indeed.'
				};
			case 'cardboard':
				return {
					description:
						'Cardboard is a thick, rigid material made from pulped recycled paper or kraft paper. It is commonly used for packaging and shipping boxes.',
					funFact:
						"If recycling cardboard feels like a chore, remember it only takes 75% of the energy needed to make new cardboard, so you're basically saving a quarter of your energy for Netflix binges"
				};
			case 'ewaste':
				return {
					description:
						'E-waste, or electronic waste, refers to discarded electrical or electronic devices, such as computers, televisions, and mobile phones.',
					funFact:
						"Every year, we toss out around 25 million metric tons of e-waste globally, making it the tech world's favorite unwanted child"
				};
			default:
				return {
					description: 'Material not recognized.',
					funFact:
						"Surprisingly, Americans throw away 25 billion Styrofoam coffee cups every year, enough to play a very depressing game of tower defense with our planet's health"
				};
		}
	};

	onMount(() => {
		socket = new Socket(WS_URL);
		// socket = new Socket('ws://localhost:8080/web');

		socket.on('status', (s: { status: string }) => {
			status = s.status;
		});

		socket.on(
			'wasteDetectionResult',
			({ cup, material, username }: { cup: boolean; material: string; username: string }) => {
				if (username !== user.username) return;
				classification = {
					...classification,
					cup,
					material,
					recyclable: materialToRecyclable(material)
				};
				if (classification.requested) showScanItemModal = true;
			}
		);

		socket.on('state', (state: { status: string; queue: string[] }) => {
			status = state.status;
			queue = state.queue;
		});

		if (map) {
			const { width, height, depth, data: mapData } = map;
			drawMap(width, height, depth, mapData);
		} else {
			socket.on(
				'getMap',
				(data: { width: number; height: number; depth: number; data: number[][] }) => {
					const { width, height, depth, data: mapData } = data;
					drawMap(width, height, depth, mapData);
					fetch('/api/maps/upload', {
						method: 'POST',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify({ width, height, depth, data: mapData, center: [0, 0] })
					});
				}
			);
			// request map from server
			socket.socket.onopen = () => {
				console.log('socket open');
				socket.send('getMap', '');
			};
		}
	});

	const drawMap = (width: number, height: number, depth: number, mapData: number[][]) => {
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
		if (user?.position) {
			const center = user.position;
			ctx.fillStyle = 'red';
			ctx.beginPath();
			ctx.rect(center[0] - crops.left, center[1] - crops.top, 2, 2);
			ctx.fill();
		}
		// add mouse event listener
		canvas.addEventListener('click', (e) => {
			const rect = canvas.getBoundingClientRect();
			const scaleX = canvas.width / rect.width;
			const scaleY = canvas.height / rect.height;
			const x = (e.clientX - rect.left) * scaleX;
			const y = (e.clientY - rect.top) * scaleY;
			const mapX = x + crops.left;
			const mapY = y + crops.top;

			// Throw error if the position is within radius of occupied pixel
			let radius = 4;
			for (let i = -radius; i <= radius; i++) {
				for (let j = -radius; j <= radius; j++) {
					if (mapData[Math.round(mapY) + i][Math.round(mapX) + j] <= 0) {
						alert('Position is too close to wall.');
						return;
					}
				}
			}

			ctx.putImageData(imageData, 0, 0);

			fetch('/api/users/position', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ position: [mapX, mapY] })
			});
			user.position = [mapX, mapY];
			ctx.putImageData(imageData, 0, 0);
			ctx.fillStyle = 'red';
			ctx.beginPath();
			ctx.rect(Math.round(x), Math.round(y), 2, 2);
			ctx.fill();
		});
	};

	const summon = (type: string) => {
		const { position } = user;
		if (!position) {
			alert('Please select a position on the map first.');
			return;
		}
		const { center } = map;
		if (!center) {
			alert('Map center not set. Contact admin.');
			return;
		}

		hasRequested = true;
		showSummonModal = false;

		// distances from center to position
		const x = (center[0] - position[0]) * -0.05;
		const y = (center[1] - position[1]) * 0.05;

		socket.send('summon', { type, x, y, user: user.username });

		fetch('/api/events', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ action: 'Summoned bin of type ' + type })
		});
	};

	const sendImage = async (e: Event) => {
		classification.requested = true;
		const files = (e.target as HTMLInputElement).files;
		if (!files) return;
		const file = files[0];
		// resize to 600x600
		const canvas = document.createElement('canvas');
		const ctx = canvas.getContext('2d');
		const image = new Image();
		image.src = URL.createObjectURL(file);
		image.onload = () => {
			canvas.width = 600;
			canvas.height = 600;
			ctx?.drawImage(image, 0, 0, 600, 600);
			const data = canvas.toDataURL('image/jpeg', 0.8);
			socket.send('detectWaste', { image: data, username: user.username });
		};

		fetch('/api/events', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ action: 'Requested waste detection' })
		});
	};
</script>

<svelte:head>
	<title>BinButler</title>
</svelte:head>

<div class="flex flex-col gap-4 grow py-1">
	<img src={`gifs/${status}.GIF`} alt="gif" class="rounded-box" />

	{#if hasRequested}
		<div><span class="font-bold">Status</span> {status}</div>
		<div>{queue.length} people in queue...</div>
		<button
			on:click={() => socket.send('done', '')}
			disabled={status != 'arrived' || queue[0] != user.username}
			class="btn btn-primary">Done</button
		>
	{:else}
		<button on:click={() => (showSummonModal = true)} class="btn btn-primary flex flex-col">
			<span>Request Bin</span>
			<span>{queue.length} people in queue</span>
		</button>

		<button on:click={() => (showChangePositionModal = true)} class="btn btn-primary"
			>Change Position</button
		>

		<div class="flex flex-col mt-auto">
			<span>Not sure which bin to use?</span>
			<input
				type="file"
				accept="image/*"
				capture="environment"
				on:input={sendImage}
				class="file-input file-input-bordered file-input-primary"
			/>
		</div>
	{/if}
</div>

<!-- MODALS -->

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

<!-- Summon Bin -->
<dialog class="modal" class:modal-open={showSummonModal}>
	<div class="modal-box flex flex-col gap-4">
		<h3 class="font-bold text-lg">Select what type of items you are disposing</h3>
		<button
			on:click={() => socket.send('testLid', { type: 'general', open: !lidOpen })}
			class="btn bg-red-500 text-white">General Waste</button
		>
		<button
			on:click={() => socket.send('testLid', { type: 'recycling', open: !lidOpen })}
			class="btn bg-green-500 text-white">Recycling</button
		>
		<button
			on:click={() => socket.send('testLid', { type: 'both', open: !lidOpen })}
			class="btn bg-blue-500 text-white">Both</button
		>
		<div class="modal-action">
			<button on:click={() => (showSummonModal = false)} class="btn">Cancel</button>
		</div>
	</div>
</dialog>

<!-- Scan Item -->
<dialog class="modal" class:modal-open={showScanItemModal}>
	<div class="modal-box flex flex-col gap-2">
		<h3 class="font-bold text-lg">
			Recyclable: <span
				class:text-green-500={classification.recyclable}
				class:text-red-500={!classification.recyclable}>{classification.recyclable}</span
			>
		</h3>
		{#if classification.cup}
			<p>
				It looks like you're recycling a cup! Make sure you check for plastic on the inside before
				you recycle.
			</p>
		{/if}
		<p>Material : {classification.material}</p>
		<p>Description : {materialToDescription(classification.material).description}</p>
		<p>Fun Fact : {materialToDescription(classification.material).funFact}</p>
		<div class="modal-action">
			<button on:click={() => (showScanItemModal = false)} class="btn">Close</button>
		</div>
	</div>
</dialog>
