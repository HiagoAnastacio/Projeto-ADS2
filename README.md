# Overwatch Meta Analyzer

> Uma plataforma de análise de dados avançada para Overwatch 2, focado em visualização de tendências de meta, taxas de vitória e escolha de heróis através de patchs.

![Status do Projeto](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)
![Versão](https://img.shields.io/badge/Versão-0.8.0-blue)

## 📋 Sobre o Projeto

O **Overwatch Meta Analyzer** é uma ferramenta desenvolvida para transformar dados brutos de partidas em insights acionáveis. Diferente de trackings convencionais, nosso foco é a **análise histórica e comparativa** entre mudanças de balanceamento (patches).

### Diferenciais
- **Análise Multi-Dimensional**: Filtre por Herói, Função, Mapa, Rank e Modo de Jogo simultaneamente.
- **Interatividade Visual**: Gráficos sincronizados com efeitos de "Highlight & Dimming" para foco instantâneo.
- **Contexto Histórico**: Compare métricas entre patches específicos para entender o impacto de buffs e nerfs.

## 🚀 Funcionalidades (Fase 2 - Completa)

### 📊 Painel Analítico
- **Filtros de Linguagem Natural**: Interface intuitiva ("Analisar [Heróis] em [Mapa]...") que constrói a query visualmente.
- **Seleção Múltipla**: Compare `Ana`, `Baptiste` e `Kiriko` no mesmo gráfico com coloração distinta.
- **Filtros Dinâmicos**: O sistema ajusta automaticamente as opções (ex: ao selecionar "Role", remove seleção de "Heróis").

### 📈 Visualização de Dados
- **Gráficos de Tendência**: Linhas do tempo para Win Rate e Pick Rate.
- **Highlight Sincronizado**: Ao passar o mouse sobre um herói (gráfico ou legenda), ele é destacado em **todos** os painéis.
- **Legendas Inteligentes**:
  - **Tooltips Focados**: Mostram apenas os dados do herói em destaque.
  - **Dimming**: Nomes não selecionados na legenda ficam opacos para reduzir ruído visual.

### 📱 Experiência do Usuário
- **Design Responsivo**: Interface adaptada para desktop e correções de usabilidade para mobile.
- **Feedback Visual**: Loaders, estados de erro e interações de hover refinadas.

## 🛠️ Tecnologias Utilizadas

- **Frontend**: React.js, TailwindCSS, Recharts, Lucide Icons.
- **Backend**: FastAPI (Python), Pandas.
- **Banco de Dados**: MySQL (Estrutura Data Warehouse - Star/Snowflake Schema).

## 📦 Como Executar

1. **Clone o Repositório**
   ```bash
   git clone https://github.com/SeuUsuario/Projeto-ADS2.git
   cd Projeto-ADS2
   ```

2. **Backend (API)**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. **Frontend (Interface)**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Acesse**: `http://localhost:5173`

## 🤝 Contribuição

Este é um projeto acadêmico (ADS - Senac). Sugestões via Issues são bem-vindas!

---
*Desenvolvido pela Equipe do Projeto ADS2*