import binascii
import logging
import os
import socket
from socket import SocketKind
from dotenv import load_dotenv
from cache import Cache
from dns_packets.config_dns import DNSConfig
from dns_packets.dns_packet_creator import DNSCreator
from dns_packets.dns_packet_parser import DNSParser
from typeclasses.creator_typeclasses.record_answer import Answer
from utils.utils_server import resolve_name
from utils.utils_dns_config import to_creator

TRANSPORT_PROTO_MAPPER = {'UDP': socket.SOCK_DGRAM, 'TCP': socket.SOCK_STREAM}

LOG_LEVEL_MAPPER = {'INFO': logging.INFO, 'DEBUG': logging.DEBUG, 'WARNING': logging.WARNING, 'ERROR': logging.ERROR,
                    'CRITICAL': logging.CRITICAL}
load_dotenv()

PORT = os.getenv('PORT') or 53

TRANSPORT: SocketKind = TRANSPORT_PROTO_MAPPER.get(os.getenv('TRANSPORT_PROTO')) or socket.SOCK_DGRAM

LOG_LEVEL = os.getenv('LOG_LEVEL') or logging.INFO

CACHE_FILE_SERIALIZE = os.getenv('CACHE_FILE') or 'cache.json'

IP_SERVER = os.getenv('IP_SERVER') or '127.0.0.1'

ROOT_DNS = os.getenv('ROOT_DNS') or '8.8.8.8'

logging.basicConfig(level=LOG_LEVEL, filename='server.log', filemode='a')

logging.info(f"Starting logging. PORT: {PORT}, TRANSPORT_PROTOCOL: {TRANSPORT}, LOG_LEVEL: {LOG_LEVEL}")


def main_loop(server_socket: socket, root_dns: str, cache: Cache):
    while True:
        data, addr = server_socket.recvfrom(1024)
        logging.info(f'{addr} connected')

        hex_data = binascii.b2a_hex(data)
        logging.info(f'read from {addr} : {hex_data}')

        query_packet: DNSParser = DNSParser(hex_data)

        for query in query_packet.queries_list:
            record_type = query.type_record
            class_type = query.class_record
            name_or_ip = query.qname
            record_cached = cache.get(name_or_ip, record_type)

            if record_cached:
                logging.info(f'{name_or_ip},{record_type} was get from cache')
                cached_dns_config = DNSConfig()
                cached_dns_config.from_parsed_packet(query_packet)
                cached_dns_config.ANSWERS.append(Answer(name_or_ip, record_type, class_type, record_cached[1], record_cached[0]))

                answer_dns = DNSCreator(cached_dns_config)
            else:
                record_cached = resolve_name(name_or_ip, record_type, class_type, root_dns)

                for answer in record_cached.answers_list:
                    rdata = to_creator(answer)
                    cache.push(name_or_ip, record_type, rdata, answer.ttl)

                logging.info(f'{name_or_ip},{record_type} was resolved from another dns_server')

                answer_dns_config = DNSConfig()
                answer_dns_config.from_parsed_packet(record_cached)
                answer_dns_config.ID = query_packet.id

                answer_dns = DNSCreator(answer_dns_config)

            answer_dns_encoded = answer_dns.to_bin()

            if len(answer_dns_encoded) % 2:
                answer_dns_encoded += '0'

            answer = bytes.fromhex(answer_dns_encoded)

            server_socket.sendto(answer, addr)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind((IP_SERVER, PORT))
        logging.info('Server is running, press ctrl+c to stop')
        cache: Cache = Cache()
        cache.from_json(CACHE_FILE_SERIALIZE)
        while True:
            try:
                main_loop(server, ROOT_DNS, cache)
            except KeyboardInterrupt as e:
                logging.info('Ctrl+C received, shutting down')
                cache.to_json(CACHE_FILE_SERIALIZE)
                break
            except Exception as e:
                logging.error(e)


if __name__ == '__main__':
    main()