📊 Overwatch 2 Stats API & ETL Pipeline
Aplicativo de backend para gestão e análise de estatísticas de heróis de Overwatch 2.

O projeto é focado em criar uma API RESTful robusta para armazenar e consultar dados de performance (Taxa de Vitória, Taxa de Escolha) por filtros como Mapa e Rank. Ele é a espinha dorsal de um futuro serviço de análise de dados.

🚀 Sobre o Projeto
Levando em consideração a volatilidade dos dados de jogos e a necessidade de alto desempenho, focamos em uma arquitetura que prioriza a velocidade e a integridade dos dados. Utilizamos FastAPI para o backend e um Pipeline de ETL (Extração, Transformação e Carga) eficiente para garantir que as estatísticas do banco estejam sempre atualizadas.

O projeto é modular. Criamos rotas CRUD genéricas, o que facilita a escalabilidade e a manutenção, pois a lógica de acesso ao banco é centralizada.

✨ Funcionalidades
Funcionalidade	Característica	Detalhes
API Genérica (CRUD)	GET, POST, PUT, DELETE	Rotas dinâmicas que aceitam o nome da tabela (/insert/hero) e o payload (dados). A segurança é garantida por uma Whitelist de tabelas.
Validação de Dados	Pydantic	O corpo de todas as requisições POST/PUT é validado estritamente por modelos Pydantic antes de tocar o banco de dados, assegurando a integridade.
ETL (Transformação)	csv_transformer.py	Script Python para processar dados brutos (ex: CSV) e transformá-los em objetos JSON mapeados para IDs (hero_id, map_id).
Carga de Dados	Método UPSERT	O pipeline de carga (próxima etapa) usará comandos INSERT ... ON DUPLICATE KEY UPDATE para atualizar as estatísticas existentes ou inserir novas, garantindo que nunca haja dados duplicados.
Segurança	Rate Limiting	Proteção contra abuso de requisições (fastapi-limiter) para todas as rotas de consulta.
DAO Isolado	function_execute.py	A lógica de conexão e execução SQL está isolada em uma função única e segura, garantindo o fechamento de conexão após cada comando.

Exportar para as Planilhas
🛠️ Tecnologias Utilizadas
Componente	Tecnologia	Detalhes e Relação com o Projeto
Backend (API)	Python (FastAPI)	Escolhido pelo alto desempenho e por ter validação de schema nativa via Pydantic. É o servidor principal da API.
Banco de Dados	MySQL	SGBD relacional robusto. As tabelas de estatísticas são projetadas com chaves primárias compostas para suportar o UPSERT.
Driver DB	mysql-connector-python	Driver assíncrono para a comunicação segura e tipada entre o Python e o MySQL.
Validação	Pydantic	Responsável por transformar os dados recebidos (JSON) em objetos Python tipados, evitando erros de tipo ou dados faltantes.

Exportar para as Planilhas
Pré-requisitos
Antes de começar, garanta que você tem as seguintes ferramentas instaladas:

Git

Python (versão 3.8 ou superior)

MySQL Server (e opcionalmente o MySQL Workbench)

uvicorn (Servidor ASGI para rodar o FastAPI)

⚙️ Passo a Passo da Instalação
1. Clonar o Repositório
Abra seu terminal e clone o projeto para sua máquina local:

Bash

git clone [https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git]
cd SEU-REPOSITORIO
2. Configurar o Backend e o Ambiente Virtual
Bash

# Crie e ative um ambiente virtual
python -m venv venv

# No Windows:
venv\Scripts\activate

# No macOS/Linux:
source venv/bin/activate

# Instale as dependências (baseado no requirements.txt)
pip install -r requirements.txt
3. Configurar o Banco de Dados e Variáveis de Ambiente
Crie o Banco de Dados no MySQL:

SQL

CREATE DATABASE ow2_stats_db;
Crie o arquivo .env: Na pasta raiz do projeto, crie o arquivo .env e preencha com suas credenciais:

Ini, TOML

# Arquivo .env
DB_HOST="localhost"
DB_USER="seu_usuario_mysql"
DB_PSWD="sua_senha_secreta"
DB_NAME="ow2_stats_db"
# Para ativar a segurança de Rate Limiting (Opcional)
# REDIS_URL="redis://localhost:6379" 
4. Aplicação do Schema (Criação de Tabelas)
É crucial criar a estrutura das tabelas antes de rodar a API.

TODO CRÍTICO: Crie um arquivo chamado schema.sql na raiz do projeto contendo os comandos CREATE TABLE.

As tabelas devem ter seus campos de identificação (IDs) e nomes definidos como VARCHAR (para nomes/descrições) ou INT (para IDs) e DECIMAL/FLOAT (para as taxas), conforme o tipo de dado esperado.

Exemplo de Chave Primária Composta (necessária para UPSERT):

SQL

CREATE TABLE `hero_map_win` (
    `hero_id` INT NOT NULL,
    `map_id` INT NOT NULL,
    `win_rate` FLOAT(5, 2) NOT NULL,
    PRIMARY KEY (`hero_id`, `map_id`)
);
Execute o schema.sql no seu MySQL Workbench ou terminal.

💾 Método de Carga de Dados (UPSERT Automático)
Este é o fluxo para popular o banco de dados com estatísticas de forma segura.

1. Transformação Local
Execute o script de ETL para transformar o CSV em JSON pronto para o banco.

Bash

# Com o venv ativo e o arquivo CSV na pasta
python csv_transformer.py
# Resultado: Criação do arquivo dados_transformados.json
2. Implementação da Carga Automática (UPSERT)
A Carga no banco deve ser feita através de uma rota de API dedicada que utilize a instrução UPSERT.

TODO CRÍTICO: Implementar a rota e o SQL.

Ação	Rota/Arquivo	SQL Necessário
SQL	function_execute.py ou db.py	Escrever a query INSERT INTO ... ON DUPLICATE KEY UPDATE
Rota	route_load.py (Novo)	Rota POST que recebe a lista de dados transformados do JSON e executa a query SQL em lote (UPSERT).

Exportar para as Planilhas
Exemplo da Query UPSERT (MySQL):

SQL

# Para a tabela hero_map_win:
INSERT INTO hero_map_win (hero_id, map_id, win_rate)
VALUES (%s, %s, %s)
ON DUPLICATE KEY UPDATE
win_rate = VALUES(win_rate);
🏃 Como Rodar a Aplicação
Para rodar a API, você precisa apenas de um terminal.

Bash

# Navegue para a pasta raiz e ative o ambiente virtual
venv\Scripts\activate  # Windows

# Inicie a API com Uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
O servidor da API estará rodando em http://127.0.0.1:8000.

Acesse a documentação interativa para testar as rotas CRUD em: http://127.0.0.1:8000/docs.

