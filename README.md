# 📊 Overwatch 2 Stats API & ETL Pipeline
Backend de Alta Performance para Gestão e Análise de Estatísticas de Heróis.

O projeto consiste em uma API RESTful construída em FastAPI para armazenar, gerenciar e expor dados de performance de Overwatch 2 (Taxa de Vitória, Taxa de Escolha) por filtros como Mapa e Rank. Este backend foi projetado para ser a espinha dorsal de um futuro serviço de análise de dados.

# 🚀 Sobre o Projeto
A arquitetura foi escolhida para enfrentar dois desafios principais: garantir a performance em I/O (Input/Output) e manter a integridade dos dados.

Performance: A utilização do FastAPI em Python, que opera de forma assíncrona, maximiza a velocidade de resposta da API.

Integridade: O uso rigoroso do Pydantic força a validação dos dados de entrada antes que qualquer query SQL seja executada.

Este é um projeto API-first. Não há um frontend no momento, mas a intenção de longo prazo é desenvolver uma interface (provavelmente React ou React Native) que consumirá exclusivamente os dados desta API.

# ✨ Princípios e Boas Práticas de Desenvolvimento
Nossa arquitetura segue rigorosamente padrões estabelecidos para garantir código limpo, manutenível e escalável:

- Princípio Aplicação no Projeto 
Detalhes:

Separação de Responsabilidades	Estrutura de Camadas (MVC Adaptado)	O projeto é dividido em Rotas (route_*.py), Modelos/Schemas (models.py) e Acesso a Dados (DAO) (db.py e function_execute.py), isolando a lógica de negócio, validação e persistência.
DAO (Data Access Object)	function_execute.py	O acesso ao MySQL é encapsulado. O DAO gerencia a conexão e desconexão para cada requisição (db.connect() e db.disconnect()), garantindo o fechamento imediato do recurso e seguindo o princípio DRY (Don't Repeat Yourself) para execução SQL.

RESTful	Rotas Genéricas CRUD	
O design da API utiliza verbos HTTP corretos (GET, POST, PUT, DELETE) em rotas dinâmicas como /insert/{table_name}, garantindo que as operações de recurso sejam previsíveis e padronizadas.

Tratamento de Erros	HTTPException	A camada DAO (function_execute.py) implementa um bloco crítico de tratamento de erros. Ele captura exceções específicas do mysql-connector e as transforma em HTTPException(500) com a mensagem de erro detalhada, facilitando o debug para o desenvolvedor.
Validação de Tipos	FastAPI + Pydantic	O framework utiliza modelos Pydantic para validar o payload JSON recebido. Isso garante que os dados sejam tipados corretamente antes de serem passados ao SQL, protegendo o backend.

Exportar para as Planilhas

# 🛠️ Tecnologias Utilizadas

- Uso Detalhado no Projeto:

Backend (Core)	Python (FastAPI)	Framework assíncrono (ASGI) que utiliza o poder do Python para I/O-bound tasks. Sua alta velocidade é fundamental para a performance da API.

Validação de Dados	Pydantic	Biblioteca CRÍTICA para a tipagem rigorosa dos dados. O FastAPI o utiliza para transformar o JSON da requisição em um objeto Python tipado, garantindo a integridade dos dados antes da inserção.

Conexão DB	SQL (MySQL)	SGBD Relacional. A lógica de UPSERT (Update or Insert) é implementada usando comandos SQL puros, aproveitando as chaves primárias compostas para eficiência.

Driver DB	mysql-connector-python	Driver assíncrono para a comunicação eficiente entre o código Python e o servidor MySQL.
Controle de Ambiente	python-dotenv	Utilizado para carregar as variáveis de ambiente (credenciais de DB) do arquivo .env de forma segura.

Segurança/Performance	fastapi-limiter (Redis)	Dependência que impõe o Rate Limiting para proteger as rotas contra abusos (ex: ataques de negação de serviço).

Exportar para as Planilhas

Dependências (Baseado no requirements.txt)

Dependência	Função Primária

fastapi	Roteamento principal e interface API.

pydantic	Definição de modelos de dados, tipagem e validação.

mysql-connector-python	Comunicação com o SGBD MySQL.

python-dotenv	Carregamento seguro das credenciais de ambiente.

fastapi-limiter	Implementação de Rate Limiting (depende de Redis).

httpx -> Biblioteca de requisição HTTP para o módulo ETL (mesmo que a extração tenha sido ajustada para CSV, ela é útil para outros serviços).

Exportar para as Planilhas

# ⚙️ Passo a Passo da Instalação

1. Clonar o Repositório
Bash

git clone [https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git]
cd SEU-REPOSITORIO
2. Configurar o Ambiente Python
Bash

# Crie e ative um ambiente virtual
python -m venv venv

# No Windows:
venv\Scripts\activate

# No macOS/Linux:
source venv/bin/activate

# Instale as dependências

- pip install -r requirements.txt

3. Configurar Banco de Dados e Variáveis de Ambiente
Crie o Banco de Dados no MySQL: CREATE DATABASE ow2_stats_db;

Crie o arquivo .env: Preencha na raiz do projeto com as credenciais:

Ini, TOML

# Arquivo .env
DB_HOST="localhost"
DB_USER="seu_usuario_mysql"
DB_PSWD="sua_senha_secreta"
DB_NAME="ow2_stats_db"
# Opcional
# REDIS_URL="redis://localhost:6379" 

4. Aplicação do Schema (Criação de Tabelas)
TODO CRÍTICO: O arquivo schema.sql deve ser criado e executado no MySQL.

Exemplo de Tabela de Estatísticas (MySQL):
As chaves primárias compostas são essenciais para o UPSERT.

Campo	Tipo SQL	Descrição

hero_id	INT NOT NULL	Chave Estrangeira para a tabela de Heróis.
map_id	INT NOT NULL	Chave Estrangeira para a tabela de Mapas.
win_rate	DECIMAL(5, 2) NOT NULL	Taxa de vitória do herói naquele mapa (Ex: 52.15).
PRIMARY KEY	(hero_id, map_id)	Garante a unicidade do par e permite o UPSERT.

Exportar para as Planilhas

💾 Carga Automática de Dados (UPSERT)
A Carga (L do ETL) é feita através de uma operação UPSERT, garantindo que não haja dados duplicados e que as estatísticas sejam atualizadas de forma eficiente.

1. Transformação de Dados:
O script csv_transformer.py gera o JSON limpo (com IDs mapeados) a partir do CSV.

Bash
python csv_transformer.py

# O arquivo dados_transformados.json estará pronto para ser carregado.

2. Carga com UPSERT (Em Desenvolvimento)
TODO CRÍTICO: Implementar a Rota de Carga em Lote (route_load.py) e o SQL de UPSERT.

Exemplo da Query UPSERT (MySQL):

SQL

INSERT INTO hero_map_win (hero_id, map_id, win_rate)
VALUES (%s, %s, %s)
ON DUPLICATE KEY UPDATE
win_rate = VALUES(win_rate);
🏃 Como Rodar a Aplicação
Para iniciar a API:

Bash

# Com o venv ativo
uvicorn main:app --reload --host 0.0.0.0 --port 8000
O servidor estará rodando em http://127.0.0.1:8000.

Acesse a documentação interativa (Swagger UI) para testes em: http://127.0.0.1:8000/docs.