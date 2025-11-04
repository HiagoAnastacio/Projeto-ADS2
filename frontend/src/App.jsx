// =======================================================================================
// COMPONENTE PRINCIPAL - App.jsx (v0.2.0 - Interativo)
// =======================================================================================
// FLUXO E A LÓGICA:
// 1. Usa o Hook 'useState' para criar "estados" (memória do componente) para:
//    - 'dimensions': Armazenar os dados dos filtros (listas de ranks, modos de jogo).
//    - 'heroStats': Armazenar os dados que serão exibidos na tabela.
//    - 'filter': Armazenar a seleção atual dos dropdowns.
//    - 'loading' / 'error': Controlar a UI durante as requisições.
// 2. Usa o Hook 'useEffect' com dependência vazia '[]' para rodar UMA VEZ no carregamento:
//    - Busca as dimensões (heróis, roles, ranks, game modes).
//    - Busca os dados GERAIS (getLatestGeneralStats).
//    - Popula os estados 'dimensions' e 'heroStats'.
// 3. Usa um SEGUNDO 'useEffect' que "escuta" mudanças no estado 'filter'.
//    - Quando 'filter' muda (usuário escolhe um rank), este efeito é disparado.
//    - Ele chama a função de API apropriada (ex: getLatestRankStats).
//    - Ele recombina os dados e atualiza 'heroStats', fazendo a tabela recarregar.
// 4. Renderiza os dropdowns e a tabela com base nos estados atuais.
//
// RAZÃO DE EXISTIR: Ser o componente raiz que age como o "Analyzer",
// gerenciando os filtros, as chamadas de API dinâmicas e a exibição dos dados.
// =======================================================================================

// Linha 24: Importa os Hooks 'useState' (para estado) e 'useEffect' (para carregar dados) do React.
import { useState, useEffect } from 'react';
// Linha 26: Importa TODAS as funções que precisamos do nosso gerenciador de API.
import {
  getHeroes,
  getRoles,
  getRanks,
  getGameModes,
  getLatestGeneralStats,
  getLatestRankStats,
  getLatestGameModeStats
} from './services/api_manager';

// Linha 37: Função auxiliar (helper) para formatar os números de rate (ex: 47.6 -> "47.60").
const formatRate = (rate) => {
  // Linha 39: Verifica se 'rate' é um número válido.
  if (typeof rate === 'number' && !isNaN(rate)) {
    // Linha 41: Retorna o número formatado com 2 casas decimais (sem multiplicar por 100).
    return rate.toFixed(2);
  }
  // Linha 44: Se não for um número (ex: "N/A"), retorna o valor como está.
  return rate;
};

// Linha 48: Definição do componente principal da aplicação.
function App() {
  // --- DEFINIÇÃO DOS ESTADOS ---

  // Linha 52: Estado para armazenar os dados das dimensões (listas para os filtros).
  const [dimensions, setDimensions] = useState({
    heroes: [], // Lista de todos os heróis (base para combinar)
    roles: new Map(), // Mapa de role_id -> role_name
    ranks: [], // Lista de ranks para o dropdown
    gameModes: [], // Lista de modos de jogo para o dropdown
  });

  // Linha 60: Estado para os dados combinados que vão para a tabela.
  const [heroStats, setHeroStats] = useState([]);
  
  // Linha 63: Estado para a seleção ATUAL dos filtros.
  const [filter, setFilter] = useState({ type: 'all', id: null }); // 'all', 'rank', ou 'gamemode'
  
  // Linha 66: Estado para controlar a exibição de "Carregando...".
  const [loading, setLoading] = useState(true);
  // Linha 68: Estado para armazenar mensagens de erro.
  const [error, setError] = useState(null);

  // --- FUNÇÃO AUXILIAR DE COMBINAÇÃO DE DADOS ---
  /**
   * Combina a lista base de heróis com as listas de estatísticas (win/pick).
   * @param {Array} baseHeroes - A lista de heróis de dimensions.heroes.
   * @param {Array} winList - A lista de win rates (vinda de qualquer view _latest).
   * @param {Array} pickList - A lista de pick rates (vinda de qualquer view _latest).
   * @param {Map} roleMap - O mapa de dimensions.roles.
   * @param {String} contextKey - A chave de dimensão para filtrar (ex: 'rank_id', 'game_mode_id').
   * @param {Number} contextId - O ID do filtro selecionado (ex: 3 para Gold).
   */
  const combineStats = (baseHeroes, winList, pickList, roleMap, contextKey = null, contextId = null) => {
    // Linha 84: Filtra as listas de stats ANTES de criar os mapas, se um contexto foi dado.
    //         Isso garante que a tabela só mostre dados para o rank/modo selecionado.
    const filteredWins = contextId ? winList.filter(item => item[contextKey] === contextId) : winList;
    const filteredPicks = contextId ? pickList.filter(item => item[contextKey] === contextId) : pickList;

    // Linha 89: Cria Mapas (hero_id -> metric) para busca rápida.
    const winRateMap = new Map(filteredWins.map(item => [item.hero_id, item.win_rate]));
    const pickRateMap = new Map(filteredPicks.map(item => [item.hero_id, item.pick_rate]));

    // Linha 93: Mapeia a lista de heróis base.
    const combined = baseHeroes.map(hero => ({
      // Linha 95: Copia as propriedades base (hero_id, hero_name, role_id).
      ...hero,
      // Linha 97: Busca a win rate no mapa; se não achar, usa 'N/A'.
      win_rate: winRateMap.get(hero.hero_id) ?? 'N/A',
      // Linha 99: Busca a pick rate no mapa; se não achar, usa 'N/A'.
      pick_rate: pickRateMap.get(hero.hero_id) ?? 'N/A',
      // Linha 101: Busca o nome da role no mapa de roles.
      role_name: roleMap.get(hero.role_id) ?? hero.role_id
    }));
    
    // Linha 105: Retorna os dados combinados e filtrados.
    return combined;
  };

  // --- EFEITOS DE BUSCA DE DADOS ---

  // Linha 111: Efeito 1: Roda UMA VEZ no carregamento inicial da página (note o `[]` vazio).
  useEffect(() => {
    // Linha 113: Define a função assíncrona que busca os dados iniciais.
    async function loadInitialData() {
      // Linha 115: Tenta buscar todos os dados essenciais em paralelo.
      try {
        // Linha 117: Define o estado de carregamento.
        setLoading(true);
        // Linha 119: Limpa erros anteriores.
        setError(null);

        // Linha 122: Chama 4 conjuntos de dados em paralelo para velocidade.
        const [
          heroesResponse,
          rolesResponse,
          ranksResponse,
          gameModesResponse,
          generalStatsResponse // [winRates, pickRates]
        ] = await Promise.all([
          getHeroes(), // Para a lista de heróis
          getRoles(), // Para mapear ID -> Nome da Role
          getRanks(), // Para popular o filtro de Rank
          getGameModes(), // Para popular o filtro de Modo de Jogo
          getLatestGeneralStats() // Para os dados da tabela inicial
        ]);

        // Linha 135: Extrai os dados das respostas.
        const heroesList = heroesResponse.data;
        const rolesList = rolesResponse.data;
        const ranksList = ranksResponse.data;
        const gameModesList = gameModesResponse.data;
        const [generalWinList, generalPickList] = [generalStatsResponse[0].data, generalStatsResponse[1].data];

        // Linha 142: Cria o mapa de Role ID -> Nome.
        const newRoleMap = new Map(rolesList.map(item => [item.role_id, item.role]));

        // Linha 145: Armazena os dados das dimensões (filtros) no estado 'dimensions'.
        setDimensions({
          heroes: heroesList,
          roles: newRoleMap,
          ranks: ranksList,
          gameModes: gameModesList,
        });

        // Linha 153: Combina os dados GERAIS para a exibição inicial.
        const combinedGeneralStats = combineStats(heroesList, generalWinList, generalPickList, newRoleMap, null, null);
        
        // Linha 156: Atualiza o estado da tabela, causando a renderização.
        setHeroStats(combinedGeneralStats);

      } catch (err) {
        // Linha 160: Bloco 'catch' para tratar erros na busca inicial.
        console.error("Erro ao carregar dados iniciais:", err);
        setError("Falha ao carregar dados essenciais. Verifique a API e recarregue a página.");
      } finally {
        // Linha 164: Bloco 'finally' garante que o loading termine, mesmo se der erro.
        setLoading(false);
      }
    }

    // Linha 169: Chama a função de carregamento inicial.
    loadInitialData();
  }, []); // Linha 171: O `[]` vazio garante que este efeito rode apenas UMA VEZ.

  
  // Linha 174: Efeito 2: Roda TODA VEZ que o estado 'filter' mudar.
  useEffect(() => {
    // Linha 176: Define a função assíncrona que busca dados filtrados.
    async function fetchFilteredData() {
      // Linha 178: Se o filtro for 'all', já temos os dados (do efeito inicial), então não faz nada.
      // (Poderíamos recarregar, mas vamos otimizar por enquanto).
      if (filter.type === 'all') {
        // Se quiséssemos recarregar os dados gerais:
        // setLoading(true);
        // const [win, pick] = await getLatestGeneralStats();
        // const combined = combineStats(dimensions.heroes, win.data, pick.data, dimensions.roles, null, null);
        // setHeroStats(combined);
        // setLoading(false);
        return; // Sai da função
      }

      // Linha 191: Se o filtro NÃO for 'all', busca os dados específicos.
      setLoading(true);
      setError(null);

      try {
        // Linha 196: Variáveis para guardar os dados buscados.
        let winList, pickList, contextKey;

        // Linha 199: Verifica o TIPO de filtro selecionado.
        if (filter.type === 'rank') {
          // Linha 201: Se for 'rank', chama a API de stats por rank.
          const [rankWinResponse, rankPickResponse] = await getLatestRankStats();
          // Linha 203: Armazena os resultados.
          winList = rankWinResponse.data;
          pickList = rankPickResponse.data;
          // Linha 206: Define a chave de contexto para a função 'combineStats'.
          contextKey = 'rank_id';
        } else if (filter.type === 'gamemode') {
          // Linha 209: Se for 'gamemode', chama a API de stats por modo de jogo.
          const [gmWinResponse, gmPickResponse] = await getLatestGameModeStats();
          // Linha 211: Armazena os resultados.
          winList = gmWinResponse.data;
          pickList = gmPickResponse.data;
          // Linha 214: Define a chave de contexto.
          contextKey = 'game_mode_id';
        } else {
          // Linha 217: Se o tipo de filtro for desconhecido, não faz nada.
          setLoading(false);
          return;
        }

        // Linha 222: Chama a função de combinação, passando os dados buscados e o filtro.
        const combinedFilteredStats = combineStats(
          dimensions.heroes, // A lista base de heróis (já em estado)
          winList,           // A lista de win rates (ex: por rank)
          pickList,          // A lista de pick rates (ex: por rank)
          dimensions.roles,  // O mapa de roles (já em estado)
          contextKey,        // A chave 'rank_id' ou 'game_mode_id'
          filter.id          // O ID selecionado (ex: 3 para Gold)
        );

        // Linha 232: Atualiza o estado da tabela com os novos dados filtrados.
        setHeroStats(combinedFilteredStats);

      } catch (err) {
        // Linha 236: Trata erros na busca filtrada.
        console.error("Erro ao buscar dados filtrados:", err);
        setError("Falha ao carregar dados filtrados.");
      } finally {
        // Linha 240: Termina o carregamento.
        setLoading(false);
      }
    }

    // Linha 245: Chama a função de busca filtrada.
    fetchFilteredData();
  // Linha 247: O array [filter] diz ao React: "Execute este efeito novamente se a variável 'filter' mudar".
  }, [filter, dimensions.heroes, dimensions.roles]); // Adiciona 'dimensions' como dependência


  // --- HANDLERS (Funções chamadas por eventos do usuário) ---

  // Linha 253: Chamada quando o dropdown de Rank muda.
  const handleRankChange = (event) => {
    // Linha 255: Pega o valor selecionado (que será o 'rank_id' como string).
    const selectedRankId = event.target.value;
    
    // Linha 258: Se o usuário selecionar "Todos os Ranks" (valor 'all')...
    if (selectedRankId === 'all') {
      // Linha 260: Reseta o filtro para 'all' e busca os dados gerais.
      setFilter({ type: 'all', id: null });
    } else {
      // Linha 263: Se selecionar um rank específico...
      // Linha 264: Atualiza o estado 'filter' para tipo 'rank' e o ID (convertido para número).
      setFilter({ type: 'rank', id: parseInt(selectedRankId, 10) });
    }
    // Linha 267: (Não precisamos mais disso, pois o useEffect [filter] cuidará da busca)
  };

  // Linha 270: Chamada quando o dropdown de Modo de Jogo muda (lógica idêntica ao Rank).
  const handleGameModeChange = (event) => {
    // Linha 272: Pega o 'game_mode_id' como string.
    const selectedGameModeId = event.target.value;
    
    // Linha 275: Se selecionar "Todos os Modos"...
    if (selectedGameModeId === 'all') {
      // Linha 277: Reseta o filtro para 'all'.
      setFilter({ type: 'all', id: null });
    } else {
      // Linha 280: Atualiza o filtro para 'gamemode' e o ID (convertido para número).
      setFilter({ type: 'gamemode', id: parseInt(selectedGameModeId, 10) });
    }
  };


  // --- RENDERIZAÇÃO ---

  // Linha 288: Renderização condicional para o estado de carregamento inicial.
  if (loading && dimensions.heroes.length === 0) {
    // Linha 290: Mostra um loading mais genérico na primeira carga.
    return <div className="text-center text-xl p-10">Carregando aplicação...</div>;
  }

  // Linha 294: Renderização condicional para erro inicial.
  if (error && dimensions.heroes.length === 0) {
    // Linha 296: Mostra o erro fatal que impediu o carregamento das dimensões.
    return <div className="text-center text-xl p-10 text-red-500 bg-red-100 border border-red-400 rounded">{error}</div>;
  }

  // Linha 300: Renderização principal da aplicação.
  return (
    // Linha 302: Container principal com classes Tailwind.
    <div className="container mx-auto p-4">
      {/* Linha 304: Título da página. */}
      <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">Overwatch Meta Analyzer</h1>

      {/* Linha 307: Seção de Filtros (Dropdowns). */}
      <div className="flex flex-col md:flex-row justify-center gap-4 mb-6">
        {/* Linha 309: Dropdown de Ranks. */}
        <div>
          {/* Linha 311: Rótulo do filtro. */}
          <label htmlFor="rank-select" className="block text-sm font-medium text-gray-700 mb-1">
            Filtrar por Rank
          </label>
          {/* Linha 315: O elemento <select> (dropdown). */}
          <select
            id="rank-select"
            // Linha 318: O 'onChange' chama nossa função 'handleRankChange' quando o usuário escolhe.
            onChange={handleRankChange}
            // Linha 320: Desabilita o dropdown se o outro filtro estiver ativo ou se estiver carregando.
            disabled={loading || filter.type === 'gamemode'}
            // Linha 322: Classes de estilo do Tailwind.
            className="mt-1 block w-full md:w-64 py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm disabled:bg-gray-200"
          >
            {/* Linha 226: Opção padrão "Todos". */}
            <option value="all">Todos os Ranks</option>
            {/* Linha 328: Itera sobre a lista 'dimensions.ranks' (do estado) para criar as <option>. */}
            {dimensions.ranks.map((rank) => (
              // Linha 330: 'key' é o 'rank_id', 'value' é o 'rank_id'.
              <option key={rank.rank_id} value={rank.rank_id}>
                {rank.rank_name} {/* O texto que o usuário vê. */}
              </option>
            ))}
          </select>
        </div>

        {/* Linha 338: Dropdown de Modo de Jogo (lógica idêntica ao de Rank). */}
        <div>
          {/* Linha 340: Rótulo. */}
          <label htmlFor="gamemode-select" className="block text-sm font-medium text-gray-700 mb-1">
            Filtrar por Modo de Jogo
          </label>
          {/* Linha 344: O elemento <select>. */}
          <select
            id="gamemode-select"
            // Linha 347: Chama 'handleGameModeChange' ao mudar.
            onChange={handleGameModeChange}
            // Linha 349: Desabilita se o filtro de rank estiver ativo ou se estiver carregando.
            disabled={loading || filter.type === 'rank'}
            // Linha 351: Classes de estilo.
            className="mt-1 block w-full md:w-64 py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm disabled:bg-gray-200"
          >
            {/* Linha 354: Opção padrão "Todos". */}
            <option value="all">Todos os Modos de Jogo</option>
            {/* Linha 356: Itera sobre 'dimensions.gameModes' (do estado). */}
            {dimensions.gameModes.map((mode) => (
              // Linha 358: 'key' e 'value' são o 'game_mode_id'.
              <option key={mode.game_mode_id} value={mode.game_mode_id}>
                {mode.game_mode_name} {/* O texto que o usuário vê. */}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Linha 367: Divisor para a tabela. */}
      <div className="overflow-x-auto shadow-md rounded-lg">
        {/* Linha 369: Overlay de Carregamento. */}
        {/* Mostra uma sobreposição semi-transparente sobre a tabela quando 'loading' é true. */}
        {loading && (
          <div className="absolute inset-0 bg-white bg-opacity-50 flex items-center justify-center z-10">
            <div className="text-xl">Atualizando dados...</div>
          </div>
        )}
        
        {/* Linha 377: Tabela de dados. */}
        <table className="min-w-full bg-white border border-gray-300">
          {/* Linha 379: Cabeçalho da tabela. */}
          <thead>
            <tr className="bg-gray-800 text-white uppercase text-sm leading-normal">
              <th className="py-3 px-4 text-left">Herói</th>
              <th className="py-3 px-4 text-center">Win Rate (%)</th>
              <th className="py-3 px-4 text-center">Pick Rate (%)</th>
              <th className="py-3 px-4 text-center">Role</th>
            </tr>
          </thead>
          {/* Linha 387: Corpo da tabela. */}
          <tbody className="text-gray-700 text-sm font-light">
            {/* Linha 389: Itera sobre o estado 'heroStats' (que agora está filtrado). */}
            {heroStats.map((hero, index) => (
              // Linha 391: Linha da tabela ('tr').
              <tr
                key={hero.hero_id} // Key única obrigatória.
                // Linha 394: Classes Tailwind para zebrar a tabela (alterna cor de fundo).
                className={`border-b border-gray-200 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'} hover:bg-blue-100`}
              >
                {/* Linha 397: Célula (td) para o nome do herói. */}
                <td className="py-3 px-4 text-left whitespace-nowrap font-medium">{hero.hero_name}</td>
                {/* Linha 399: Célula (td) para Win Rate, usando a função de formatação. */}
                <td className="py-3 px-4 text-center">{formatRate(hero.win_rate)}</td>
                {/* Linha 401: Célula (td) para Pick Rate, usando a função de formatação. */}
                <td className="py-3 px-4 text-center">{formatRate(hero.pick_rate)}</td>
                {/* Linha 403: Célula (td) para o nome da Role (mapeado). */}
                <td className="py-3 px-4 text-center">{hero.role_name}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {/* Linha 409: Tratamento para tabela vazia. */}
        {/* Se 'heroStats' estiver vazio (e não estiver carregando), mostra uma mensagem. */}
        {!loading && heroStats.length === 0 && (
          <div className="text-center p-6 text-gray-500">
            Nenhum dado encontrado para os filtros selecionados.
          </div>
        )}
      </div>
    </div>
  );
}

// Linha 422: Exporta o componente App para ser usado pelo 'main.jsx'.
export default App;