<script lang="ts">
	import { Socket } from '$lib/socket';

	let url: string;
	let event: string;
	let data: string;
	let connected: boolean = false;

	let socket: Socket;

	const connect = () => {
		socket = new Socket(url);
		socket.socket.onopen = () => {
			alert('Connected');
			connected = true;
		};
		socket.socket.onerror = (e) => {
			alert('Error: check console');
			console.error(e);
			connected = false;
		};
		socket.socket.onclose = () => {
			alert('Connection closed');
			connected = false;
		};
	};

	const send = () => {
		console.log('Sending', event, data);
		socket.send(event, data);
		alert(`Sent event: ${event}, data: ${data}`);
	};
</script>

{#if connected}
	<div class="flex flex-col gap-4">
		<input
			type="text"
			class="input input-bordered"
			placeholder="Event (string)"
			bind:value={event}
		/>
		<input
			type="text"
			class="input input-bordered"
			placeholder="Data (json string)"
			bind:value={data}
		/>
		<button class="btn btn-primary" on:click={send}>Send</button>
	</div>
{:else}
	<div class="flex flex-col gap-4">
		<input
			type="text"
			class="input input-bordered"
			placeholder="ws://192.168.XXX.XXX:PORT"
			bind:value={url}
		/>
		<button class="btn btn-primary" on:click={connect}>Connect</button>
	</div>
{/if}
