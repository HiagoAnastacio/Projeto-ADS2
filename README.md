<a id="readme-top"></a>

<br />
<div align="center">

<h1 align="center">Overwatch 2 - Stats API & ETL Pipeline</h3>

  <p align="center">
    Um backend de alta performance em FastAPI para extração, gestão e análise de estatísticas de heróis de Overwatch 2.
    <br />
    <br />
    <a href="https://github.com/HiagoAnastacio/Projeto-ADS2/issues">Reportar Bug</a>
    ·
    <a href="https://github.com/HiagoAnastacio/Projeto-ADS2/issues/new?labels=enhancement&template=feature-request---.md">Sugerir Funcionalidade</a>
  </p>
</div>

<details>
  <summary><strong>📝 Sumário</strong></summary>
  <ol>
    <li><a href="#-sobre-o-projeto">Sobre o Projeto</a></li>
    <li><a href="#-arquitetura-e-princípios">Arquitetura e Princípios</a></li>
    <li><a href="#-tecnologias-utilizadas">Tecnologias Utilizadas</a></li>
    <li>
      <a href="#-guia-de-instalação-e-uso">Guia de Instalação e Uso</a>
      <ul>
        <li><a href="#pré-requisitos">Pré-requisitos</a></li>
        <li><a href="#instalação-e-configuração">Instalação e Configuração</a></li>
      </ul>
    </li>
    <li><a href="#-exemplos-de-uso-da-api">Exemplos de Uso da API</a></li>
    <li>
      <a href="#-evolução-do-projeto">Evolução do Projeto</a>
      <ul>
        <li><a href="#histórico-de-modificações">Histórico de Modificações</a></li>
        <li><a href="#ideias-em-prototipagem">Ideias em Prototipagem</a></li>
        <li><a href="#próximos-passos-roadmap">Próximos Passos (Roadmap)</a></li>
      </ul>
    </li>
    <li><a href="#-licença">Licença</a></li>
  </ol>
</details>

## 🎯 Sobre o Projeto

Este projeto é uma API RESTful robusta, construída com FastAPI, que serve como a espinha dorsal para uma futura aplicação de análise de meta de Overwatch 2. Ele vai além de uma simples API, implementando um pipeline de ETL (Extração, Transformação e Carga) completo e automatizado para manter um banco de dados relacional sempre atualizado com as estatísticas mais recentes do jogo.

A fonte de dados é uma API não documentada da própria Blizzard, descoberta através de técnicas de análise de rede, o que torna o processo de coleta de dados um desafio interessante de engenharia.

### ✨ Principais Funcionalidades

* **API RESTful Genérica:** Endpoints CRUD (GET, POST, PUT, DELETE) dinâmicos e seguros para interagir com as tabelas do banco de dados.
* **Pipeline de ETL Automatizado:** Um conjunto de scripts orquestrados que popula o banco de dados de forma inteligente, respeitando uma hierarquia de 3 níveis para garantir a integridade dos dados.
* **Agendamento de Tarefas:** Um serviço isolado (`scheduler.py`) executa o pipeline de atualização periodicamente (ex: semanalmente), garantindo que as estatísticas se mantenham relevantes sem intervenção manual.
* **Validação de Dados Robusta:** Uso intensivo do Pydantic para validar e tipar todos os dados na camada da API, protegendo o banco de dados contra informações malformadas.
* **Documentação Automática:** A API gera sua própria documentação interativa (Swagger UI), facilitando os testes e o futuro desenvolvimento do frontend.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## 🏛️ Arquitetura e Princípios

O projeto foi desenhado para ser limpo, manutenível e escalável, seguindo princípios sólidos de engenharia de software.

* **Separação de Responsabilidades (SoC):**
    * **API (`app/`):** Focada exclusivamente em expor os dados via HTTP.
    * **Serviços (`services/`):** Contém a lógica de negócios que roda em segundo plano, como o agendamento e a população de dados.
    * **Modelos (`model/`):** Define a estrutura dos dados (Schemas Pydantic) e a interface de acesso ao banco (DAO).

* **Don't Repeat Yourself (DRY):** A lógica de acesso ao banco (`function_execute.py`) e as funções auxiliares de ETL (`data_populate_help.py`) são centralizadas para serem reutilizadas em todo o projeto.

* **Hierarquia de Dados:** O pipeline de população respeita uma estrutura de 3 níveis para garantir a integridade referencial do banco:
    1.  **Nível 1 (Dimensões Estáticas):** Dados que raramente mudam (`role`, `rank`, `map`), populados via script SQL.
    2.  **Nível 2 (Dimensões Dinâmicas):** Dados de referência descobertos via API (`hero`).
    3.  **Nível 3 (Fatos):** As estatísticas que mudam constantemente e dependem dos níveis anteriores.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## 🛠️ Tecnologias Utilizadas

Esta é a stack de tecnologias que dá vida ao projeto:

| Tecnologia | Função na Aplicação |
| :--- | :--- |
| **Python** | Linguagem principal para todo o backend e scripts. |
| **FastAPI** | Framework web assíncrono para a construção da API RESTful de alta performance. |
| **Pydantic** | Validação e tipagem rigorosa de dados. |
| **MySQL** | Banco de dados relacional para persistência dos dados. |
| **Uvicorn** | Servidor ASGI para executar a aplicação FastAPI. |
| **APScheduler** | Biblioteca para agendar a execução automática do pipeline de dados. |
| **Requests** | Biblioteca para realizar as chamadas HTTP para a API da Blizzard. |
| **python-dotenv**| Gerenciamento seguro de variáveis de ambiente. |

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## ⚙️ Guia de Instalação e Uso

Para colocar o projeto para rodar em sua máquina local, siga estes passos:

### Pré-requisitos

* **Python 3.10+**
* **MySQL Server 8.0+** (ou compatível)
* **Git**

### Instalação e Configuração

1.  **Clone o Repositório**
    ```sh
    git clone [https://github.com/SEU-USUARIO/PROJETO-ADS2.git](https://github.com/SEU-USUARIO/PROJETO-ADS2.git)
    cd PROJETO-ADS2
    ```

2.  **Crie e Ative o Ambiente Virtual**
    ```sh
    # Crie o ambiente
    python -m venv .venv

    # Ative no Windows (PowerShell)
    .\.venv\Scripts\activate

    # Ative no macOS/Linux
    source .venv/bin/activate
    ```

3.  **Instale as Dependências**
    ```sh
    pip install -r backend/requirements.txt
    ```

4.  **Configure as Variáveis de Ambiente**
    * Na pasta `backend/`, crie um arquivo chamado `.env`.
    * Preencha-o com suas credenciais do MySQL:
        ```env
        DB_HOST="localhost"
        DB_USER="seu_usuario_mysql"
        DB_PSWD="sua_senha_mysql"
        DB_NAME="projeto_ads2"
        ```

5.  **Prepare o Banco de Dados**
    * **Passo A (Estrutura):** Usando um cliente MySQL, execute o script `backend/data/Database071025.sql` para criar todas as tabelas.
    * **Passo B (Dados Estáticos):** Em seguida, execute o script `SQL.txt` para popular as tabelas de `role`, `rank` e `game_mode`.

6.  **Popule o Banco com Dados da API**
    * Rode os scripts de população na ordem correta. Este processo buscará todos os dados da Blizzard e os inserirá no seu banco.
    ```sh
    # 1. Popula a tabela 'hero'
    python backend/services/scripts/populate_lvl2.py

    # 2. Popula as tabelas de estatísticas (pode demorar vários minutos!)
    python backend/services/scripts/populate_lvl3.py
    ```

7.  **Inicie a API!** 🎉
    * Navegue até a pasta `backend` e inicie o servidor Uvicorn:
    ```sh
    cd backend
    uvicorn app.main:app --reload
    ```
    * Sua API estará rodando em `http://127.0.0.1:8000`.
    * Acesse a documentação interativa em `http://127.0.0.1:8000/docs` para explorar e testar os endpoints.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## 🖥️ Exemplos de Uso da API

A API foi projetada para ser genérica e intuitiva. Aqui estão alguns exemplos usando `curl`:

**URL Base:** `http://127.0.0.1:8000/api`

#### **1. 📥 Buscar todos os heróis (GET)**
* Busca todos os registros da tabela `hero`.
    ```bash
    curl -X GET "[http://127.0.0.1:8000/api/get/hero](http://127.0.0.1:8000/api/get/hero)"
    ```

#### **2. ➕ Inserir um novo mapa (POST)**
* Adiciona um novo registro à tabela `map`. O corpo da requisição deve corresponder ao schema.
    ```bash
    curl -X POST "[http://127.0.0.1:8000/api/insert/map](http://127.0.0.1:8000/api/insert/map)" -H "Content-Type: application/json" -d \
    '{
      "game_mode_id": 1,
      "map_name": "Meu Novo Mapa"
    }'
    ```

#### **3. 🔄 Atualizar um herói (PUT)**
* Atualiza o herói com `hero_id = 1`. Apenas os campos enviados no corpo são alterados.
    ```bash
    curl -X PUT "[http://127.0.0.1:8000/api/update/hero/1](http://127.0.0.1:8000/api/update/hero/1)" -H "Content-Type: application/json" -d \
    '{
      "hero_icon_img_link": "[http://novo.link/imagem.png](http://novo.link/imagem.png)"
    }'
    ```

#### **4. 🗑️ Deletar um mapa (DELETE)**
* Remove o mapa com `map_id = 1`.
    ```bash
    curl -X DELETE "[http://127.0.0.1:8000/api/delete/map/1](http://127.0.0.1:8000/api/delete/map/1)"
    ```

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## 📈 Evolução do Projeto

Esta seção documenta a jornada de desenvolvimento do projeto, as ideias atuais e o que vem pela frente.

### 📜 Histórico de Modificações
* **Estruturação Inicial:** Criação de uma API FastAPI com rotas CRUD genéricas e validação Pydantic.
* **Desenvolvimento do Pipeline ETL:** Implementação do primeiro script para extração de dados da API da Blizzard.
* **Refatoração Arquitetural (SoC):** O pipeline foi refatorado em três scripts especializados (`SQL seed`, `populate_dimensions`, `populate_facts`) e a lógica reutilizável foi movida para um módulo de helpers, melhorando a manutenibilidade.
* **Correção de Inconsistências:** Ajuste do schema e dos scripts para lidar com palavras reservadas do SQL (ex: `rank`) e para garantir a unicidade de dados nas tabelas de dimensão.
* **Automação:** Implementação de um serviço de agendamento (`scheduler.py`) para executar o pipeline de atualização de dados periodicamente.

### 🧪 Ideias em Prototipagem
* **Agregação de Dados com Views:** Em vez de popular tabelas agregadas (ex: `hero_win`), a estratégia atual é criar `Views` no banco de dados para calcular essas médias em tempo real, evitando redundância e garantindo dados sempre atualizados.
* **Segurança (Rate Limiting):** A infraestrutura para limitar a taxa de requisições usando `fastapi-limiter` e Redis está presente no código, mas desativada.

### 🗺️ Próximos Passos (Roadmap)
- [ ] **Desenvolvimento do Frontend:** Iniciar a construção da interface do usuário com **React**, que consumirá esta API para exibir os dados.
- [ ] **Ativação da Segurança em Produção:** Ativar e configurar o `CORSMiddleware` para domínios de produção e habilitar o `Rate Limiting` com Redis.
- [ ] **Melhoria no Pipeline de Fatos:** Agregar dados de outras dimensões (ex: por plataforma `console`) no `populate_facts.py`.
- [ ] **Criação de Endpoints Analíticos:** Desenvolver rotas específicas na API para retornar dados já processados (ex: `/api/analysis/top5-winrate-by-rank/{rank_name}`).

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## 📄 Licença

Distribuído sob a Licença MIT. Veja `LICENSE.txt` para mais informações.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/SEU-USUARIO/PROJETO-ADS2/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/SEU-USUARIO/PROJETO-ADS2/blob/master/LICENSE.txt