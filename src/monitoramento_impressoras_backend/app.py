import asyncio
import sys
import signal
import schedule
import time

from datetime import date, datetime, timedelta

from monitoramento_impressoras_backend.database.session import SessionLocal

from monitoramento_impressoras_backend.services import ScanService, SyncService, ReportService, DailyCountersService

from monitoramento_impressoras_backend.utils.loggin import log_info, log_error

from monitoramento_impressoras_backend.utils.export import ExportData

from monitoramento_impressoras_backend.repositories import (
    PrinterRepository,
    BranchRepository,
    BranchNetworkRepository,
    ErrorCounterRepository,
    RawCounterRepository,
    DailyCounterRepository,
    LogChangePrinterRepository,
    PositionRepository
)


# sudo ip neigh del 192.168.0.146 dev enp0s3 -> para resetar o ip-
def limpar_log():
    # try:
    with open('src/monitoramento_impressoras_backend/logs/monitoramento.log', 'w'): pass # limpa o log


def handle_exit(signum, frame):
    '''
    Função chamada pelo sistema operacional (ou pelo seu .sh)10.0
    para encerrar o programa de forma limpa.
    '''
    log_info(f'\n⚠️ Sinal de encerramento ({signum}) recebido.')
    log_info('Finalizando tarefas e fechando o sistema com segurança...')
    # O sys.exit garante que o Python pare, mas o Lock no ScanService
    # protege as transações que estiverem em curso no exato momento.
    sys.exit(0)


def run_sync(scan_data_list):
    log_info('[AUTO] Iniciando a sincronização...')    

    with SessionLocal() as session:
        try:
            printer_repository = PrinterRepository(session)
            counters_repository = RawCounterRepository(session)
            errors_repository = ErrorCounterRepository(session)
            logs_repository = LogChangePrinterRepository(session)
            position_repository = PositionRepository(session)
            
            sync_service = SyncService(
                printers_repository=printer_repository,
                counters_repository=counters_repository,
                errors_repository=errors_repository,
                logs_repository=logs_repository,
                position_repository=position_repository 
            )
            
            sync_service.sync_printers(scan_data_list)
            session.commit()
            
        except Exception as e:
            log_error(f'[X] Erro critíco ao realizar sincronização das impressoras, ERRO: {e}')
            session.rollback()
    
    log_info('[AUTO] Sincronização finalizada.')
    
    
def run_scan_db():
    scan_data_list = []
    
    log_info('[AUTO] Iniciando scan de impressoras do banco de dados...')
    # ========== SCAN DO DB ==========
    with SessionLocal() as session:
        try:
            printer_repository = PrinterRepository(session)
            error_repository = ErrorCounterRepository(session)
            
            scan_service = ScanService(printer_repository=printer_repository, error_repository=error_repository)
            
            scan_data_list = asyncio.run(scan_service.collect_scan_data("db"))

            session.commit()
           
        except Exception as e:
            log_error(f'[X] Erro critíco ao realizar ao scan SNMP das impressoras cadastradas no BD, ERRO: {e}')
            session.rollback()
            
        finally:
            session.close()
            
    log_info('[AUTO] Scan finalizado.')
    
    #if scan_data_list:
    run_sync(scan_data_list) 
    

def run_scan_branches():    
    log_info('[AUTO] Iniciando scan das redes da filiais...')
    # ========== SCAN DAS REDES ==========
    snmp_data_list_branches = []
    with SessionLocal() as session:
        try:
            branch_repository = BranchRepository(session)
            branch_network_repository = BranchNetworkRepository(session)
            error_repository = ErrorCounterRepository(session)
            
            scan_service = ScanService(
                branch_repository=branch_repository,
                branch_network_repository=branch_network_repository,
                error_repository=error_repository
            )
            
            snmp_data_list_branches = asyncio.run(scan_service.collect_scan_data("branch"))
            #session.commit()
           
        except Exception as e:
            log_error(f'[X] Erro critíco ao realizar ao scan SNMP das impressoras cadastradas no BD, ERRO: {e}')
            session.rollback()
            
        finally:
            session.close()
    log_info('[AUTO] Scan finalizado.')
    
    if snmp_data_list_branches:
        run_sync(snmp_data_list_branches) 


def run_generate_resume_daily_counters(ini_date, end_date):
    log_info(f'Realizando resumos diários a partir do dia {ini_date} até {end_date}')
    
    with SessionLocal() as session:
        printer_repo = PrinterRepository(session)
        raw_counters_repo = RawCounterRepository(session)
        errors_repo = ErrorCounterRepository(session)
        daily_counters_repo = DailyCounterRepository(session)
    
        daily_counter_service = DailyCountersService(
            printer_repo,
            raw_counters_repo,
            errors_repo,
            daily_counters_repo
        )
        try:
            daily_counter_service.generate_summaries_date_range(ini_date, end_date)
            session.commit()
        
        except Exception as e:
            log_error(f'FALHA ao realizar os resumos: {e}')
            session.rollback()
        
        finally:
            session.close()


def run_export():
    with SessionLocal() as session:
        printer_repository = PrinterRepository(session)
        branch_repository = BranchRepository(session)
        export = ExportData(printers_repository=printer_repository, branch_repository=branch_repository)
        try:        
            export.printers()
            log_info('[AUTO] Exportação da tabela printers concluída.')
        except Exception as e:
            log_error(f'Erro ao exportar impressoras: {e}')
        
        try:
            export.branches()
            log_info('[AUTO] Exportação da tabela branches concluída.')
        except Exception as e:
            log_error(f'Erro ao exportar filiais: {e}')
    

def task_scheduled():
    log_info('[AUTO] Iniciando ciclo completo...')
    limpar_log()
    
    run_scan_branches()
    run_scan_db()
    
    # ========== EXPORTAÇÃO ==========
    log_info('[AUTO] Ciclo de varredura completo. Iniciando exportação...')
    
    #run_export()
    
    log_info('[AUTO] Ciclo completo finalizado.')


def thread_scheduler():
    # Registra os sinais de encerramento
    
    task_scheduled()
    
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)
    
    schedule.every(10).minutes.do(task_scheduled)
    

    # Exemplo: Roda em um horário específico
    # schedule.every().day.at('23:00').do(tarefa_agendada)

    while True:
        schedule.run_pending()
        time.sleep(1)


'''
def thread_manual():
    while True:
        print('\n' + '='*40)
        print('      PRINTER MONITOR SaaS')
        print('='*40)
        print('1. Forçar Scan de Impressoras (DB)')
        print('2. Forçar Scan de Filiais (Redes)')
        print('3. Realizar Resumo Diário (03/03/2026)')
        print('0. Sair')
        print('='*40)
        
        opcao = input('Escolha uma opção: ')

        if opcao == '1':
            print('\n🚀 Iniciando Scan do Banco de Dados...')
            asyncio.run(ScanService.scan_db())
        
        elif opcao == '2':
            print('\n🚀 Iniciando Scan de todas as Filiais...')
            asyncio.run(ScanService.scan_branches())

        elif opcao == '3':
            print('Realizando resumos diários a partir do dia 03/03 até D-1 (manutenção)')
            ini_date = date(2026, 3, 3)
            end_date = (datetime.now() - timedelta(days=1)).date()
            #DailyCountersService.generate_summaries_date_range(ini_date=ini_date, end_date=end_date)
            # Se você tiver o scan_manual pronto no Service:
            #asyncio.run(ScanService.scan_manual(ip, branch_id=1, network_id=1))
            pass

        elif opcao == '0':
            print('Encerrando sistema...')
            break
        else:
            print('Opção inválida!')
'''            

if __name__ == '__main__':
    limpar_log()
    
    thread_scheduler()
    
    '''
        # run_generate_resume_daily_counters(date(2026, 4, 1), date(2026, 5, 1))
        with SessionLocal() as session:
            dialy_counter_repository = DailyCounterRepository(session)
            report_service = ReportService(daily_counters_repository=dialy_counter_repository)
            report_service.generate_month_summary(month_number=6, year=2026)       
        
    '''
    

    '''
        import pandas as pd
        
        from monitoramento_impressoras_backend.repositories.position_repository import PositionRepository
        from monitoramento_impressoras_backend.database.models.positions import Position
                
        position_repository = PositionRepository(session)
        
        ips_location_df = pd.read_excel("src/monitoramento_impressoras_backend/ip_location.xlsx")
        
        mapa_location = dict(zip(ips_location_df['IP'], ips_location_df['position']))
        
        
        try:
            for ip in ips_location_df['IP']:
                print(f"Adicionando IP {ip}")
                position = position_repository.get_by_ip(ip)
                
                if position is not None:
                    print("IP já cadastrado. Ignorando...")
                    continue
                if ip.strip() == '': continue
                
                nome = str(mapa_location.get(ip))
                
                print(f"Nome {nome} {len(nome)}")
                
                
                position = Position(
                    ip = ip,
                    name = str(mapa_location.get(ip)).strip()
                )
                
                position_repository.save(position)
                
            session.commit()
        
        except Exception as e:
            print(f'Erro {e}')
            session.rollback()
        
        finally:
            session.close()
    '''
    
    '''
        printer_repo = PrinterRepository(session)
        raw_counter_repo = RawCounterRepository(session)
        error_counter_repo = ErrorCounterRepository(session)
        daily_counter_repo = DailyCounterRepository(session)
        
        daily_counters_service = DailyCountersService(
            printer_repo=printer_repo,
            raw_counters_repo=raw_counter_repo,
            errors_repo=error_counter_repo,
            daily_counters_repo=daily_counter_repo
        )
        
        ini_date = date(2026, 1, 1)
        end_date = date(2026, 7, 7)
        
        daily_counters_service.generate_summaries_date_range(ini_date=ini_date, end_date=end_date, force=True)
    '''
        
    '''
        with SessionLocal() as session:
            repo = DailyCounterRepository(session)
            report_service = ReportService(daily_counters_repository=repo)
            today = date.today()
            #init_date = today - timedelta(days=7)
            init_date = date(2026, 1, 1)
            #end_date = today - timedelta(days=3)
            end_date = date(2026, 5, 29)
            
            report_service.generate_summary_by_date_range(init_date=init_date, end_date=end_date)
        #report_service.generate_daily_summary(date=end_date)
        
        print('Fim')
    '''