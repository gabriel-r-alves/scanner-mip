import pandas as pd

from .loggin            import *
from monitoramento_impressoras_backend.repositories  import PrinterRepository, BranchRepository


class ExportData:
    def __init__(self, printers_repository=None, branch_repository=None) -> None:
        self.EXPORT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_exported')
        os.makedirs(LOG_DIR, exist_ok=True)
        
        self.printers_repository = printers_repository
        self.branch_repository = branch_repository


    def printers(self, output_path="data_exported/printers_data.xlsx"):
        if self.printers_repository is None:
            log_error(f"Repositório de impressoras não carregado ou com erro. {self.printers_repository}")
            return
        
        try:
            log_info("Iniciando exportação: Coletando dados do repositório...")
            printers_data = self.printers_repository.get_all_printers()

            if not printers_data:
                log_info("Nenhum dado encontrado para exportar.")
                return
            
            data_dict = []
            
            for p in printers_data:
                d = vars(p).copy()
                d.pop('_sa_instance_state', None)
                data_dict.append(d)

            df = pd.DataFrame(data_dict)
            
            # Exportando para Excel (também poderia ser .to_csv)
            df.to_excel(output_path, index=False, engine='openpyxl')
            
            log_info(f"Sucesso! Planilha '{output_path}' gerada com {len(df)} linhas.")
            return True

        except Exception as e:
            log_error(f"Erro ao exportar: {e}")


    def branches(self, output_path="data_exported/branches_data.xlsx"):
        if self.branch_repository is None:
            log_error(f"Repositório de filiais não carregado ou com erro. {self.branch_repository}")
            return
        try:
            log_info("Iniciando exportação: Coletando dados do repositório...")

            branches_data = self.branch_repository.get_all_branches()

            if not branches_data:
                log_info("Nenhum dado encontrado para exportar.")
                return
            
            data_dict = []
            
            for p in branches_data:
                d = vars(p).copy()
                d.pop('_sa_instance_state', None)
                data_dict.append(d)

            df = pd.DataFrame(data_dict)
            
            # Exportando para Excel (também poderia ser .to_csv)
            df.to_excel(output_path, index=False, engine='openpyxl')
            
            log_info(f"Sucesso! Planilha '{output_path}' gerada com {len(df)} linhas.")
            return True

        except Exception as e:
            log_error(f"Erro ao exportar: {e}")

