from enum import Enum

__RESP_MSGS__ = ["ERR_CODE = 0. No Error",
                 "ERR_CODE = 1. Connection Refused: Unacceptable protocol version",
                 "ERR_CODE = 2. Connection Refused: Identifier rejected",
                 "ERR_CODE = 3. Connection Refused: Server Unavailable",
                 "ERR_CODE = 4. Connection Refused: Bad username or password",
                 "ERR_CODE = 5. Connection Refused: Authorization erro",
                 "ERR_CODE = 6. Connection lost or bad",
                 "ERR_CODE = 7. Timeout waiting for Length bytes",
                 "ERR_CODE = 8. Timeout waiting for Payload",
                 "ERR_CODE = 9. Timeout waiting for CONNACK",
                 "ERR_CODE = 10. Timeout waiting for SUBACK",
                 "ERR_CODE = 11. Timeout waiting for UNSUBACK",
                 "ERR_CODE = 12. Timeout waiting for PINGRESP",
                 "ERR_CODE = 13. Malformed Remaining Length",
                 "ERR_CODE = 14. Problem with the underlying communication port",
                 "ERR_CODE = 15. Address could not be parsed",
                 "ERR_CODE = 16. Malformed received MQTT packet ",
                 "ERR_CODE = 17. Subscription failure",
                 "ERR_CODE = 18. Payload decoding failure",
                 "ERR_CODE = 19. Failed to compile a Decoder",
                 "ERR_CODE = 20. The received MQTT packet type is not supported on this client",
                 "ERR_CODE = 21. Timeout waiting for PUBACK",
                 "ERR_CODE = 22. Timeout waiting for PUBREC",
                 "ERR_CODE = 23. Timeout waiting for PUBCOMP"]


class MqttResponseCode(Enum):
    NO_ERROR = 0
    CONN_REFUSED = 1
    CONN_REFUSED_ID_REJECTED = 2
    CONN_REFUSED_SERVER_UNAVAILABLE = 3
    CONN_REFUSED_BAD_USER_PASS = 4
    CONN_REFUSED_AUTH_ERROR = 5
    CONN_LOST = 6
    LENGTH_BYTES_TIMEOUT = 7
    PAYLOAD_TIMEOUT = 8
    CONNACK_TIMEOUT = 9
    SUBACK_TIMEOUT = 10
    UNSUBACK_TIMEOUT = 11
    PINGRESP_TIMEOUT = 12
    MALFORMED_LENGTH = 13
    PROBLEM_PORT = 14
    ADDR_NOT_PARSED = 15
    MALFORMED_PACKET = 16
    SUB_FAILURE = 17
    PAYLOAD_DECO_FAILURE = 18
    COMPILE_DECODER_FAIL = 19
    PACKET_TYPE_NOT_SUPPORTED = 20
    PUBACK_TIMEOUT = 21
    PUBREC_TIMEOUT = 22
    PUBCOMP_TIMEOUT = 23

    def __str__(self):
        return __RESP_MSGS__[self.value]

    def __repr__(self):
        return f"MqttResponseCode[name = {self.name}, value = {self.value}]"

    def __eq__(self, other):
        if not isinstance(other, MqttResponseCode):
            return False
        return self.value == other.value
