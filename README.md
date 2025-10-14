<a id="readme-top"></a>

<br />
<div align="center">
  
<h2 align="center">Overwatch 2 - Stats API & ETL Pipeline</h2>

  <p align="center">
    Um backend de alta performance em FastAPI para extração, gestão e análise de estatísticas de heróis de Overwatch 2, com um pipeline de dados totalmente automatizado.
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
    <li><a href="#-fluxo-de-dados-etl">Fluxo de Dados (ETL)</a></li>
    <li>
      <a href="#-evolução-do-projeto">Evolução do Projeto</a>
      <ul>
        <li><a href="#histórico-de-modificações">Histórico de Modificações</a></li>
        <li><a href="#próximos-passos-roadmap">Próximos Passos (Roadmap)</a></li>
      </ul>
    </li>
    <li><a href="#-licença">Licença</a></li>
  </ol>
</details>

## 🎯 Sobre o Projeto

Este projeto consiste em uma API RESTful robusta, construída com FastAPI, projetada para ser a espinha dorsal de um serviço de análise de meta de Overwatch 2. A aplicação não apenas serve os dados, mas também implementa um pipeline de ETL (Extração, Transformação e Carga) completo e automatizado para manter o banco de dados atualizado com as estatísticas mais recentes do jogo.

A fonte de dados é uma combinação de uma API não documentada da Blizzard (para estatísticas) e Web Scraping (para a lista de mapas), refletindo uma solução de engenharia adaptativa para a ausência de uma API pública completa.

### ✨ Principais Funcionalidades

* **API RESTful Genérica:** Endpoints CRUD (GET, POST, PUT, DELETE) que operam de forma dinâmica e segura sobre um conjunto de tabelas e views autorizadas.
* **Pipeline de ETL Automatizado:** Um conjunto de scripts orquestrados que popula o banco de dados respeitando uma hierarquia de dados de 3 níveis para garantir a integridade referencial.
* **Agendamento Integrado:** Um serviço de agendamento (`data_uploader.py`) que executa o pipeline de atualização periodicamente (ex: semanalmente). Ele é iniciado junto com a API através do `lifespan` do FastAPI, eliminando a necessidade de gerenciar processos separados.
* **Dados Agregados com Views:** As tabelas de dados agregados (ex: `hero_win`) foram substituídas por `Views` do MySQL, que calculam as médias em tempo real. Isso evita redundância de dados e garante que as informações estejam sempre consistentes.
* **Validação de Dados Robusta:** Uso intensivo do Pydantic para validar e tipar todos os dados na camada da API, protegendo o banco de dados contra informações malformadas.
* **Documentação Automática:** A API gera sua própria documentação interativa (Swagger UI), facilitando os testes e o desenvolvimento do frontend.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## 🏛️ Arquitetura e Princípios

O projeto foi desenhado para ser limpo, manutenível e escalável, seguindo princípios sólidos de engenharia de software.

* **Separação de Responsabilidades (SoC):**
    * **API (`app/`):** Focada exclusivamente em expor os dados via HTTP.
    * **Serviços (`services/`):** Contém a lógica de negócios que roda em segundo plano, como o agendamento e os scripts de população de dados.
    * **Modelos (`model/`):** Define a estrutura dos dados (Schemas Pydantic) e a interface de acesso ao banco (DAO).

* **Don't Repeat Yourself (DRY):** A lógica de acesso ao banco (`function_execute.py`) e as funções de extração (`extraction_helpers.py`) são centralizadas para serem reutilizadas em todo o projeto.

* **Hierarquia de Dados:** O pipeline de população respeita uma estrutura de 3 níveis para garantir a integridade referencial do banco:
    1.  **Nível 1 (Dimensões Estáticas):** Dados que raramente mudam (`role`, `rank`, `game_mode`), populados via script SQL `Sql_build.sql`.
    2.  **Nível 2 (Dimensões Dinâmicas):** Dados de referência que são descobertos (`hero` via API, `map` via Web Scraping).
    3.  **Nível 3 (Fatos):** As estatísticas que mudam constantemente e dependem dos níveis anteriores.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## 🛠️ Tecnologias Utilizadas

Esta é a stack de tecnologias que dá vida ao projeto:

| Tecnologia | Função na Aplicação |
| :--- | :--- |
| **Python** | Linguagem principal para todo o backend e scripts. |
| **FastAPI** | Framework web assíncrono para a construção da API RESTful. |
| **Pydantic** | Validação e tipagem rigorosa de dados. |
| **MySQL** | Banco de dados relacional para persistência dos dados. |
| **Uvicorn**| Servidor ASGI para executar a aplicação FastAPI. |
| **APScheduler** | Biblioteca para agendar a execução automática do pipeline de dados. |
| **Requests** | Biblioteca para realizar as chamadas HTTP para a API da Blizzard. |
| **BeautifulSoup4** | Biblioteca para Web Scraping do HTML da página de mapas da Blizzard. |
| **python-dotenv** | Gerenciamento seguro de variáveis de ambiente. |

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

2.  **Crie e Ative o Ambiente Virtual (dentro do backend)**
    ```sh
    cd backend
    python -m venv .venv

    # Ative no Windows (PowerShell)
    .\.venv\Scripts\activate

    # Ative no macOS/Linux
    source .venv/bin/activate
    ```

3.  **Instale as Dependências**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configure as Variáveis de Ambiente**
    * Ainda na pasta `backend/`, crie um arquivo chamado `.env`.
    * Preencha-o com suas credenciais do MySQL:
        ```env
        DB_HOST="localhost"
        DB_USER="seu_usuario_mysql"
        DB_PSWD="sua_senha_mysql"
        DB_NAME="projeto_ads2"
        ```

5.  **Prepare o Banco de Dados (Setup Inicial)**
    * Usando um cliente MySQL (Workbench, etc.), execute o script `backend/data/Sql_build.sql`. Isso irá criar o schema, as tabelas, os dados estáticos e as `Views`.

6.  **Execute a Carga Inicial de Dados Dinâmicos**
    * Rode os scripts de população de Nível 2 e 3 **uma vez**, manualmente, para a carga inicial.
    ```sh
    # 1. Popula a tabela 'map' via Web Scraping
    python services/scripts/scrape_maps_lvl2.py

    # 2. Popula a tabela 'hero' via API
    python services/scripts/populate_hero_lvl2.py

    # 3. Popula as tabelas de estatísticas (pode demorar vários minutos!)
    python services/scripts/populate_lvl3.py
    ```

7.  **Inicie a Aplicação Completa (API + Agendador)!** 🎉
    * Com tudo populado, inicie o servidor Uvicorn. Este comando único ativa tanto a API quanto o serviço de agendamento em segundo plano.
    ```sh
    # Estando na pasta 'backend'
    uvicorn app.main:app --reload
    ```
    * Sua API estará rodando em `http://127.0.0.1:8000`.
    * Acesse a documentação interativa em `http://127.0.0.1:8000/docs`.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## 🌊 Fluxo de Dados (ETL)

O coração do projeto é o pipeline automatizado de Extração, Transformação e Carga (ETL).

* **Extração (Fetch):**
    * **Estatísticas (`hero`, `win_rate`, `pick_rate`):** Utiliza a biblioteca `requests` para chamar a API interna da Blizzard. Uma simulação de navegador é feita ao incluir um cabeçalho `User-Agent` na requisição. Os dados já são recebidos em formato JSON.
    * **Mapas (`map`):** Utiliza `requests` e `BeautifulSoup4` para fazer Web Scraping da página de mapas da Blizzard, extraindo os nomes dos mapas e seus modos de jogo diretamente do HTML.

* **Transformação (Transform):**
    * Os dados brutos da API e do scraping são limpos e estruturados em dicionários Python pelos scripts de população.
    * As chaves estrangeiras (como `role_id`, `rank_id`) são resolvidas consultando dicionários em memória que foram previamente carregados do banco de dados.

* **Carga (Load):**
    * Os scripts constroem e executam queries SQL `INSERT ... ON DUPLICATE KEY UPDATE` para inserir os novos dados ou atualizar os existentes, garantindo que o banco de dados reflita as estatísticas mais recentes.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## 📈 Evolução do Projeto

Esta seção documenta a jornada de desenvolvimento do projeto, as ideias atuais e o que vem pela frente.

### 📜 Histórico de Modificações
* **Estruturação Inicial:** Criação de uma API FastAPI com rotas CRUD genéricas e validação Pydantic.
* **Desenvolvimento do Pipeline ETL:** Implementação dos primeiros scripts para extração de dados da API da Blizzard e Web Scraping.
* **Refatoração Arquitetural (SoC):** O pipeline foi refatorado em múltiplos scripts especializados (`scrape_maps_lvl2`, `populate_hero_lvl2`, `populate_lvl3`) e a lógica reutilizável de extração foi movida para um módulo de helpers (`utils/extraction_helpers`).
* **Otimização do Banco de Dados:** As tabelas de dados agregados foram substituídas por `Views` do MySQL para evitar redundância, garantir consistência e simplificar o pipeline de carga.
* **Automação Integrada:** O serviço de agendamento (`data_uploader.py`) foi integrado ao ciclo de vida da API principal usando `lifespan`, permitindo que ambos os serviços rodem com um único comando.

### 🗺️ Próximos Passos (Roadmap)
- [ ] **Desenvolvimento do Frontend:** Iniciar a construção da interface do usuário com **React**, que consumirá esta API para exibir os dados.
- [ ] **Ativação da Segurança em Produção:** Ativar e configurar o `CORSMiddleware` para domínios de produção e habilitar o `Rate Limiting`.
- [ ] **Melhoria no Pipeline de Fatos:** Agregar dados de outras dimensões (ex: por plataforma `console`) no `populate_lvl3.py`.
- [ ] **Criação de Endpoints Analíticos:** Desenvolver rotas específicas na API para retornar dados já processados (ex: `/api/analysis/top5-winrate-by-rank/{rank_name}`).

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## 📄 Licença

Distribuído sob a Licença MIT.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>