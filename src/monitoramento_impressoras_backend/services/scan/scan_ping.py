import aioping

async def async_scan_ping(ip) -> bool:
        try:
            await aioping.ping(ip, timeout=2)
            return True
        except TimeoutError:
            return False
        except Exception as e:
            print(f"ERRO NO PING para {ip}: {e}")
            return False

