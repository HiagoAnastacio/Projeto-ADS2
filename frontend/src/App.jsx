// =======================================================================================
// COMPONENTE PRINCIPAL - App.jsx (v0.3.0 - Contêiner)
// =======================================================================================
// ... (Comentários de cabeçalho) ...
// =======================================================================================

// Linha 17: (CORREÇÃO 1) Importa os 'Hooks' (funções especiais) do React.
import { useState, useEffect } from 'react';
// Linha 19: Importa a função de "Serviço" do ApiManager.js.
import { fetchAnalyticsData } from './services/ApiManager';
// Linha 20: Importa o componente de "Apresentação" da Tabela.
import StatTable from './components/StatTable';
// Linha 22: Importa o componente de "Apresentação" do Gráfico.
import StatDashboard from './components/StatDashboard';
// Linha 23: Importa o componente de "Apresentação" dos Filtros.
import FilterBar from './components/FilterBar';

// Linha 25: Define o componente "Contêiner".
function App() {
  // --- 1. Gerenciamento de Estado ---
  // Linha 27: Cria "memória" (estado) para os dados dos filtros (listas de heróis/ranks).
  const [dimensions, setDimensions] = useState({ hero: [], rank: [] });
  // Linha 28: Cria "memória" para os dados da tabela.
  const [tableData, setTableData] = useState([]);
  // Linha 29: Cria "memória" para os dados do gráfico.
  const [chartData, setChartData] = useState([]);
  // Linha 30: Cria "memória" para o filtro ATUAL (inicia com hero_id: 1).
  const [filters, setFilters] = useState({ hero_id: 1 });
  // Linhas 31-32: Criam "memória" para feedback de UI.
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // --- 2. Lógica de Busca de Dados ---

  // Linha 37: Efeito 1: Busca as dimensões (filtros) UMA VEZ no carregamento.
  useEffect(() => {
    // Linha 38: Define a função assíncrona que fará a busca.
    const loadDimensions = async () => {
      try {
        // Linha 40: Define a Query JSON para a tabela 'hero'.
        const heroQuery = { table_name: "hero" };
        // Linha 41: Define a Query JSON para a tabela 'rank'.
        const rankQuery = { table_name: "rank" };

        // Linha 44: (CORREÇÃO 2) Chama o ApiManager duas vezes em paralelo.
        const [heroRes, rankRes] = await Promise.all([
          fetchAnalyticsData(heroQuery),
          fetchAnalyticsData(rankQuery)
        ]);

        // Linha 50: Atualiza a "memória" (estado) com os resultados.
        setDimensions({
          hero: heroRes.data,
          rank: rankRes.data
        });
      } catch (err) {
        // Linha 56: Define o estado de erro se a busca falhar.
        setError("Falha ao carregar filtros (dimensões).");
        console.error(err);
      }
    };
    // Linha 61: Chama a função.
    loadDimensions();
  // Linha 62: O `[]` significa: "Execute este useEffect apenas UMA VEZ".
  }, []);

  // Linha 65: Efeito 2: Busca dados analíticos QUANDO OS FILTROS MUDAM.
  useEffect(() => {
    const loadAnalytics = async () => {
      // Linha 68: Proteção (não fazer nada se o filtro de herói não estiver pronto).
      if (!filters.hero_id) return;

      try {
        // Linha 72: Ativa o "Carregando..." (Feedback Visual).
        setLoading(true);
        setError(null);

        // Linha 76: Query 1 (para o Gráfico): Pede a tabela de FATO (histórica).
        const chartQuery = {
          table_name: "hero_win",
          filters_equal: { hero_id: filters.hero_id }
        };

        // Linha 84: Query 2 (para a Tabela): Pede a VIEW (dados mais recentes).
        const tableQuery = {
          table_name: "vw_hero_rank_win_latest",
          filters_equal: { hero_id: filters.hero_id }
        };

        // Linha 90: (CORREÇÃO 2) Chama o ApiManager com as duas queries.
        const [chartRes, tableRes] = await Promise.all([
          fetchAnalyticsData(chartQuery),
          fetchAnalyticsData(tableQuery)
        ]);

        // Linha 96: (CORREÇÃO 2) Atualiza a "memória" (estado) com os dados.
        setChartData(chartRes.data);
        setTableData(tableRes.data);

      } catch (err) {
        // Linha 101: Define o estado de erro.
        setError("Falha ao carregar dados analíticos.");
        console.error(err);
      } finally {
        // Linha 104: Desativa o "Carregando...".
        setLoading(false);
      }
    };

    // Linha 109: Chama a função.
    loadAnalytics();
  // Linha 110: O `[filters]` significa: "Re-execute este useEffect SEMPRE que 'filters' mudar".
  }, [filters]);

  // --- 3. Renderização (View) ---
  // Linha 113: Se houver erro, exibe a mensagem de erro.
  if (error) return <div className="text-red-500 p-4">Erro: {error}</div>;

  // Linha 116: Renderiza o layout principal.
  return (
    <div className="container mx-auto p-4">
      {/* ... Título ... */}
      
      {/* Linha 120: Renderiza o componente de Filtros. */}
      <FilterBar
        // Linha 122: Passa os dados das dimensões (do estado) como 'prop'.
        dimensions={dimensions}
        // Linha 123: Passa a *função* 'setFilters' para o filho (para "levantar o estado").
        onFilterChange={(newFilters) => setFilters(newFilters)}
      />

      {/* Linha 127: Se estiver carregando, mostra "Carregando...". */}
      {loading ? (
        <div className="text-center p-8">Carregando dados...</div>
      ) : (
        // Linha 130: Senão, mostra os dados (Divulgação Progressiva).
        <div className="mt-4">
          
          {/* Linha 133: (Hierarquia Visual) O Gráfico vem primeiro. */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-2">Análise Histórica (Gráfico)</h2>
            {/* Linha 137: Renderiza o Gráfico, passando os dados (do estado) como 'prop'. */}
            <StatDashboard data={chartData} />
          </section>

          {/* Linha 141: (Hierarquia Visual) A Tabela vem depois. */}
          <section>
            <h2 className="text-2xl font-semibold mb-2">Dados Atuais (Tabela)</h2>
            {/* Linha 145: Renderiza a Tabela, passando os dados (do estado) como 'prop'. */}
            <StatTable data={tableData} />
          </section>
        </div>
      )}
    </div>
  );
}

// Linha 153: Exporta o componente App para o main.jsx poder usá-lo.
export default App;