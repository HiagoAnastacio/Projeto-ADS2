<a id="readme-top"></a>

<br />
<div align="center">
  
<h2 align="center">Overwatch 2 - Stats API & ETL Pipeline</h2>

  <p align="center">
    Um backend de alta performance em FastAPI para extração, gestão e análise de estatísticas de heróis de Overwatch 2, com um pipeline de dados totalmente automatizado e suporte a histórico de dados.
    <br />
    <a href="https://github.com/HiagoAnastacio/Projeto-ADS2/issues">Reportar Bug</a>
    ·
    <a href="https://github.com/HiagoAnastacio/Projeto-ADS2/issues/new?labels=enhancement&template=feature-request---.md">Sugerir Funcionalidade</a>
  </p>
</div>

<details open>
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
        <li><a href="#executando-a-aplicação">Executando a Aplicação</a></li>
      </ul>
    </li>
    <li><a href="#-estrutura-da-api-restful-v1">Estrutura da API RESTful (v1)</a></li>
    <li><a href="#-pipeline-de-etl">Pipeline de ETL</a></li>
    <li><a href="#-banco-de-dados">Banco de Dados</a></li>
    <li><a href="#-histórico-de-melhorias-recentes">Histórico de Melhorias Recentes</a></li>
    <li><a href="#-próximos-passos-roadmap">Próximos Passos (Roadmap)</a></li>
    <li><a href="#-contribuição">Contribuição</a></li>
    <li><a href="#-licença">Licença</a></li>
    <li><a href="#-contato">Contato</a></li>
  </ol>
</details>

---

### 🚀 Sobre o Projeto

Este projeto consiste em um backend robusto construído com **FastAPI** que serve uma **API RESTful** para acesso a dados estatísticos do jogo Overwatch 2. Os dados são coletados e mantidos atualizados por um **pipeline de ETL (Extração, Transformação e Carga)** automatizado que utiliza fontes como a API oficial da Blizzard e técnicas de Web Scraping. Uma característica chave é o **armazenamento historiográfico** dos dados, permitindo análises de tendências ao longo do tempo.

O objetivo é fornecer uma fonte de dados confiável e performática para um frontend (a ser desenvolvido em React) ou outras aplicações analíticas.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 🏛️ Arquitetura e Princípios

O backend segue uma arquitetura modular e aderente aos princípios de boas práticas de desenvolvimento:

* **Separação de Responsabilidades (SoC):**
    * **API (FastAPI):** Lida exclusivamente com requisições HTTP, validação de entrada/saída e orquestração da lógica de negócio. Utiliza um **Pool de Conexões** (`db_manager.py`) para acesso otimizado ao banco de dados.
    * **Pipeline de ETL (APScheduler + Scripts):** Responsável pela coleta, transformação (mínima) e carga dos dados no banco. Opera de forma independente da API e utiliza uma **conexão de banco de dados dedicada** (`db.py`, `function_execute.py`) adequada para *jobs* de longa duração.
    * **Camada DAO (Data Access Object):** Abstrai a interação direta com o banco de dados MySQL (`db.py`, `function_execute.py`, `db_manager.py`).
    * **Modelos (Pydantic):** Define os schemas de dados (`models.py`) para validação e documentação.
    * **Segurança:** Centraliza configurações de CORS, Rate Limiting (futuro) e Whitelists de acesso a tabelas (`security/`).
* **Don't Repeat Yourself (DRY):**
    * **API Genérica:** Utiliza rotas dinâmicas (`/{table_name}`) e um resolvedor de modelos (`model_resolver.py`) para evitar a duplicação de código CRUD para cada tabela.
    * **Helpers:** Funções reutilizáveis para tarefas comuns como requisições HTTP (`extraction_helpers.py`) e execução de SQL (`function_execute.py`, `db_manager.py`).
    * **Whitelists Centralizadas:** As permissões de acesso às tabelas são definidas em um único local (`table_whitelist_security.py`).
* **API RESTful:** As rotas seguem os padrões REST, utilizando verbos HTTP corretamente e URLs focadas em recursos (substantivos), com versionamento (`/api/v1/`).
* **Armazenamento Historiográfico:** As tabelas de fato utilizam chaves primárias compostas incluindo `date_of_the_data` para permitir o armazenamento de múltiplos *snapshots* das métricas ao longo do tempo.
* **Configuração via Ambiente:** Credenciais e configurações sensíveis são gerenciadas via arquivos `.env`.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### ✨ Tecnologias Utilizadas

* ![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python&logoColor=white)
* ![FastAPI](https://img.shields.io/badge/FastAPI-0.117.1-green?style=flat-square&logo=fastapi&logoColor=white)
* ![Uvicorn](https://img.shields.io/badge/Uvicorn-0.37.0-purple?style=flat-square&logo=python&logoColor=white)
* ![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange?style=flat-square&logo=mysql&logoColor=white)
* ![Pydantic](https://img.shields.io/badge/Pydantic-v2-blue?style=flat-square)
* ![APScheduler](https://img.shields.io/badge/APScheduler-Async-yellow?style=flat-square)
* ![Requests](https://img.shields.io/badge/Requests-HTTP-red?style=flat-square)
* ![BeautifulSoup4](https://img.shields.io/badge/BeautifulSoup4-Scraping-lightblue?style=flat-square)
* ![python-dotenv](https://img.shields.io/badge/python--dotenv-Config-lightgrey?style=flat-square)
* ![python-slugify](https://img.shields.io/badge/python--slugify-Utils-grey?style=flat-square)

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 🛠️ Guia de Instalação e Uso

#### Pré-requisitos

* **Python:** Versão 3.11 ou superior.
* **MySQL:** Servidor MySQL 8.0 ou superior instalado e rodando.
* **Git:** Para clonar o repositório.
* **pip:** Gerenciador de pacotes do Python.

#### Instalação e Configuração

1.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/HiagoAnastacio/Projeto-ADS2.git](https://github.com/HiagoAnastacio/Projeto-ADS2.git)
    cd Projeto-ADS2/backend 
    ```
2.  **Crie e Ative um Ambiente Virtual:**
    ```bash
    python -m venv .venv 
    # Windows
    .\.venv\Scripts\activate 
    # Linux/macOS
    source .venv/bin/activate 
    ```
3.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    pip install -e .  # Instala o projeto em modo editável (essencial para importações)
    ```
4.  **Configure as Variáveis de Ambiente:**
    * Renomeie o arquivo `.env.exemple` para `.env`.
    * Edite o arquivo `.env` e preencha com as credenciais do seu banco de dados MySQL:
        ```env
        DB_HOST='localhost' # Ou o IP/host do seu servidor MySQL
        DB_USER='seu_usuario_mysql'
        DB_PSWD='sua_senha_mysql'
        DB_NAME='projeto_ads2' # Nome do banco de dados a ser criado
        ```
5.  **Crie o Banco de Dados e as Tabelas:**
    * Execute o script `Sql_build.sql` no seu cliente MySQL preferido (MySQL Workbench, DBeaver, terminal `mysql`). Este script criará o banco `projeto_ads2` (se não existir), as tabelas, as views e inserirá os dados iniciais (seeds).

#### Executando a Aplicação

1.  **Inicie a API e o Agendador:**
    * Certifique-se de que seu ambiente virtual está ativado.
    * Na pasta `backend`, execute:
        ```bash
        uvicorn main:app --reload
        ```
    * `--reload`: Faz o servidor reiniciar automaticamente ao detectar alterações no código (ótimo para desenvolvimento).
2.  **Acesse a Documentação da API (Swagger):**
    * Abra seu navegador e acesse: `http://localhost:8000/docs`
3.  **Verifique o Pipeline de ETL:**
    * O pipeline está configurado para rodar automaticamente (por padrão, toda segunda-feira às 02:30, mas pode ser ajustado em `services/data_uploader.py`).
    * Para testes, você pode descomentar a linha `scheduler.add_job(run_update_pipeline)` em `services/data_uploader.py` para que ele rode imediatamente ao iniciar a API.
    * Acompanhe os logs no console onde o `uvicorn` está rodando para ver o progresso e possíveis erros do pipeline.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 🌐 Estrutura da API RESTful (v1)

A API segue os padrões RESTful e está versionada sob `/api/v1`.

**Endpoints Genéricos (CRUD):**

* `GET /api/v1/{resource_name}`: Lista todos os registros de uma tabela ou view permitida (`ALLOWED_GET_TABLES`).
* `GET /api/v1/{resource_name}/{item_id}`: Busca um registro específico pelo ID. **Funciona apenas para tabelas de dimensão simples** (`EDITABLE_TABLES` - hero, map, role, etc.). Retorna 400 para views ou tabelas de fato.
* `POST /api/v1/{resource_name}`: Cria um novo registro em uma tabela permitida (`ALLOWED_WRITE_TABLES`). O corpo JSON é validado contra o schema Pydantic.
* `PUT /api/v1/{resource_name}/{item_id}`: Atualiza um registro existente (permite atualização parcial) em uma tabela permitida (`ALLOWED_WRITE_TABLES`). O corpo JSON é validado.
* `DELETE /api/v1/{resource_name}/{item_id}`: Exclui um registro existente em uma tabela permitida (`ALLOWED_WRITE_TABLES`).

**Endpoint de Documentação Auxiliar:**

* `GET /api/v1/models/{table_name}/example`: Retorna um exemplo de corpo JSON esperado para operações POST/PUT em uma tabela específica (útil para o frontend e testes).

**Segurança:**

* **CORS:** Configurado para permitir requisições de origens de desenvolvimento (`localhost`). Precisa ser ajustado para produção.
* **Whitelists:** O acesso (leitura/escrita) a cada tabela/view é controlado por listas centralizadas em `app/security/table_whitelist_security.py`.
* **Validação:** Os corpos das requisições POST/PUT são rigorosamente validados usando Pydantic.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 🔄 Pipeline de ETL

O pipeline automatizado é responsável por manter o banco de dados atualizado.

* **Orquestração:** Gerenciado pelo `APScheduler` dentro do `services/data_uploader.py`, integrado ao ciclo de vida do FastAPI.
* **Fontes de Dados:** API da Blizzard (para estatísticas de heróis) e Web Scraping (para mapas). **(Atenção: As URLs podem precisar de atualização frequente).**
* **Execução em Etapas:**
    1.  `populate_scrape_map_lvl2.py`: Extrai e carrega mapas e modos de jogo.
    2.  `populate_hero_lvl2.py`: Extrai e carrega/atualiza heróis e suas roles.
    3.  `populate_lvl3.py`: Itera sobre ranks e mapas, busca estatísticas (win/pick rate) da API e insere **novos registros** nas tabelas de fato (`hero_rank_map_win`, `hero_rank_map_pick`).
* **Robustez:** Cada etapa possui tratamento de erro. Falhas críticas (ex: não conseguir carregar heróis) abortam o pipeline, enquanto falhas menos críticas (ex: timeout em uma requisição de stats) são logadas como aviso, permitindo que o pipeline continue.
* **Logging:** Logs detalhados são gerados para acompanhar o progresso e diagnosticar falhas.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 💾 Banco de Dados

* **Tecnologia:** MySQL 8.0+.
* **Modelo:** Híbrido, com tabelas de dimensão (`hero`, `rank`, `map`, etc.) e tabelas de fato (`hero_rank_map_win`, `hero_rank_map_pick`).
* **Historicidade:** As tabelas de fato usam uma chave primária composta (`hero_id`, `rank_id`, `map_id`, `date_of_the_data`) para armazenar o histórico das métricas.
* **Views:** Views (`vw_..._latest`, `vw_hero_win`, etc.) são usadas para fornecer acesso simplificado aos dados mais recentes ou agregações comuns, otimizando as consultas da API. As views `_latest` utilizam *Window Functions* para garantir a exibição apenas do último *snapshot*.
* **Setup:** O script `Sql_build.sql` contém a definição completa do schema, incluindo tabelas, constraints, views e dados iniciais (seeds).

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### ✨ Histórico de Melhorias Recentes (Out/2025)

* **Banco de Dados Historiográfico:** Implementada chave primária composta com data nas tabelas de fato e reescrita das views para suportar análise temporal, exibindo apenas os dados mais recentes por padrão.
* **Otimização de Performance da API:** Introduzido Pool de Conexões para acesso ao banco pela API, separando-o do acesso usado pelo ETL.
* **API RESTful:** Rotas refatoradas para seguir padrões REST, com versionamento `/api/v1`.
* **Robustez do ETL:** Melhorado o tratamento de erros no pipeline, validação de dados da API e logging granular.
* **Correção de Dependências:** Atualizada a biblioteca `python-slugify`.
* **Documentação da API:** Aprimoradas as descrições dos endpoints no Swagger.
* **Estrutura do Projeto:** Utilização do `pyproject.toml` para tratar o backend como um pacote instalável, melhorando as importações.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 🗺️ Próximos Passos (Roadmap)

-   [ ] **Desenvolvimento do Frontend:** Iniciar a construção da interface do usuário com **React/Vite/Tailwind**, que consumirá esta API para exibir os dados.
-   [ ] **Verificação de URLs do ETL:** Confirmar e atualizar as URLs usadas para Web Scraping e acesso à API da Blizzard, pois podem ter mudado. Validar os *slugs* de ranks/mapas.
-   [ ] **Ativação da Segurança em Produção:** Ativar e configurar o `Rate Limiting` (provavelmente com Redis). Ajustar as origens do `CORSMiddleware` para domínios de produção.
-   [ ] **Criação de Endpoints Analíticos:** Desenvolver rotas específicas na API para retornar dados já processados para o frontend (ex: `/api/v1/analysis/top-heroes-by-winrate?rank=gold`).
-   [ ] **Testes:** Implementar testes unitários e de integração.
-   [ ] **Deployment:** Configurar o deploy da API e do banco de dados.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 🙏 Contribuição

Contribuições são o que tornam a comunidade open source um lugar incrível para aprender, inspirar e criar. Qualquer contribuição que você fizer será **muito apreciada**.

Se você tiver alguma sugestão para melhorar este projeto, por favor, faça um fork do repositório e crie um pull request. Você também pode simplesmente abrir uma issue com a tag "enhancement".
Não se esqueça de dar uma estrela ao projeto! Obrigado!

1.  Faça um Fork do Projeto
2.  Crie sua Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit suas Mudanças (`git commit -m 'Add some AmazingFeature'`)
4.  Push para a Branch (`git push origin feature/AmazingFeature`)
5.  Abra um Pull Request

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 📄 Licença

Distribuído sob a Licença MIT. Veja `LICENSE` para mais informações.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 📫 Contato

Hiago Anastacio - hiagoanastacios@gmail.com

Link do Projeto: [https://github.com/HiagoAnastacio/Projeto-ADS2](https://github.com/HiagoAnastacio/Projeto-ADS2)

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>