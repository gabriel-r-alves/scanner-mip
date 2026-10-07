# 🖨️ Scanner MIP — Coletor de Monitoramento de Impressoras (Projeto de Estudo)

Este projeto nasceu da minha necessidade de **entender na prática como funciona o monitoramento de dispositivos em rede**.

Ao invés de ficar apenas na teoria, decidi construir uma aplicação real capaz de:
- Descobrir dispositivos ativos na rede de forma eficiente
- Coletar informações de contadores e status via SNMP
- Armazenar dados transacionais e gerar relatórios periódicos

> 💡 Este é um projeto de aprendizado contínuo — estou evoluindo ele conforme aprendo novos conceitos de arquitetura e concorrência.

---

## 🎯 O que estou aprendendo com este projeto

- Comunicação com dispositivos de hardware via **SNMP** (Protocolo UDP na porta 161)
- Programação assíncrona de alta performance com **asyncio**
- Agendamento de tarefas e orquestração de rotinas com **schedule**
- Organização de código limpo utilizando **Camadas (Repository + Services)**
- Persistência de dados transacionais e migrações com **SQLAlchemy + Alembic**
- Manipulação de dados e exportação com **Pandas**

---

## 🚀 Funcionalidades atuais

- 🔍 **Descobrir dispositivos ativos na rede de forma eficiente.**
- 📡 **Coletar informações de contadores e status das impressoras.** 
- 🔂 **Validar e sincronizar os dados coletados.**
- 🖥️ **Persistir os dados coletados no banco de dados.**

---

## 🛠️ Tecnologias utilizadas

- Python 3.13+
- asyncio / threading
- pysnmp-lextudio
- python-nmap
- aioping
- SQLAlchemy + Alembic
- Pandas + Openpyxl

---

## 🏗️ Estrutura do projeto
```
.
├── migrations/                 # Scripts de controle e histórico de migrações do Alembic
│   ├── versions/               # Arquivos sequenciais de atualizações do banco de dados
│   └── env.py                  # Script de ciclo de vida e conectividade do Alembic
├── src/
│   └── monitoramento_impressoras_backend/
│       ├── app.py              # Ponto de entrada (Orquestrador, Threads e Sinais do SO)
│       ├── database/           # Configurações de sessão e inicialização da Base
│       │   └── models/         # Mapeamento declarativo de tabelas (Entidades ORM)
│       ├── data_exported/      # Destino dos relatórios consolidados em Excel (.xlsx)
│       ├── logs/               # Armazenamento físico de logs em tempo real
│       ├── repositories/       # Camada de Persistência (Padrão Repository para CRUD)
│       ├── services/           # Regras de negócio (Scans assíncronos, Sync e Relatórios)
│       └── utils/              # Funções de suporte (Cálculos de IP, IO sem buffer, Exportações)
├── tests/                      # Suite de testes automatizados da aplicação
├── poetry.lock                 # Travamento de versões exatas de dependências externas
├── pyproject.toml              # Configurações do Poetry, empacotamento e metadados do projeto
├── README.md                   # Documentação principal da aplicação
└── SETUP.md                    # Manual técnico com instruções passo a passo para deploy
```

---

## 🔧 Como executar
Após realizar o [setup](SETUP.md):
### 1. Clonar o repositório

```bash
git clone https://github.com/gabriel-r-alves/scanner-mip.git
cd scanner-mip
```

### 2. Inicializar ambiente

```bash
poetry shell
```

### 3. Instalar dependências

```bash
poetry install
```

### 5. Configurar banco de dados

```bash
alembic upgrade head
```

### 6. Executar

```bash
poetry run python -m monitoramento_impressoras_backend.app
```

## ⚠️ Observação importante (ICMP / Permissão)

Durante o desenvolvimento, encontrei um problema comum ao trabalhar com **ICMP (ping)** usando a biblioteca `aioping`.

Por padrão, sistemas Linux exigem permissões elevadas para envio de pacotes ICMP.

### 💥 Erro comum:
- `Operation not permitted`

### ✅ Soluções possíveis:

**Opção 1 — Rodar como root**
```bash
sudo poetry run python -m monitoramento_impressoras_backend.app
```

**Opção 2 — Dar permissão para o Python usar ICMP (recomendado)**
```bash
sudo setcap cap_net_raw+ep $(which python3)
```
Isso permite executar o projeto sem precisar de sudo.

## ⚙️ Funcionamento

O sistema roda com dois modos principais:

- 🔄 **Automático**  
  Executa rotinas periódicas de monitoramento (varredura, coleta e exportação)

- 🖥️ **Manual**  
  Interface interativa via terminal para executar ações sob demanda:
  - atualizar status das impressoras
  - descobrir novos dispositivos na rede
  - gerar relatórios de contadores

---

## 🗺️ Evolução arquitetural

### Estado atual

O Scanner atualmente é responsável pela coleta, validação e
sincronização dos dados com o banco de dados.

```text
Scanner
├── Descoberta
├── Coleta
├── Validação
├── Sincronização
└── Persistência
```

### Em evolução
A arquitetura está sendo gradualmente separada para reduzir as
responsabilidades do Scanner.

O objetivo é fazer com que o Scanner seja responsável apenas pela
coleta dos dados, enquanto o Backend assuma as responsabilidades
relacionadas à persistência e disponibilização das informações.

### Arquitetura planejada

```
Scanner
   │
   │ dados coletados
   ▼
Backend
   │
   │ persistência / API
   ▼
MariaDB
```
> **Nota:** A versão atual ainda mantém responsabilidades de
> sincronização e persistência dentro do Scanner. Essa estrutura faz
> parte da versão atual e será gradualmente separada conforme a
> arquitetura evolui.

**Scanner MIP**
Responsável pela descoberta de dispositivos e coleta das informações.

**Backend MIP**
Responsável pela API, regras de sincronização e persistência.

**MariaDB**
Responsável pelo armazenamento dos dados.

## 👨‍💻 Sobre mim

Sou desenvolvedor em início de carreira e gosto de aprender construindo projetos reais.

Este projeto faz parte do meu portfólio e representa meu processo de evolução, onde estou explorando conceitos mais avançados enquanto ainda consolido minha base em desenvolvimento.

---

## 📌 Status

🚧 Em desenvolvimento contínuo
