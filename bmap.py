from random import randint
import threading
import socket
import struct
import json
import sys

MC_QUERY_MAGIC = b"\xFE\xFD"
MC_QUERY_HANDSHAKE = b"\x09"
MC_QUERY_STATISTICS = b"\x00"

def ping_minecraft_server(host, port):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        client.settimeout(2)
        client.connect((host, port))

        handshake = MC_QUERY_MAGIC + MC_QUERY_HANDSHAKE + struct.pack(">l", randint(1, 9999999))
        client.send(handshake)
        token = client.recv(65535)[5:-1].decode()

        if token:
            payload = b'\x00\x00\x00\x00'
            request_stat = MC_QUERY_MAGIC + MC_QUERY_STATISTICS + struct.pack(">l", randint(1, 9999999)) + struct.pack('>l', int(token)) + payload
            client.send(request_stat)
            buff = str(client.recv(65535)[5:])
            return parse_packet(packet=buff)
        else:
            return None
    except:
        return None

def parse_packet(packet):
    data = packet.split(r"\x01")
    packet_one = data[0].split(r'\x00')[2:-2]
    packet_two = data[1].split(r'\x00')[2:-2]
    host = {}

    for i in range(0, len(packet_one), 2):
        host[packet_one[i]] = packet_one[i + 1]

    host["players"] = packet_two

    return json.dumps(host, indent=4)

def scan_ports(host, ports):
    for port in ports:
        data = ping_minecraft_server(host, port)
        if data:
            print(f"Port {port}: {data}")

def main():

    host = sys.argv[1]
    begin_port = int(sys.argv[2])
    end_port = int(sys.argv[3])
    
    ports = range(begin_port, end_port) 
    num_threads = 100
    split_ports = [ports[i:i + num_threads] for i in range(0, len(ports), num_threads)]

    threads = []
    for ports_chunk in split_ports:
        thread = threading.Thread(target=scan_ports, args=(host, ports_chunk))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
