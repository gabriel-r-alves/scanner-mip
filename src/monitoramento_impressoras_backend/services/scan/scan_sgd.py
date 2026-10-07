import socket
import asyncio

from monitoramento_impressoras_backend.domain.dtos import PrinterData, ScanResp
from monitoramento_impressoras_backend.domain.enums import ScanErrorType
from monitoramento_impressoras_backend.utils.loggin import log_error


class ScanSgd:
    def __init__(self):
        
        self.variables = {
            "num_serial": "device.unique_id", # ou "device.friendly_name"
            #"printer_status": "device.status", # status da impressora
            "counter": "odometer.total_label_count", # contador de etiquetas
            "model": "device.product_name" # modelo,
            # "print.tone", # darkness ou toner
            #"appl.name", # -> firmware completo ou #"appl.version" -> firmware versão 
            # "ezpl.print_width", # -> largura da etiqueta
            # "media.type",
            # "media.sense_mode",
            # "power.voltage",
            # "odometer.total_print_length",
            # "odometer.total_print_length_m",
            # "head.used",
            # "head.resistance",
             # status
            # "device.host_status",
            # "device.company_name" # nome da empresa -> zebra tecnologies 
            # "device.model"
        }
    
    
    async def async_collect(self, ip, port=9100, vars_list: dict|None=None, timeout: float = 5.0) -> ScanResp:
        try:
            if vars_list is None:
                vars_list = self.variables

            result = {}
            
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port),
                timeout=timeout
            )
            
            try:
                for key, sgd_var in vars_list.items():
                    command = f'! U1 getvar "{sgd_var}"\r\n'

                    writer.write(command.encode())
                    await writer.drain()

                    data = await asyncio.wait_for(
                        reader.read(1024),
                        timeout=timeout
                    )

                    response = data.decode(errors="ignore").strip().strip('"')

                    if response == "?":
                        response = None

                    result[key] = response

                    if not any(result.values()):
                        return ScanResp(
                            success=False,
                            printer_data=None,
                            error="Nenhum dado SGD obtido",
                            error_type=ScanErrorType.NO_DATA
                        )
                                   
                return ScanResp(
                    success=True,
                    printer_data=PrinterData(**result),
                    error=None,
                    error_type=None
                )
                
            finally:
                writer.close()
                await writer.wait_closed()
    
    
        except asyncio.TimeoutError:
            log_error(f"Timeout SGD {ip}:{port}")

            return ScanResp(
                success=False,
                printer_data=None,
                error="Timeout ao consultar dispositivo",
                error_type=ScanErrorType.TIMEOUT
            )
 
            
        except Exception as e:
            log_error(f"Erro SGD {ip}:{port}: {e}")

            return ScanResp(
                success=False,
                printer_data=None,
                error=str(e),
                error_type=ScanErrorType.INTERNAL_ERROR
            )
    
    

if __name__== "__main__":
    scan = ScanSgd()
    result = asyncio.run(scan.async_collect(ip="10.0.9.55"))
    print(result)
    result = asyncio.run(scan.async_collect(ip="10.0.5.55"))
    print(result)
    result = asyncio.run(scan.async_collect(ip="10.0.3.52"))
    print(result)