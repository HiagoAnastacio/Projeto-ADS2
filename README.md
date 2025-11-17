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
    <li><a href="#-próximos-passos-roadmap">Próximos Passos (Roadmap)</a></li>
    <li><a href="#-licença">Licença</a></li>
    <li><a href="#-contato">Contato</a></li>
  </ol>
</details>

---

### 🚀 Sobre o Projeto

Este projeto consiste em um backend robusto construído com **FastAPI** que serve uma **API RESTful** para acesso a dados estatísticos do jogo Overwatch 2. Os dados são coletados e mantidos atualizados por um **pipeline de ETL (Extração, Transformação e Carga)** automatizado que utiliza a API interna da Blizzard.

A principal característica do projeto é o **armazenamento historiográfico** dos dados. Ao contrário da plataforma oficial, nosso banco de dados salva *snapshots* do meta ao longo do tempo (a cada execução do pipeline), permitindo análises temporais detalhadas sobre como o balanceamento afeta o jogo.

A arquitetura de BI (Business Intelligence) utiliza **Renderização no Lado do Cliente (Client-Side Rendering)**. O backend expõe um endpoint de consulta analítica (`POST /analysis/query`) que retorna JSON bruto, e o frontend utiliza a biblioteca **Recharts** para desenhar os gráficos interativos.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 🏛️ Arquitetura e Princípios

O backend segue uma arquitetura modular e aderente aos princípios de boas práticas de desenvolvimento:

* **Separação de Responsabilidades (SoC):**
    * **API (FastAPI):** Lida com requisições HTTP (`routes/`), validação (`model/models.py`) e gerenciamento de conexões (`utils/db_manager.py`).
    * **Pipeline de ETL (APScheduler + `services/`):** A lógica de ETL é desacoplada em três camadas (Extractors, Loaders, Orchestrators).
* **Don't Repeat Yourself (DRY):**
    * **API Genérica:** Utiliza rotas dinâmicas (`/{table_name}`) e um resolvedor de modelos (`model_resolver.py`) para evitar a duplicação de código CRUD.
    * **Helpers (Utils):** Funções comuns (como requisições HTTP ou execução de SQL) são centralizadas.
* **API RESTful:** As rotas seguem os padrões REST, com versionamento (`/API/V1-DATA/`).
* **Armazenamento Historiográfico:**
    * As tabelas de fato (ex: `hero_rank_win`) são projetadas para armazenar *snapshots* históricos.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### ✨ Tecnologias Utilizadas

#### Backend (Python)
* **Framework Principal:** FastAPI
* **Servidor ASGI:** Uvicorn
* **Validação de Dados:** Pydantic
* **Agendamento de Tarefas (ETL):** APScheduler
* **Chamadas de API (ETL):** `Requests`
* **Web Scraping (ETL):** `BeautifulSoup4`
* **Configuração:** `python-dotenv`

#### Frontend (JavaScript)
* **Biblioteca Principal:** React
* **Ferramenta de Build/Servidor:** Vite
* **Cliente HTTP:** Axios
* **Biblioteca de Gráficos:** **Recharts** (NOVO)
* **Estilização:** Tailwind CSS
* **Linter:** ESLint

#### Banco de Dados
* **SGBD:** MySQL (8.0+)
* **Driver Python:** `mysql-connector-python`

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 🛠️ Guia de Instalação e Uso

(Esta seção permanece a mesma da versão anterior: Pré-requisitos, Instalação, Execução)

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 🌐 Estrutura da API RESTful (v1)

A API segue os padrões RESTful e está versionada sob `/API/V1-DATA/`.

**Endpoints Genéricos (CRUD):**

* `GET /API/V1-DATA/{resource_name}`: Lista todos os registros de uma tabela ou view permitida (`ALLOWED_GET_TABLES`).
* `POST /API/V1-DATA/{resource_name}`: Cria um novo registro.
* `PUT /API/V1-DATA/{resource_name}/{item_id}`: Atualiza um registro.
* `DELETE /API/V1-DATA/{resource_name}/{item_id}`: Exclui um registro.

**Endpoint de Análise (v1.1 - NOVO):**

* `POST /API/V1-DATA/analysis/query`: Um endpoint genérico de consulta de BI (Business Intelligence).
    * **Função:** Permite ao frontend solicitar dados (JSON) complexos e históricos para a renderização de gráficos.
    * **Corpo (Body):** Aceita um objeto `AnalysisQuery` que especifica:
        * `table_name`: A tabela/view a ser consultada (ex: `hero_win` para histórico).
        * `filters_equal`: Filtros de igualdade (ex: `{"hero_id": 1}`).
        * `start_date` / `end_date`: Filtros de período.
    * **Resposta:** Retorna um JSON com os dados brutos para o frontend renderizar o gráfico (via Recharts).

**Endpoint de Documentação Auxiliar:**

* `GET /API/V1-DATA/models/{table_name}/example`: Retorna um exemplo de corpo JSON esperado para uma tabela específica.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 🔄 Pipeline de ETL

O pipeline automatizado (`data_uploader.py`) é responsável por manter o banco de dados atualizado.

* **Arquitetura (SoC):** O pipeline segue um padrão modular de **Extração, Carga e Orquestração** (E-L-O).
    * **`services/extractors/`**: Responsável por extrair dados das fontes externas (API da Blizzard, Web Scraping).
    * **`services/loaders/`**: Responsável por carregar (inserir/atualizar) os dados no banco de dados.
    * **`services/orchestrators/`**: Responsável por controlar o fluxo (ex: "primeiro extraia os heróis, depois carregue os heróis").
* **Lógica de Coleta de Fatos:**
    * O orquestrador (`run_stats_lvl3_pipeline.py`) chama o extrator (`info_stats_lvl3_extractor.py`) iterativamente com diferentes combinações de filtros.
    * **Lógica de Derivação (Transformação):** Como a API não fornece todas as agregações (ex: média por rank), o orquestrador primeiro insere os dados granulares e depois executa queries `INSERT ... SELECT ... GROUP BY` para calcular e popular as tabelas agregadas restantes.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 💾 Banco de Dados

* **Tecnologia:** MySQL 8.0+.
* **Modelo:** Híbrido, com tabelas de **Dimensão** (`hero`, `rank`, `map`, etc.) e tabelas de **Fato** (`hero_win`, `hero_rank_win`, etc.).
* **Integridade:** Dimensões usam `UNIQUE KEY` nos nomes para evitar duplicatas.
* **Historicidade:** Tabelas de fato usam `UNIQUE KEY` no contexto + data (ex: `uq_hero_rank_win_snapshot (hero_id, rank_id, date_of_the_data)`).
* **Views `_latest`:** Para cada tabela de fato, existe uma view (`vw_hero_win_latest`, etc.) que usa `ROW_NUMBER()` para exibir *apenas* o registro mais recente para cada contexto, otimizando as consultas do frontend.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 🗺️ Próximos Passos (Roadmap)

-   [ ] **Desenvolvimento do Frontend (Fase Atual):**
    * **Objetivo:** Implementar dashboards interativos (Renderização no Cliente).
    * **Ação:** Atualizar o `frontend/src/services/api_manager.js` para consumir o novo endpoint `POST /API/V1-DATA/analysis/query`.
    * **Ação:** Atualizar o `frontend/src/App.jsx` para usar a biblioteca **Recharts** para renderizar gráficos (ex: gráfico de linha) com os dados JSON recebidos.
-   [ ] **Refatoração do Extrator (Backend/ETL):**
    * **Objetivo:** Tornar a extração de dados resiliente a falhas da API da Blizzard.
    * **Ação:** Implementar a lógica de "Teste A/B" no `info_stats_lvl3_extractor.py` para validar os dados contra "falhas silenciosas" (conforme discutido).
-   [ ] **Refatoração de Dimensões (Backend/DB):**
    * **Objetivo:** Transformar os filtros fixos (`region=Americas`) em dimensões dinâmicas.
-   [ ] **Adicionar Análise Contextual (A Fazer):**
    * **Objetivo:** Justificar as estatísticas com informações qualitativas (ex: "Genji fraco no Bronze...").
-   [ ] **Ativação da Segurança em Produção:** Ativar e configurar o `Rate Limiting`. Ajustar as origens do `CORSMiddleware`.
-   [ ] **Testes:** Implementar testes unitários e de integração.
-   [ ] **Deployment:** Configurar o deploy da API e do banco de dados.

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