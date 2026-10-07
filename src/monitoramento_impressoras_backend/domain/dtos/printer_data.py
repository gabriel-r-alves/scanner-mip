from dataclasses import dataclass

@dataclass
class PrinterData:
    num_serial: str | None = None
    model: str | None = None 
    counter: str | None = None

    
    @property
    def is_valid(self) -> bool:
        return bool(
            self.num_serial
            and self.num_serial.strip()
            and self.counter
            and self.counter.strip()
        )