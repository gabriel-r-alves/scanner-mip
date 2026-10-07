import ipaddress

'''
    partes = ip_str.split('.') # Divide o IP em quatro partes (octetos)
    ip_int = 0
    for i, parte in enumerate(partes):
        # Converte a parte para inteiro e adiciona ao resultado
        # Multiplicamos por 256^ (3-i) ou deslocamos para a esquerda
        ip_int += int(parte) * (256**(3-i))
    return ip_int
    '''


def validating_ip(ip:str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def str_to_bin(ip: str) -> bytes:
    return ipaddress.ip_address(ip).packed

#-------------------------------------------
# reformular depois

def bin_to_str(value: bytes) -> str:

    return str(ipaddress.ip_address(value))

def bin_to_int(value:bytes) -> int:   
    return int(ipaddress.ip_address(value))

def int_to_str(value: int) -> str: 
    return str(ipaddress.ip_address(value))
#--------------------------------------------

