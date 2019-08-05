import socket
import uasyncio as asyncio
import network
import gc


class DNSQuery:
	def __init__(self, data):
		self.data = data
		self.domain = ''
		tipo = (data[2] >> 3) & 15  # Opcode bits
		if tipo == 0:  # Standard query
			ini = 12
			lon = data[ini]
			while lon != 0:
				self.domain += data[ini + 1:ini + lon + 1].decode('utf-8') + '.'
				ini += lon + 1
				lon = data[ini]
		print("searched domain:" + self.domain)

	def response(self, ip):

		print("Response {} == {}".format(self.domain, ip))
		if self.domain:
			packet = self.data[:2] + b'\x81\x80'
			packet += self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'  # Questions and Answers Counts
			packet += self.data[12:]  # Original Domain Name Question
			packet += b'\xC0\x0C'  # Pointer to domain name
			packet += b'\x00\x01\x00\x01\x00\x00\x00\x3C\x00\x04'  # Response type, ttl and resource data length -> 4 bytes
			packet += bytes(map(int, ip.split('.')))  # 4bytes of IP
		print(packet)
		return packet

# function to handle incoming dns requests
async def run_dns_server():

    udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # set non-blocking otherwise execution will stop at 'recvfrom' until a connection is received
    #  and this will prevent the other async threads from running
    udps.setblocking(False)

    # bind to port 53 on all interfaces
    udps.bind(('0.0.0.0', 53))

    while True:
        try:
            gc.collect()

            data, addr = udps.recvfrom(4096)
            print("Incoming data...")

            DNS = DNSQuery(data)
            udps.sendto(DNS.response(SERVER_IP), addr)

            print("Replying: {:s} -> {:s}".format(DNS.domain, SERVER_IP))

            await asyncio.sleep_ms(100)

        except Exception as e:
            print("Timeout")
            await asyncio.sleep_ms(3000)

    udps.close()

# function to handle incoming TCP connections
async def handle_client(reader, writer):
    try:
        gc.collect()

        data = await reader.read()

        message = data.decode()
        addr = writer.get_extra_info('peername')
        print('Received {} from {}'.format(message, addr))

        if len(message) > 0:
            response = 'HTTP/1.0 200 OK\r\n\r\n'

            # load the template and return it to the client
            with open('index.html') as f:
                response += f.read()

            yield from writer.awrite(response)

            yield from writer.aclose()

            print("client socket closed")

    except Exception as e:
        print('failed handling client: {}'.format(e))

    print('done with request from {}'.format(addr))



print('starting up!')

SERVER_IP = '10.0.0.1'
SERVER_SUBNET = '255.255.255.0'

# ssid max length is 32 chars
SERVER_SSID = 'myssid'

# setup the network
ap_if = network.WLAN(network.AP_IF)
ap_if.active(True)
ap_if.ifconfig((SERVER_IP, SERVER_SUBNET, SERVER_IP, SERVER_IP))
ap_if.config(essid=SERVER_SSID, authmode=network.AUTH_OPEN)


# create tasks for the web server and the DNS server and then start them
loop = asyncio.get_event_loop()
loop.create_task(asyncio.start_server(handle_client, "0.0.0.0", 80))
loop.create_task(run_dns_server())
loop.run_forever()
loop.close()