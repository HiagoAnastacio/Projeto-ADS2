# Overwatch Meta Analyzer

![GitHub repo size](https://img.shields.io/github/repo-size/iuricode/README-template?style=for-the-badge)
![GitHub language count](https://img.shields.io/github/languages/count/iuricode/README-template?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/iuricode/README-template?style=for-the-badge)
![Bitbucket open issues](https://img.shields.io/bitbucket/issues/iuricode/README-template?style=for-the-badge)
![Bitbucket open pull requests](https://img.shields.io/bitbucket/pr-raw/iuricode/README-template?style=for-the-badge)

<img src="https://i.imgur.com/3Q9Q8L2.png" alt="Exemplo de imagem do projeto">

> Uma ferramenta robusta de análise de dados para o ecossistema competitivo de Overwatch 2, fornecendo insights detalhados sobre o "Meta", Win Rates e Pick Rates através de um dashboard interativo.

### Ajustes e melhorias

O projeto ainda está em desenvolvimento e as próximas atualizações serão voltadas nas seguintes tarefas:

- [x] Criação de pipelines de ETL (Extract, Transform, Load)
- [x] Dashboard de Análise (Win Rate & Pick Rate)
- [x] Filtros Dinâmicos (Rank, Mapa, Herói)
- [ ] Otimização para Mobile
- [ ] Integração com Docker (Cloud Deployment)

## 💻 Pré-requisitos

Antes de começar, verifique se você atendeu aos seguintes requisitos:

*   Você instalou a versão mais recente de `Python 3.10+`
*   Você instalou a versão mais recente de `Node.js 18+`
*   Você possui um banco de dados `MySQL 8.0+` configurado e rodando.

## 🚀 Instalando Overwatch Meta Analyzer

Para instalar o Overwatch Meta Analyzer, siga estas etapas:

### Backend (API)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# Configure o .env com suas credenciais do MySQL
```

### Frontend (Dashboard)
```bash
cd frontend
npm install
```

### Banco de Dados
Execute o script `backend/data/Sql_build.sql` no seu servidor MySQL para criar a estrutura necessária.

## ☕ Usando Overwatch Meta Analyzer

Para usar o Meta Analyzer, siga estas etapas:

1.  Inicie a API Backend:
    ```bash
    cd backend
    uvicorn app.main:app --reload
    ```
2.  Inicie o Frontend:
    ```bash
    cd frontend
    npm run dev
    ```
3.  Acesse `http://localhost:5173` no seu navegador.

Acesse a **Seção de Análise**, utilize os filtros no topo para selecionar o contexto desejado (ex: Mapa "King's Row" no Rank "Platinum") e visualize os gráficos de tendência e a tabela detalhada.

## 📫 Contribuindo para Overwatch Meta Analyzer

Para contribuir com Overwatch Meta Analyzer, siga estas etapas:

1.  Bifurque este repositório.
2.  Crie um branch: `git checkout -b <nome_branch>`.
3.  Faça suas alterações e confirme-as: `git commit -m '<mensagem_commit>'`
4.  Envie para o branch original: `git push origin Overwatch-Meta-Analyzer / <local>`
5.  Crie a solicitação de pull.

Como alternativa, consulte a documentação do GitHub em [como criar uma solicitação pull](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

## 🤝 Colaboradores

Agradecemos às seguintes pessoas que contribuíram para este projeto:

<table>
  <tr>
    <td align="center">
      <a href="#">
        <img src="https://i.imgur.com/o2b2r1r.png" width="100px;" alt="Foto do Estudante"/><br>
        <sub>
          <b>Estudantes ADS</b>
        </sub>
      </a>
    </td>
  </tr>
</table>

## 📝 Licença

Esse projeto está sob licença. Veja o arquivo [LICENÇA](LICENSE) para mais detalhes.