import unittest

from dns_packets.dns_packet_creator import DNSCreator
from dns_packets.config_dns import DNSConfig
from typeclasses.creator_typeclasses import RecordTypeAAAA
from typeclasses import Query
from typeclasses import RecordTypeA
from typeclasses import RecordTypeCNAME
from typeclasses import Answer


class TestCreatorAnswer(unittest.TestCase):
    bytes_stream = b'e473818000010002000000000470696e6709617263686c696e7578036f72670000010001c00c0005000100000ae6000b087265646972656374c011c0300001000100000ae600045fd8c385'
    dns_config = DNSConfig()
    dns_config.ID = int('e473', 16)
    dns_config.QR = 1
    dns_config.OP_CODE = 0
    dns_config.AA = 0
    dns_config.TC = 0
    dns_config.RD = 1
    dns_config.RA = 1
    dns_config.Z = 0
    dns_config.RCODE = 0
    dns_config.ANCOUNT = 1
    dns_config.ARCOUNT = 0
    dns_config.NSCOUNT = 0
    dns_config.QDCOUNT = 1
    query = Query('ping.archlinux.org', 'A', 'IN')
    dns_config.QUERIES = [query]
    record_cname = RecordTypeCNAME('redirect.archlinux.org')
    record_a = RecordTypeA('95.216.195.133')
    record_aaaa = RecordTypeAAAA('ffff:0:0:0:0:0:0:0')
    answer1 = Answer('ping.archlinux.org', 'CNAME', 'IN', 2790, 11, record_cname)
    answer2 = Answer('redirect.archlinux.org', 'A', 'IN', 2790, 4, record_a)
    answer3 = Answer('ping.archlinux.org', 'AAAA', 'IN', 2790, 4, record_a)
    dns_config.ANSWERS = [answer2, answer3]

    def test_packet_creator_answer(self):
        self.maxDiff = None
        created_packet = hex(int(DNSCreator(self.dns_config).to_bin(), 2))[2:]
        print(created_packet)
        self.assertEqual(created_packet, bin(int(self.bytes_stream, 16))[2:])
