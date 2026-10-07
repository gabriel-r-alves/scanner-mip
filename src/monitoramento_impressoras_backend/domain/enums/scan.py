from enum import StrEnum

class CollectorType(StrEnum):
    SNMP = "snmp"
    SGD = "sgd"
    PING = "ping"
    MANUAL= "manual"
    
    @property
    def requires_scan(self) -> bool:
        return self in {
            self.SNMP,
            self.SGD,
        }
    
    @property
    def requires_collector(self) -> bool:
        return self != self.MANUAL
    

class ConnectionStatus(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    SCANNER_ERROR = "scanner_error"
    INITIALIZED = "initialized"
    
    
class ScanStatus(StrEnum):
    INITIALIZED = "initialized"
    
    COLLECT_SUCCESS = "collect_success"
    PING_SUCCESS = "success"
    
    INVALID_SCANNER = "invalid_scanner"
    INVALID_RESPONSE = "invalid_response"
    INVALID_PRINTER = "invalid_printer"
    
    COLLECTION_NOT_REQUIRED = "collection_not_required" # scan ignora
    
    SCANNER_TIMEOUT = "scanner_timeout"
    PING_TIMEOUT = "ping_timeout"
    
    INTERNAL_ERROR = "internal_error"
    COLLECT_EMPTY = "collect_empty"


class ScanErrorType(StrEnum):
    SNMP_ERROR = "snmp_error"
    SGD_ERROR = "sgd_error"
    PROTOCOL_ERROR = "protocol_error"
    NO_DATA = "no_data"
    INTERNAL_ERROR = "internal_error"
    TIMEOUT = "timeout"    
    
