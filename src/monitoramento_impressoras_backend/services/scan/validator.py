class ScanValidator:
    def validate_printer(self, printer)-> tuple[bool, str|None]:
            validations = [
                (printer.ip is not None, "ip null"),
            ]
            
            for valid, error in validations:
                if not valid:
                    return (valid, error)
            
            return (True, None)
        
    