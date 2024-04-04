export class Socket {
	socket: WebSocket;
	events: Record<string, Function>;

	constructor(url: string) {
		this.socket = new WebSocket(url);
		this.socket.onclose = this.onClose.bind(this);
		this.socket.onmessage = this.onMessage.bind(this);
		this.events = {};
	}

	onClose() {
		console.log('socket closed');
	}

	onMessage(message: MessageEvent) {
		let { event, data } = JSON.parse(message.data);
		console.log('socket message', event, data);
		data = data[0] == '{' ? JSON.parse(data) : data;
		console.log(data);
		if (this.events[event]) this.events[event](data);
	}

	on(event: string, callback: Function) {
		this.events[event] = callback;
	}

	send(event: string, data: any) {
		this.socket.send(JSON.stringify({ event, data }));
	}

	close() {
		this.socket.close();
	}
}
