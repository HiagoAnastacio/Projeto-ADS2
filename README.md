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
    <li><a href="#-contribuição">Contribuição</a></li>
    <li><a href="#-licença">Licença</a></li>
    <li><a href="#-contato">Contato</a></li>
  </ol>
</details>

---

### 🚀 Sobre o Projeto

Este projeto consiste em um backend robusto construído com **FastAPI** que serve uma **API RESTful** para acesso a dados estatísticos do jogo Overwatch 2. Os dados são coletados e mantidos atualizados por um **pipeline de ETL (Extração, Transformação e Carga)** automatizado que utiliza a API interna da Blizzard.

A principal característica do projeto é o **armazenamento historiográfico** dos dados. Ao contrário da plataforma oficial, nosso banco de dados salva *snapshots* do meta ao longo do tempo (a cada execução do pipeline), permitindo análises temporais detalhadas sobre como o balanceamento afeta o jogo.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 🏛️ Arquitetura e Princípios

O backend segue uma arquitetura modular e aderente aos princípios de boas práticas de desenvolvimento:

* **Separação de Responsabilidades (SoC):**
    * **API (FastAPI):** Lida com requisições HTTP, validação (Pydantic) e orquestração. Utiliza um **Pool de Conexões** (`db_manager.py`) para acesso otimizado ao DB.
    * **Pipeline de ETL (APScheduler + Scripts):** Responsável pela coleta, transformação e carga dos dados. Opera de forma independente da API e utiliza uma **conexão de DB dedicada** (`model/db.py`, `utils/function_execute.py`) para *jobs* de longa duração.
* **Don't Repeat Yourself (DRY):**
    * **API Genérica:** Utiliza rotas dinâmicas (`/{table_name}`) e um resolvedor de modelos (`model_resolver.py`) para evitar a duplicação de código CRUD para cada tabela/view.
    * **Whitelists Centralizadas:** As permissões de acesso às tabelas/views são definidas em um único local (`table_whitelist_security.py`).
* **API RESTful:** As rotas seguem os padrões REST, utilizando verbos HTTP corretamente e URLs focadas em recursos (substantivos), com versionamento (`/API/V1-DATA/`).
* **Armazenamento Historiográfico (v0.6.0):**
    * As tabelas de fato (ex: `hero_rank_win`) são projetadas para armazenar *snapshots* históricos.
    * Usam `UNIQUE KEY` na combinação do contexto e da data (ex: `UNIQUE KEY (hero_id, rank_id, date_of_the_data)`) para garantir que cada snapshot seja um registro único.
* **Integridade de Dados:** As tabelas de dimensão (ex: `hero`, `rank`) usam `UNIQUE KEY` nos nomes (ex: `UNIQUE KEY (hero_name)`) para prevenir dados duplicados e permitir atualizações (`ON DUPLICATE KEY UPDATE`) pelo ETL.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### ✨ Tecnologias Utilizadas

#### Backend (Python)
* **Framework Principal:** FastAPI
* **Servidor ASGI:** Uvicorn
* **Validação de Dados:** Pydantic
* **Agendamento de Tarefas (ETL):** APScheduler
* **Geração de Gráficos (Dashboard):** **Matplotlib** (NOVO)
* **Chamadas de API (ETL):** `Requests`
* **Web Scraping (ETL):** `BeautifulSoup4`
* **Utilitário de URL (ETL):** `python-slugify`
* **Configuração:** `python-dotenv`

#### Frontend (JavaScript)
* **Biblioteca Principal:** React
* **Ferramenta de Build/Servidor:** Vite
* **Cliente HTTP:** Axios
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
* `GET /API/V1-DATA/{resource_name}/{item_id}`: Busca um registro específico pelo ID. (Restrito a tabelas de dimensão simples).
* `POST /API/V1-DATA/{resource_name}`: Cria um novo registro em uma tabela permitida (`ALLOWED_WRITE_TABLES`).
* `PUT /API/V1-DATA/{resource_name}/{item_id}`: Atualiza um registro existente em uma tabela permitida.
* `DELETE /API/V1-DATA/{resource_name}/{item_id}`: Exclui um registro existente em uma tabela permitida.

**Endpoint de Documentação Auxiliar:**

* `GET /API/V1-DATA/models/{table_name}/example`: Retorna um exemplo de corpo JSON esperado para uma tabela específica.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 🔄 Pipeline de ETL

O pipeline automatizado (`data_uploader.py`) é responsável por manter o banco de dados atualizado.

* **Orquestração:** Gerenciado pelo `APScheduler` dentro do ciclo de vida do FastAPI.
* **Execução em Etapas:**
    1.  `populate_scrape_map_lvl2.py`: Extrai e carrega mapas e modos de jogo.
    2.  `populate_hero_lvl2.py`: Extrai e carrega/atualiza heróis e suas roles.
    3.  `populate_lvl3.py` (v0.6.1): Popula **todas** as tabelas de fato.
* **Lógica de Coleta de Fatos (v0.6.1):**
    * O script chama a API da Blizzard (`.../rates/data/?...`) iterativamente com diferentes combinações de filtros (ex: `tier=gold, map=dorado`).
    * **Lógica de Derivação (Etapa 4):** Como a API não fornece *todas* as agregações (ex: média por rank, média por modo de jogo), o script primeiro insere os dados granulares que coleta (ex: `hero_rank_map_win`) e depois executa queries `INSERT ... SELECT ... GROUP BY` para calcular e popular as tabelas agregadas restantes (`hero_rank_win`, `hero_gamemode_win`, etc.).
    * **Consistência:** Um *timestamp* único (`execution_timestamp`) é usado para todas as inserções de uma única execução, garantindo que os dados derivados correspondam aos dados coletados.
* **Filtros Fixos:** O ETL está configurado para buscar dados apenas de `region=Americas` e `rq=2` (Ranked) para garantir a consistência dos dados.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 💾 Banco de Dados

* **Tecnologia:** MySQL 8.0+.
* **Modelo:** Híbrido, com tabelas de **Dimensão** (`hero`, `rank`, `map`, etc.) e tabelas de **Fato** (`hero_win`, `hero_rank_win`, etc.).
* **Integridade:** Dimensões usam `UNIQUE KEY` nos nomes (ex: `uq_hero_name`) para evitar duplicatas.
* **Historicidade:** Tabelas de fato usam `id AUTO_INCREMENT PRIMARY KEY` e `UNIQUE KEY` no contexto + data (ex: `uq_hero_rank_win_snapshot (hero_id, rank_id, date_of_the_data)`). Isso permite que o ETL insira um novo registro para o mesmo contexto em momentos diferentes.
* **Views `_latest`:** Para cada tabela de fato, existe uma view (`vw_hero_win_latest`, `vw_hero_rank_map_win_latest`, etc.) que usa `ROW_NUMBER()` para exibir *apenas* o registro mais recente para cada contexto, otimizando as consultas do frontend.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

---

### 🗺️ Próximos Passos (Roadmap)

-   [ ] **Desenvolvimento do Frontend:** (Fase Atual) Implementar filtros interativos (dropdowns) para permitir a análise dos dados das views `_latest`.
-   [ ] **Implementar Geração de Dashboards (Backend):**
    * **Objetivo:** Criar endpoints que retornem gráficos como imagens.
    * **Ação:** Usar **Matplotlib** no `analysis/plot_generator.py` para criar funções que geram gráficos (ex: gráfico de linhas).
    * **Ação:** Criar os endpoints em `routes/analytic_routes/route_analysis.py` (ex: `GET /API/V1-DATA/analysis/hero_history/{hero_id}`) que:
        1.  Buscam o histórico de dados de uma tabela de fato (ex: `hero_win`).
        2.  Passam os dados para o `plot_generator.py`.
        3.  Retornam a imagem (PNG) gerada para o frontend.
-   [ ] **Refatoração de Dimensões (Backend/DB):**
    * **Objetivo:** Transformar os filtros fixos (`region=Americas`, `rq=2`) em dimensões dinâmicas.
    * **Ação:** Adicionar tabelas de dimensão `region` e `queue_type` ao `data/Sql_build.sql`.
    * **Ação:** Modificar o ETL para iterar sobre essas novas dimensões, populando o banco com dados globais.
-   [ ] **Adicionar Análise Contextual (A Fazer):**
    * **Objetivo:** Justificar as estatísticas com informações qualitativas (conforme sua sugestão).
    * **Ação:** Adicionar uma tabela ou mecanismo para armazenar notas de análise (ex: "Genji fraco no Bronze devido à alta curva de aprendizado") e exibi-las no frontend.
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