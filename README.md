# 📊 Overwatch 2 Stats API & ETL Pipeline
Backend de Alta Performance para Gestão e Análise de Estatísticas de Heróis.

O projeto consiste em uma API RESTful construída em FastAPI para armazenar, gerenciar e expor dados de performance de Overwatch 2 (Taxa de Vitória, Taxa de Escolha) por filtros como Mapa e Rank. Este backend foi projetado para ser a espinha dorsal de um futuro serviço de análise de dados.

## 🚀 Sobre o Projeto
A arquitetura foi escolhida para enfrentar dois desafios principais: garantir a performance em I/O (Input/Output) e manter a integridade dos dados.

Performance: A utilização do FastAPI em Python, que opera de forma assíncrona, maximiza a velocidade de resposta da API.

Integridade: O uso rigoroso do Pydantic força a validação dos dados de entrada antes que qualquer query SQL seja executada.

Este é um projeto API-first. Não há um frontend no momento, mas a intenção de longo prazo é desenvolver uma interface (provavelmente React ou React Native) que consumirá exclusivamente os dados desta API.

## ✨ Princípios e Boas Práticas de Desenvolvimento
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

## 🛠️ Tecnologias Utilizadas

- #### Uso Detalhado no Projeto:

- Backend (Core), Python (FastAPI), Framework assíncrono (ASGI) que utiliza o poder do Python para I/O-bound tasks. Sua alta - - velocidade é fundamental para a performance da API.

- Validação de Dados Pydantic Biblioteca CRÍTICA para a tipagem rigorosa dos dados. O FastAPI o utiliza para transformar o JSON da requisição em um objeto Python tipado, garantindo a integridade dos dados antes da inserção.

- Conexão DB SQL (MySQL) SGBD Relacional. A lógica de UPSERT (Update or Insert) é implementada usando comandos SQL puros, aproveitando as chaves primárias compostas para eficiência.

- Driver DB	mysql-connector-python	Driver assíncrono para a comunicação eficiente entre o código Python e o servidor MySQL.
Controle de Ambiente	python-dotenv	Utilizado para carregar as variáveis de ambiente (credenciais de DB) do arquivo .env de forma segura.

- Segurança/Performance	fastapi-limiter (Redis)	Dependência que impõe o Rate Limiting para proteger as rotas contra abusos (ex: ataques de negação de serviço). Que ainda está em desenvolvimento...

- Exportar para as Planilhas

- #### Dependências:

| Dependência            | Função                                              |
|------------------------|-----------------------------------------------------|
| fastapi	             | Roteamento principal e interface API.               |
| pydantic               | Definição de modelos de dados, tipagem e validação. |
| mysql-connector-python | Comunicação com o SGBD MySQL.                       |
| python-dotenv	         | Carregamento seguro das credenciais de ambiente.    |
| fastapi-limiter	     | Implementação de Rate Limiting (depende de Redis).  |
| httpx                  | Biblioteca de requisição HTTP para o módulo ETL     |

## ⚙️ Passo a Passo da Instalação

1. Clonar o Repositório
Bash

git clone [https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git]
cd "SEU-REPOSITORIO"

2. Configurar o Ambiente Python
Bash

3. Crie e ative um ambiente virtual
python -m venv venv

4. No Windows:
venv\Scripts\activate

- No macOS/Linux:
source venv/bin/activate

5. Instale as dependências

- pip install -r requirements.txt

6. Configurar Banco de Dados e Variáveis de Ambiente
Crie o Banco de Dados no MySQL: CREATE DATABASE ow2_stats_db;

7. Crie o arquivo .env: Preencha na raiz do projeto com as credenciais:

- Arquivo .env

DB_HOST = "localhost"
DB_USER = "seu_usuario_mysql"
DB_PSWD = "sua_senha_secreta"
DB_NAME = "ow2_stats_db"

8. Aplicação do Schema (Criação de Tabelas)
TODO CRÍTICO: O arquivo schema.sql deve ser criado e executado no MySQL.

- Exemplo de Tabela de Estatísticas (hero_mao_win) (MySQL):
As chaves primárias e estrangeiras são essenciais para a devida estruturação e lógica de dados da aplicação.

| Campo 	      | Tipo SQL 	           | Descrição                                          |
|-----------------|------------------------|----------------------------------------------------|
| hero_map_win_id | INT NOT NULL           | Chave primária da tabela.                          |
| hero_id	      | INT NOT NULL           | Chave Estrangeira para a tabela de Heróis.         |
| map_id	      | INT NOT NULL	       | Chave Estrangeira para a tabela de Mapas.          |
| win_rate	      | DECIMAL(5, 2) NOT NULL | Taxa de vitória do herói naquele mapa (Ex: 52.15). |

9. Carga com UPSERT (Em Desenvolvimento)...

# Com o venv ativo
uvicorn main:app --reload --host 0.0.0.0 --port 8000
O servidor estará rodando em http://127.0.0.1:8000.

Acesse a documentação interativa (Swagger UI) para testes em: http://127.0.0.1:8000/docs.

##### Opcional
- Inicialição no RESDIS na porta: 6379
- ###### REDIS_URL="redis://localhost:6379" 


🏃 COMO RODAR A APLICAÇÃO
Para iniciar a API:

Bash

- ARRUMA O README ↓
## Com o venv ativo
uvicorn main:app --reload --host 0.0.0.0 --port 8000
O servidor estará rodando em http://127.0.0.1:8000.

A documentação interativa (Swagger UI) para testes está em: http://127.0.0.1:8000/docs.

## 📝 EXEMPLOS DE USO DA API
A API segue um padrão CRUD genérico para as tabelas básicas (hero, map, role, rank, etc.) listadas na Whitelist. Usaremos a tabela hero como exemplo.

URL Base: http://127.0.0.1:8000

1. Consulta Genérica (GET)
Rota para buscar todos os registros de uma tabela autorizada.

Verbo	Rota	Descrição
GET	/get/{table_name}	Retorna todos os itens da tabela.

Exportar para as Planilhas
Exemplo: Buscar todos os Heróis

Bash

curl -X GET "http://127.0.0.1:8000/get/hero"
Resposta de Sucesso (Status 200 OK):

JSON

[
  {
    "hero_id": 1,
    "hero_name": "Tracer",
    "hero_role": "Damage"
  },
  {
    "hero_id": 2,
    "hero_name": "Genji",
    "hero_role": "Damage"
  }
]
2. Inserção de Dados (POST)
Rota para inserir um novo item em uma tabela. O corpo da requisição DEVE seguir o modelo Pydantic da tabela correspondente.

Verbo	Rota	Descrição
POST	/insert/{table_name}	Insere um novo registro na tabela.

Exportar para as Planilhas
Exemplo: Inserir um novo Herói (Body JSON)

Bash

curl -X POST "http://127.0.0.1:8000/insert/hero" -H "Content-Type: application/json" -d '
{
  "hero_name": "Mauga",
  "hero_role": "Tank",
  "hero_icon_img_link": "link_para_imagem.png"
}'
Resposta de Sucesso (Status 200 OK):

JSON

{
  "message": "Dados inseridos com sucesso na tabela 'hero'.",
  "new_id": 3
}
3. Atualização de Dados (PUT)
Rota para atualizar um registro existente. O item_id deve estar na URL.

Verbo	Rota	Descrição
PUT	/update/{table_name}/{item_id}	Atualiza o registro com o ID fornecido.

Exportar para as Planilhas
Exemplo: Alterar o Role do Herói com ID 1 (Tracer)

Bash

curl -X PUT "http://127.0.0.1:8000/update/hero/1" -H "Content-Type: application/json" -d '
{
  "hero_role": "DPS" 
}'
Resposta de Sucesso (Status 200 OK):

JSON

{
  "message": "Item com ID 1 atualizado com sucesso na tabela 'hero'.",
  "rows_affected": 1
}
4. Exclusão de Dados (DELETE)
Rota para excluir um registro existente.

Verbo	Rota	Descrição
DELETE	/delete/{table_name}/{item_id}	Exclui o registro com o ID fornecido.

Exportar para as Planilhas
Exemplo: Excluir o Herói com ID 3 (Mauga)

Bash

curl -X DELETE "http://127.0.0.1:8000/delete/hero/3"
Resposta de Sucesso (Status 200 OK):

JSON

{
  "message": "Item com ID 3 excluído com sucesso da tabela 'hero'.",
  "rows_affected": 1
}
