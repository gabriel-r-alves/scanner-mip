# 🖨️ Scanner MIP — Coletor de Monitoramento de Impressoras

Este projeto nasceu da minha necessidade de **entender na prática como funciona o monitoramento de dispositivos em rede**.

Ao invés de ficar apenas na teoria, decidi construir uma aplicação real capaz de:

- Descobrir dispositivos ativos na rede de forma eficiente
- Coletar informações de contadores e status via SNMP
- Validar e sincronizar os dados coletados
- Armazenar dados e gerar relatórios

> 💡 Este é um projeto de aprendizado contínuo. Estou evoluindo a aplicação conforme aprendo novos conceitos de arquitetura, concorrência, comunicação em rede e desenvolvimento de software.

---

## 🎯 O que estou aprendendo com este projeto

- Comunicação com dispositivos de hardware via **SNMP**
- Programação assíncrona com **asyncio**
- Concorrência e execução de rotinas de monitoramento
- Agendamento de tarefas com **schedule**
- Organização de código utilizando **camadas de serviço e Repository**
- Persistência de dados e migrações com **SQLAlchemy + Alembic**
- Manipulação e exportação de dados com **Pandas**
- Comunicação com dispositivos através de diferentes métodos de coleta

---

## 🚀 Funcionalidades atuais

- 🔍 **Descoberta de dispositivos na rede**
- 📡 **Coleta de informações de impressoras**
- 📊 **Coleta de contadores**
- 🔂 **Validação e sincronização dos dados coletados**
- 🖥️ **Persistência dos dados no banco de dados**
- 📄 **Exportação de informações para relatórios**

---

## 🛠️ Tecnologias utilizadas

- Python 3.13+
- asyncio
- threading
- schedule
- PySNMP
- aioping
- SQLAlchemy
- Alembic
- MariaDB
- Pandas
- Openpyxl
- Poetry

---

## 🏗️ Estrutura do projeto

```text
.
├── migrations/
│   ├── versions/              # Histórico de migrações do Alembic
│   └── env.py                 # Configuração do ambiente de migração
│
├── src/
│   └── monitoramento_impressoras_backend/
│       ├── app.py             # Ponto de entrada e orquestração
│       ├── database/          # Configuração do banco e modelos
│       ├── repositories/      # Camada de persistência
│       ├── services/          # Regras de negócio e rotinas de coleta
│       └── utils/             # Funções auxiliares
│
├── tests/                     # Testes automatizados
├── .env.example               # Modelo das variáveis de ambiente
├── poetry.lock                # Versões exatas das dependências
├── pyproject.toml             # Configuração do projeto e dependências
├── README.md                  # Documentação principal
└── SETUP.md                   # Guia de configuração do ambiente
```

## 🔧 Como executar
Para configurar o ambiente, consulte primeiro o [SETUP.md.](./SETUP.md)

### 1. Clonar o repositório

```bash
git clone https://github.com/gabriel-r-alves/scanner-mip.git

cd scanner-mip
```

### 2. Ativar o ambiente

```bash
poetry shell
```

Também é possível executar comandos diretamente através de poetry run.

### 3. Instalar as dependências

```bash
poetry install
```

### 4. Aplicar as migrations

```bash
alembic upgrade head
```

### 5. Executar o Scanner

```bash
poetry run python -m monitoramento_impressoras_backend.app
```

## ⚠️ Observação importante — ICMP

Durante o desenvolvimento, encontrei uma limitação comum ao trabalhar com ICMP (ping) utilizando a biblioteca aioping.

Em determinadas configurações Linux, o processo pode não possuir permissão para enviar pacotes ICMP diretamente.

### 💥 Erro comum

```bash
Operation not permitted
```

### ✅ Possíveis soluções

**Opção 1 — executar com privilégios elevados**

```bash
sudo poetry run python -m monitoramento_impressoras_backend.app
```

**Opção 2 — conceder ao Python a capacidade necessária**

```bash
sudo setcap cap_net_raw+ep $(which python3)
```

> A configuração de permissões pode variar de acordo com a distribuição Linux e a instalação do Python.

## ⚙️ Funcionamento

O Scanner possui dois modos principais de operação:

### 🔄 Automático

Executa rotinas periódicas de monitoramento, incluindo:

- varredura da rede
- coleta de informações
- atualização dos dados
- geração de relatórios

### 🖥️ Manual

Permite executar determinadas operações sob demanda, como:

- atualizar o status das impressoras
- descobrir novos dispositivos
- coletar informações
- gerar relatórios

## 🗺️ Evolução arquitetural
### Estado atual

Atualmente, o Scanner ainda possui responsabilidades relacionadas à coleta, validação, sincronização e persistência.

```text
Scanner
├── Descoberta
├── Coleta
├── Validação
├── Sincronização
└── Persistência
```

### Em evolução

A arquitetura está sendo gradualmente separada para reduzir as responsabilidades do Scanner.

O objetivo é fazer com que o Scanner seja responsável principalmente pela **descoberta e coleta dos dados**, enquanto o Backend assuma as responsabilidades relacionadas à **API**, **sincronização e persistência**.

#### Arquitetura planejada

```text
┌──────────────┐
│   Scanner    │
│              │
│ Descoberta   │
│ Coleta       │
│ Validação    │
└──────┬───────┘
       │
       │ dados coletados
       ▼
┌──────────────┐
│   Backend    │
│              │
│ API          │
│ Sincronização│
│ Persistência │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   MariaDB    │
└──────────────┘
```

> **Nota:** A versão atual ainda mantém responsabilidades de sincronização e persistência dentro do Scanner. Essa estrutura faz parte da versão atual e será gradualmente separada conforme a arquitetura evolui.

### Responsabilidades planejadas

**Scanner MIP**

Responsável pela descoberta de dispositivos e coleta das informações.

**Backend MIP**

Responsável pela API, regras de sincronização e persistência.

**MariaDB**

Responsável pelo armazenamento dos dados.

## 👨‍💻 Sobre mim

Sou desenvolvedor em início de carreira e gosto de aprender construindo projetos reais.

Este projeto faz parte do meu portfólio e representa meu processo de evolução, onde estou explorando conceitos mais avançados de arquitetura, comunicação em rede, concorrência e desenvolvimento de software enquanto consolido minha base.

## 📌 Status

🚧 Em desenvolvimento contínuo


