# Passo a passo inicial

## 1 - Instalação

### 1.1 - pipx

Para instalar o `pipx` no Debian:

```bash
sudo apt update
sudo apt install pipx
```

Após a instalação, configurar o PATH para que o sistema reconheça as ferramentas instaladas pelo pipx:

```bash
pipx ensurepath
```

> Pode ser necessário reiniciar o terminal após esse comando para que a alteração do ```PATH``` seja reconhecida.

### 1.2 - poetry
Para instalar o poetry:

```bash
pipx install poetry
poetry --version
```
Para adicionar o suporte ao comando poetry shell:

**Via pipx:**

```bash
pipx inject poetry poetry-plugin-shell
```

**Via poetry self**

```bash
poetry self add poetry-plugin-shell
```
> As duas opções têm a mesma finalidade. Não é necessário executar as duas.

Após isso rodar o seguinte comando, para que o poetry crie por padrão as venvs dentro da pasta do projeto:

```bash
poetry config virtualenvs.in-project true
```

Dessa forma, a virtualenv será criada em:
```
.venv/
```

### 1.3 - Python

Para instalar o Python na versão utilizada pelo projeto:

```
poetry python install 3.13
```

Uma resposta similar a esta deve ser retornada:

```bash
Downloading and installing 3.13.2 (cpython) ... Done 
Testing 3.13.2 (cpython) ... Done
```
>**importante:**os comandos a partir deste ponto devem ser executados dentro da pasta do projeto, onde está localizado o arquivo ```pyproject.toml```

Selecionar o Python 3.13 para o ambiente virtual do projeto:

```bash
poetry env use 3.13
```

Verificar as informações do ambiente:

```bash
poetry env info
```

A saída deve indicar algo semelhante a:

```bash
Virtualenv
Python:         3.13.x
Implementation: CPython
Path:           /caminho/do/projeto/.venv
Executable:     /caminho/do/projeto/.venv/bin/python
Valid:          True
```

## 2 - Ativação do ambiente

Existem duas formas de executar comandos utilizando o ambiente virtual do Poetry.

Utilizando ```poetry run```:

```bash
poetry run <comando>
```

Ou ativando o shell do ambiente:

```bash
poetry shell
```

Neste setup, vamos utilizar o ```poetry shell``` para manter o ambiente virtual ativo durante a configuração do projeto.

Execute:

```bash
poetry shell
```

O Poetry deverá iniciar um novo shell utilizando a virtualenv criada para o projeto.

O prompt do terminal deverá passar a indicar o ambiente virtual, por exemplo:

```bash
(projeto-py3.13) user@debian:~/projetos/projeto$
```
>O nome exibido entre parênteses pode variar de acordo com o nome do projeto e da virtualenv.

Agora instalar as dependências:

```bash
poetry install
```

Após a instalação, verificar a versão do Python utilizada:

```bash
python --version
```

Deve retornar:

```bash
Python 3.13.x
```

Para consultar as dependências instaladas:

```bash
poetry show
```


## 3 - Configuração das variáveis de ambiente

O projeto utiliza variáveis de ambiente para armazenar configurações locais, como a conexão com o banco de dados.

O repositório possui um arquivo .env.example com um modelo das variáveis necessárias:

```bash
.env.example
```
>Esse arquivo não contém credenciais reais e pode ser versionado no repositório.

### 3.1 Criar o arquivo ```.env```

Na raiz do projeto, criar uma cópia do arquivo de exemplo:

```bash
cp .env.example .env
```

Agora teremos:

```
scanner-mip/
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
└── ...
```

O arquivo ```.env ``` deve ser utilizado para armazenar os valores específicos do ambiente.

**Configurar a conexão com o banco**

Abrir o arquivo .env:

```bash
nano .env
```

Configurar:

```
DATABASE_URL='mysql+pymysql://mip_user:SUA_SENHA@IP_DO_SERVIDOR:3306/mip'
```

Exemplo:

```
DATABASE_URL='mysql+pymysql://mip_user:SUA_SENHA@192.168.0.100:3306/mip'
```
>Substitua os valores de exemplo pelos dados reais do ambiente.

>Caso a senha contenha caracteres especiais, eles podem precisar ser codificados para utilização na URL de conexão.

O ```.env.example``` deve continuar contendo apenas valores de exemplo:

```
DATABASE_URL = 'mysql+pymysql://user_name:user_password@db_ip:db_port/database'
```

Ele serve para indicar quais variáveis precisam ser configuradas sem expor credenciais.

## 4. Configuração do banco de dados

O Scanner MIP utiliza MariaDB para persistência dos dados.

Antes de continuar, certifique-se de que:

- O MariaDB está instalado e em execução.
- A máquina onde o Scanner MIP será executado possui acesso ao servidor MariaDB.
- O usuário utilizado pela aplicação possui permissão no banco.
- A porta do MariaDB está acessível pela rede, quando o banco estiver em outro servidor.

### 4.1 Criar o banco de dados

No servidor MariaDB, acesse o banco como usuário administrativo:

```bash
sudo mysql --no-defaults -u root
```

Crie o banco:

```sql
CREATE DATABASE mip;
```

Confirme:

```sql
SHOW DATABASES;
```

O banco ```mip``` deverá aparecer na lista.

### 4.2 Criar o usuário da aplicação

Ainda dentro do MariaDB:

```sql
CREATE USER 'mip_user'@'IP_DO_SCANNER'
IDENTIFIED BY 'SUA_SENHA';
```

Conceda as permissões:

```sql
GRANT ALL PRIVILEGES ON mip.* TO 'mip_user'@'IP_DO_SCANNER';
FLUSH PRIVILEGES;
```
> Substitua ```IP_DO_SCANNER``` pelo endereço IP da máquina onde o Scanner MIP será executado.

> Para um ambiente local onde aplicação e banco estão na mesma máquina, pode ser utilizado ```localhost```.

Verifique o usuário:

```sql
SELECT User, Host
FROM mysql.user
WHERE User = 'mip_user';
```

> Nunca versionar o arquivo .env. Ele pode conter credenciais reais.

> O arquivo .env.example deve permanecer versionado e conter apenas valores de exemplo.


### 4.3 Testar a conexão com o banco

Com o ambiente Poetry ativado e dentro do diretório do projeto:

```
alembic current
```

Se a conexão estiver funcionando, o Alembic deverá iniciar normalmente e indicar o dialeto utilizado:

```bash
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
```
Em um banco recém-criado, é normal não existir uma revisão atual nesse momento.

### 4.4 Aplicar as migrations

Execute:

```bash
alembic upgrade head
```

Esse comando cria a estrutura do banco de dados de acordo com a migration atual.

Para verificar a revisão aplicada:
```bash
alembic current
```

O resultado deverá indicar a revisão atual seguida de:
```bash
(head)
```

### 4.5 Verificar as tabelas

No MariaDB:
```sql
mysql -h IP_DO_SERVIDOR -u mip_user -p mip
```

Depois:
```sql
SHOW TABLES;
```

As tabelas definidas pelos models do projeto deverão estar presentes.

### 4.6 Migration inicial

O projeto possui uma migration inicial que representa o schema atual:
```
migrations/
└── versions/
    └── <hash>_initial_schema.py
```

Essa migration foi gerada utilizando Alembic e validada contra o schema anterior do projeto.

O banco novo foi comparado estruturalmente com o banco anterior, verificando:

- tabelas
- colunas
- tipos
- valores padrão
- chaves primárias
- chaves estrangeiras
- índices
- constraints UNIQUE

