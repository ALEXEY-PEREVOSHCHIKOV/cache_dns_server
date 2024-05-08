from typeclasses.parser_typeclasses.record_a import RecordTypeA
from typeclasses.parser_typeclasses.record_aaaa import RecordTypeAAAA
from typeclasses.parser_typeclasses.record_answer import Answer
from typeclasses.parser_typeclasses.record_cname import RecordTypeCNAME
from typeclasses.parser_typeclasses.record_mx import RecordTypeMX
from typeclasses.parser_typeclasses.record_ns import RecordTypeNS
from typeclasses.parser_typeclasses.record_ptr import RecordTypePTR
from typeclasses.parser_typeclasses.record_soa import RecordTypeSoa
from utils.utils import parse_query, SEEK, TTL_OFFSET, RD_LENGTH_OFFSET, TYPE_RECORD, QNAME, CLASS_RECORD

def parse_answer(bits_stream: str, carrier: list, carrier_limit: int, init_seek: int) -> tuple[list, int]:
    seek = init_seek

    while len(carrier) < carrier_limit:
        parsed_answer = parse_query(bits_stream, seek)

        seek = parsed_answer[SEEK]
        ttl = int(bits_stream[seek: seek + TTL_OFFSET], 2)

        seek += TTL_OFFSET
        rd_length = int(bits_stream[seek: seek + RD_LENGTH_OFFSET], 2) * 8
        seek += RD_LENGTH_OFFSET
        rdata = bits_stream[seek: seek + rd_length]

        type_record = parsed_answer[TYPE_RECORD]

        if type_record == 'A':
            rdata = RecordTypeA(rdata)
        elif type_record == 'AAAA':
            rdata = RecordTypeAAAA(rdata)
        elif type_record == 'PTR':
            rdata = RecordTypePTR(bits_stream, seek)
        elif type_record == 'NS':
            rdata = RecordTypeNS(bits_stream, seek)
        elif type_record == 'SOA':
            rdata = RecordTypeSoa(bits_stream, seek)
        elif type_record == 'MX':
            rdata = RecordTypeMX(bits_stream, seek)
        elif type_record == 'CNAME':
            rdata = RecordTypeCNAME(bits_stream, seek)

        seek += rd_length

        answer = Answer(parsed_answer[QNAME], type_record, parsed_answer[CLASS_RECORD], ttl, rd_length, rdata)

        carrier.append(answer)

    return carrier, seek
