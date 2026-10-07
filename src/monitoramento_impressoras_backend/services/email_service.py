import os
import smtplib
import email.message

from datetime import datetime
from calendar import month_name

from monitoramento_impressoras_backend.repositories import *


def get_date() -> list[dict[str, str]]:
    mes_atual = None
    mes_anterior = None

    data_atual = datetime.now()
    mes_atual = data_atual.month

    mes_anterior = 12 if mes_atual == 1 else mes_atual - 1

    mes_atual = month_name[mes_atual]
    mes_anterior = month_name[mes_anterior]

    return [{"mes_atual": mes_atual}, {"mes_anterior": mes_anterior}]


def enviar_email():
    filiais = BranchRepository.get_all_branches()
    if not branches:
        print("Filiais vazias!")
        return
    
    printers = PrinterRepository.get

    for filial in filiais:
        print(filial)

    datas = get_data()
    print(datas)
    
    if datas["mes_atual"] and datas["mes_atual"]:
        print("Datas com erro")
        return

    
'''
    linhas = ""
    
    for imp in impressoras:
        linhas += f"""
        <tr>
            <td>{imp.posicao}</td>
            <td>{imp.num_serie}</td>
            <td>{imp.contador_mesAnterior}</td>
            <td>{imp.contador_mesAtual}</td>
        </tr>
        """

    server_smtp = os.getenv("server_smtp")
    port = int(os.getenv("port"))
    sender_email = os.getenv("sender_email")
    password = os.getenv("password")

    reciver_email = ''
    subject = ''
    body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Tabela no e-mail</title>
    </head>
    <body>
        <div>
            <table>
                <thead>
                    <tr>
                        <th>Impressora</th>
                        <th>Série</th>
                        <th> impressões {mes_anterior}</th>
                        <th> impressões {mes_atual}</th>
                    </tr>
                </thead>
                <tbody>
                    {linhas}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
'''
