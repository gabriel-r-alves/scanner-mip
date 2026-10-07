import asyncio

# from dataclasses import dataclass

from monitoramento_impressoras_backend.utils.loggin import log_error, log_info
from monitoramento_impressoras_backend.domain.dtos import PrinterData, ScanResp
from monitoramento_impressoras_backend.domain.enums import ScanErrorType

from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi.asyncio import *


class ScanSnmp:
    def __init__(self, OID_MAP = None, community="public") -> None:
        self.OID_MAP = OID_MAP if OID_MAP is not None else {
            "1.3.6.1.2.1.43.5.1.1.17.1": "num_serial",
            "1.3.6.1.2.1.25.3.2.1.3.1": "model",
            "1.3.6.1.2.1.43.10.2.1.4.1.1": "counter"
        }
        self.engine = SnmpEngine()
        self.community = community
        

    async def async_snmp(
        self,
        ip,
        custom_oids: dict | None = None,
        timeout: float = 15.0,
        transport_timeout: float = 2.0,
        transport_retries: int = 1,
        max_attempts: int = 2,
        backoff_factor: float = 2.0
    ) -> ScanResp:
        """
        Executa uma consulta SNMP.

        Retorna:
            ScanResp:
                - success=True quando a coleta é realizada com sucesso.
                - success=False com o respectivo ScanErrorType em caso de erro.

        Não lança TimeoutError; o timeout é retornado como
        ScanErrorType.TIMEOUT.
        """
        oids = custom_oids if custom_oids else [
            '1.3.6.1.2.1.1.5.0',
            '1.3.6.1.2.1.43.5.1.1.17.1',
            '1.3.6.1.2.1.25.3.2.1.3.1',
            '1.3.6.1.2.1.43.10.2.1.4.1.1'
        ]

        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            log_info(f"[SNMP] {ip} attempt {attempt}/{max_attempts} (timeout={timeout}s transport_timeout={transport_timeout}s retries={transport_retries})")
            try:
                transport = await UdpTransportTarget.create(
                    (ip, 161),
                    timeout=transport_timeout,
                    retries=transport_retries
                )

                loop = asyncio.get_event_loop()
                start = loop.time()

                # get_cmd is an awaitable generator; wrap with asyncio.wait_for
                error_indication, error_status, error_index, var_binds = await asyncio.wait_for(
                    get_cmd(
                        self.engine,
                        CommunityData(self.community),
                        transport,
                        ContextData(),
                        *[ObjectType(ObjectIdentity(oid)) for oid in oids],
                        lookupNames=False,
                        lookupValues=False
                    ),
                    timeout=timeout
                )

                duration = loop.time() - start
                log_info(f"[SNMP] resposta de {ip} em {duration:.2f}s (attempt {attempt})")
                
                # protocolo SNMP retornou; checar status
                if error_indication:
                    msg = str(error_indication)
                    log_error(f"[SNMP] Erro SNMP em {ip}: {msg}")
        
                    if "timeout" in msg.lower():
                        error_type = ScanErrorType.TIMEOUT
                    else:
                        error_type = ScanErrorType.PROTOCOL_ERROR
        
                    return ScanResp(
                        success=False,
                        printer_data=None,
                        error=msg,
                        error_type=error_type
                    )
                    
                if error_status:
                    msg = error_status.prettyPrint()
                    log_error(f"[SNMP] Erro na resposta SNMP em {ip}: {msg}")
                    return ScanResp(
                        success=False,
                        printer_data=None,
                        error=msg,
                        error_type=ScanErrorType.PROTOCOL_ERROR
                    )

                # parse var_binds tolerante
                data = {}
                for oid, value in var_binds:
                    oid_str = str(oid)
                    field = self.OID_MAP.get(oid_str)
                    if field is None and oid_str.endswith('.0'):
                        field = self.OID_MAP.get(oid_str[:-2])
                    if field:
                        data[field] = str(value)

                if not data:
                    msg = "Nenhum dado SNMP obtido"
                    log_error(f"[SNMP] {msg} de {ip}")

                    return ScanResp(
                        success=False,
                        printer_data=None,
                        error=msg,
                        error_type=ScanErrorType.NO_DATA
                    )
                
                
                return ScanResp(
                    success=True,
                    printer_data=PrinterData(
                        num_serial=data.get('num_serial'),
                        model=data.get('model'),
                        counter=data.get('counter')
                    ),
                    error=None,
                    error_type=None
                )

            except asyncio.TimeoutError as e:
                log_error(f"[SNMP] Timeout no attempt {attempt} para {ip} (timeout={timeout}s)")
                if attempt < max_attempts:
                    backoff = (backoff_factor ** (attempt - 1))
                    sleep_for = min(backoff, 10.0)
                    log_info(f"[SNMP] aguardando {sleep_for:.1f}s antes da próxima tentativa para {ip}")
                    await asyncio.sleep(sleep_for)
                    continue
                else:
                    # último attempt: propagar TimeoutError para o service tratar como SCANNER_TIMEOUT
                    return ScanResp(
                        success=False,
                        printer_data=None,
                        error="Timeout ao consultar dispositivo SNMP",
                        error_type=ScanErrorType.TIMEOUT
                    )
                    
            except Exception as e:
                log_error(f"[SNMP] Erro crítico na conexão SNMP com {ip}: {e}")

                return ScanResp(
                    success=False,
                    printer_data=None,
                    error=str(e),
                    error_type=ScanErrorType.INTERNAL_ERROR
                )

