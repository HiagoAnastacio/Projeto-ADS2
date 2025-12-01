/**
 * AnalysisSection.jsx
 *
 * Este componente é o coração do dashboard de análise da aplicação.
 *
 * RAZÃO DE EXISTIR:
 * - Permitir que o usuário visualize e filtre os dados estatísticos de Overwatch 2.
 * - Atuar como o controlador principal que orquestra a busca de dados (via AppDataContext)
 *   baseada nos filtros selecionados pelo usuário.
 * - Exibir os resultados através de gráficos (WinRateChart, PickRateChart) e uma tabela detalhada.
 *
 * POSIÇÃO NO FLUXO DE DADOS:
 * 1. Recebe dados brutos de referência (heróis, mapas, ranks, etc.) do Contexto (AppDataContext).
 * 2. Gerencia o estado local dos filtros (hero_id, map_id, etc.) selecionados pelo usuário.
 * 3. Quando os filtros mudam, determina qual tabela do banco de dados consultar (ex: hero_win, hero_rank_map_win).
 * 4. Chama a função `fetchAnalytics` do contexto para buscar os dados filtrados do Backend.
 * 5. Processa e enriquece os dados retornados (juntando Win Rate e Pick Rate).
 * 6. Passa os dados processados para os componentes filhos (Charts e Table) para renderização.
 */

// Importa hooks do React para gerenciamento de estado e efeitos colaterais
import { useState, useEffect, useMemo } from 'react';
// Importa o hook do contexto para acessar dados globais e funções de API
import { useAppData } from '../context/AppDataContext';
// Importa componentes de UI reutilizáveis
import Dropdown from '../components/Dropdown';
import Table from '../components/Table';
// Importa componentes de visualização de dados (Gráficos)
import WinRateChart from '../components/dashboards/WinRateChart';
import PickRateChart from '../components/dashboards/PickRateChart';
// Importa ícones da biblioteca Lucide React
import { Search, Loader2 } from 'lucide-react';

// --- Hook Personalizado: useDebounce ---
// Utilizado para atrasar a atualização de um valor até que o usuário pare de digitar/interagir.
// Isso evita chamadas excessivas à API enquanto o usuário ainda está alterando filtros.
function useDebounce(value, delay) {
    // Estado local para armazenar o valor com atraso
    const [debouncedValue, setDebouncedValue] = useState(value);

    // Efeito que roda sempre que o valor ou o delay mudam
    useEffect(() => {
        // Cria um timer que atualizará o valor debounced após o tempo definido
        const handler = setTimeout(() => {
            setDebouncedValue(value);
        }, delay);

        // Função de limpeza: cancela o timer anterior se o valor mudar antes do tempo acabar
        return () => {
            clearTimeout(handler);
        };
    }, [value, delay]);

    // Retorna o valor atualizado após o delay
    return debouncedValue;
}

// --- Componente Principal: AnalysisSection ---
const AnalysisSection = () => {
    // Desestrutura os dados e funções necessários do contexto global da aplicação
    const { heroes, maps, ranks, roles, gameModes, fetchAnalytics } = useAppData();

    // --- Estado dos Filtros ---
    // Armazena os IDs selecionados para cada categoria de filtro.
    // Inicialmente todos são nulos (nenhum filtro aplicado).
    const [filters, setFilters] = useState({
        hero_id: null,
        map_id: null,
        rank_id: null,
        role_id: null,
        game_mode_id: null
    });

    // --- Estado das Labels ---
    // Armazena o texto exibido nos botões dos Dropdowns.
    // Isso melhora a UX mostrando o que está selecionado (ex: "King's Row" ao invés de "Todos os Mapas").
    const [labels, setLabels] = useState({
        hero: 'Todos os Heróis',
        map: 'Todos os Mapas',
        rank: 'Todos os Ranks',
        role: 'Todas as Funções',
        game_mode: 'Todos os Modos'
    });

    // --- Estado dos Dados ---
    // Armazena os dados processados prontos para serem exibidos na tabela
    const [tableData, setTableData] = useState([]);
    // Armazena os dados históricos para o gráfico de Win Rate
    const [chartWinData, setChartWinData] = useState([]);
    // Armazena os dados históricos para o gráfico de Pick Rate
    const [chartPickData, setChartPickData] = useState([]);
    // Controla a exibição do indicador de carregamento (spinner)
    const [loading, setLoading] = useState(false);

    // Aplica o debounce aos filtros para evitar requisições a cada clique rápido
    // O useEffect de busca dependerá desta variável, não de 'filters' diretamente
    const debouncedFilters = useDebounce(filters, 500);

    // --- Handler de Mudança de Filtro ---
    // Função genérica para atualizar o estado quando um item é selecionado em qualquer dropdown
    const handleFilterChange = (key, item, labelKey) => {
        setFilters(prev => {
            // Cria uma cópia dos filtros atuais e atualiza o filtro modificado
            const newFilters = { ...prev, [key]: item.id };
            // Atualiza também o texto do botão correspondente
            const newLabels = { ...labels, [labelKey]: item.label };

            // --- Lógica de Exclusão Mútua ---
            // Certos filtros não fazem sentido juntos ou a UI simplifica a escolha.

            // Se o usuário selecionou um Herói específico...
            if (key === 'hero_id' && item.id !== null) {
                // ...removemos o filtro de Função (Role), pois um herói já tem uma função definida.
                newFilters.role_id = null;
                newLabels.role = 'Todas as Funções';
            }
            // Se o usuário selecionou uma Função...
            if (key === 'role_id' && item.id !== null) {
                // ...removemos o filtro de Herói, para mostrar todos daquela função.
                newFilters.hero_id = null;
                newLabels.hero = 'Todos os Heróis';
            }

            // Se o usuário selecionou um Mapa...
            if (key === 'map_id' && item.id !== null) {
                // ...removemos o filtro de Modo de Jogo, pois um mapa pertence a um único modo.
                newFilters.game_mode_id = null;
                newLabels.game_mode = 'Todos os Modos';
            }
            // Se o usuário selecionou um Modo de Jogo...
            if (key === 'game_mode_id' && item.id !== null) {
                // ...removemos o filtro de Mapa, para mostrar todos os mapas daquele modo.
                newFilters.map_id = null;
                newLabels.map = 'Todos os Mapas';
            }

            // Atualiza o estado das labels visualmente
            setLabels(newLabels);
            // Retorna o novo estado dos filtros para o hook useState
            return newFilters;
        });
    };

    // --- Lógica de Seleção de Tabela Dinâmica ---
    // Determina qual tabela do banco de dados deve ser consultada com base na combinação de filtros ativos.
    // Isso é crucial para performance e para buscar os dados agregados corretos.
    const getTableNames = (f) => {
        // Define tabelas padrão (visão global por herói)
        let winTable = 'hero_win';
        let pickTable = 'hero_pick';

        // --- Prioridade 1: Combinações Específicas (Filtros Compostos) ---

        // Se filtrar por Mapa E Rank simultaneamente...
        if (f.map_id && f.rank_id) {
            // ...usa a tabela agregada por Herói + Rank + Mapa
            winTable = 'hero_rank_map_win';
            pickTable = 'hero_rank_map_pick';
        }
        // Se filtrar por Modo de Jogo E Rank simultaneamente...
        else if (f.game_mode_id && f.rank_id) {
            // ...usa a tabela agregada por Herói + Modo + Rank
            winTable = 'hero_game_mode_rank_win';
            pickTable = 'hero_game_mode_rank_pick';
        }

        // --- Prioridade 2: Filtros Únicos ---

        // Se filtrar apenas por Mapa...
        else if (f.map_id) {
            winTable = 'hero_map_win';
            pickTable = 'hero_map_pick';
        }
        // Se filtrar apenas por Modo de Jogo...
        else if (f.game_mode_id) {
            winTable = 'hero_game_mode_win';
            pickTable = 'hero_game_mode_pick';
        }
        // Se filtrar apenas por Rank...
        else if (f.rank_id) {
            winTable = 'hero_rank_win';
            pickTable = 'hero_rank_pick';
        }

        // Retorna os nomes das tabelas de Win Rate e Pick Rate a serem consultadas
        return { winTable, pickTable };
    };

    // --- Efeito Principal de Busca de Dados ---
    // Executado sempre que os filtros (debounced) ou a lista de heróis mudam.
    useEffect(() => {
        const fetchData = async () => {
            // Ativa o indicador de carregamento
            setLoading(true);
            try {
                // Desestrutura os filtros atuais
                const { hero_id, map_id, rank_id, role_id, game_mode_id } = debouncedFilters;
                // Verifica se todos os filtros estão vazios (estado inicial/padrão)
                const isDefault = !hero_id && !map_id && !rank_id && !role_id && !game_mode_id;

                let tWin = [], tPick = [];

                if (isDefault) {
                    // --- Caso Padrão (Sem Filtros) ---
                    // Busca apenas o snapshot mais recente (última data) para a tabela principal.
                    // Isso evita carregar todo o histórico desnecessariamente na visão inicial.
                    const [latestWin, latestPick] = await Promise.all([
                        fetchAnalytics({ table_name: 'vw_hero_win_latest', limit: 100 }),
                        fetchAnalytics({ table_name: 'vw_hero_pick_latest', limit: 100 })
                    ]);
                    tWin = latestWin;
                    tPick = latestPick;

                    // Para os gráficos, precisamos do histórico completo, então buscamos na tabela base 'hero_win'.
                    const [histWin, histPick] = await Promise.all([
                        fetchAnalytics({ table_name: 'hero_win', limit: 500 }),
                        fetchAnalytics({ table_name: 'hero_pick', limit: 500 })
                    ]);
                    // Atualiza os estados dos gráficos com o histórico
                    setChartWinData(histWin);
                    setChartPickData(histPick);

                } else {
                    // --- Caso com Filtros Ativos ---

                    // 1. Determina quais tabelas consultar baseada na combinação de filtros
                    const { winTable, pickTable } = getTableNames(debouncedFilters);

                    // 2. Prepara os objetos de filtro para a API
                    const filtersEqual = {}; // Filtros de igualdade exata (WHERE x = y)
                    const filtersIn = {};    // Filtros de lista (WHERE x IN (...))

                    // Adiciona os filtros de igualdade se estiverem presentes
                    if (hero_id) filtersEqual.hero_id = hero_id;
                    if (map_id) filtersEqual.map_id = map_id;
                    if (rank_id) filtersEqual.rank_id = rank_id;
                    if (game_mode_id) filtersEqual.game_mode_id = game_mode_id;

                    // Lógica especial para Filtro de Função (Role)
                    // Como as tabelas de fato geralmente não têm 'role_id' direto, filtramos os heróis.
                    if (role_id) {
                        // Encontra todos os IDs de heróis que pertencem à função selecionada
                        const heroesInRole = heroes.filter(h => h.role_id === role_id).map(h => h.hero_id);

                        if (heroesInRole.length > 0) {
                            // Adiciona um filtro IN para buscar dados apenas desses heróis
                            filtersIn.hero_id = heroesInRole;
                        } else {
                            // Se não houver heróis nesta função (erro de cadastro?), limpa dados e aborta
                            setTableData([]);
                            setLoading(false);
                            return;
                        }
                    }

                    // 3. Executa as requisições à API em paralelo
                    const [resWin, resPick] = await Promise.all([
                        fetchAnalytics({ table_name: winTable, filters_equal: filtersEqual, filters_in: filtersIn, limit: 200 }),
                        fetchAnalytics({ table_name: pickTable, filters_equal: filtersEqual, filters_in: filtersIn, limit: 200 })
                    ]);
                    tWin = resWin;
                    tPick = resPick;

                    // Atualiza os gráficos com os dados filtrados retornados
                    setChartWinData(resWin);
                    setChartPickData(resPick);
                }

                // 4. Enriquece os dados brutos para exibição na tabela (adiciona nomes, ícones, formatação)
                const enriched = enrichData(tWin, tPick);
                setTableData(enriched);

            } catch (error) {
                // Loga qualquer erro ocorrido durante o processo
                console.error("Erro ao buscar dados:", error);
            } finally {
                // Desativa o indicador de carregamento, independente de sucesso ou erro
                setLoading(false);
            }
        };

        // Chama a função de busca
        fetchData();
    }, [debouncedFilters, heroes]); // Re-executa se os filtros ou a lista de heróis mudar

    // --- Helper: Enriquecer Dados ---
    // Combina os dados de Win Rate e Pick Rate e adiciona metadados (nomes, imagens)
    const enrichData = (winData, pickData) => {
        if (!winData) return [];

        // Cria um mapa para acesso rápido ao Pick Rate usando uma chave composta (HeroID + Data)
        const pickMap = new Map();
        if (pickData) {
            pickData.forEach(p => {
                const key = `${p.hero_id}-${p.date_of_the_data}`;
                pickMap.set(key, p.pick_rate);
            });
        }

        // Mapeia cada registro de Win Rate para um objeto completo para a tabela
        return winData.map(item => {
            // Busca os objetos completos de referência baseados nos IDs
            const hero = heroes.find(h => h.hero_id === item.hero_id);
            const map = maps.find(m => m.map_id === item.map_id);
            const rank = ranks.find(r => r.rank_id === item.rank_id);
            const mode = gameModes.find(g => g.game_mode_id === item.game_mode_id);

            // Formata a data para o padrão brasileiro
            const dateObj = new Date(item.date_of_the_data);
            const formattedDate = dateObj.toLocaleDateString('pt-BR');

            // Retorna o objeto formatado para o componente Table
            return {
                'Ícone': hero ? hero.hero_icon_img_link : null,
                'Herói': hero ? hero.hero_name : `ID ${item.hero_id}`,
                'Win Rate (%)': item.win_rate,
                // Busca o Pick Rate correspondente no mapa, ou usa '-' se não encontrar
                'Pick Rate (%)': pickMap.get(`${item.hero_id}-${item.date_of_the_data}`) || item.pick_rate || '-',
                'Data': formattedDate,
                // Adiciona colunas condicionais apenas se o dado existir (para não mostrar colunas vazias)
                ...(map && { 'Mapa': map.map_name }),
                ...(rank && { 'Rank': rank.rank_name }),
                ...(mode && { 'Modo': mode.game_mode_name }),
            };
        });
    };

    // --- Preparação dos Itens dos Dropdowns (Memoized) ---
    // Cria as listas de opções para os dropdowns, adicionando a opção "Todos" no início.
    // Usa useMemo para evitar recriação desnecessária a cada renderização.

    const heroItems = useMemo(() =>
        [{ label: 'Todos os Heróis', id: null }, ...heroes.map(h => ({ label: h.hero_name, id: h.hero_id }))]
            .map(i => ({ ...i, action: () => handleFilterChange('hero_id', i, 'hero') })),
        [heroes, labels]);

    const mapItems = useMemo(() =>
        [{ label: 'Todos os Mapas', id: null }, ...maps.map(m => ({ label: m.map_name, id: m.map_id }))]
            .map(i => ({ ...i, action: () => handleFilterChange('map_id', i, 'map') })),
        [maps, labels]);

    const rankItems = useMemo(() =>
        [{ label: 'Todos os Ranks', id: null }, ...ranks.map(r => ({ label: r.rank_name || r.rank || r.name || 'Rank', id: r.rank_id }))]
            .map(i => ({ ...i, action: () => handleFilterChange('rank_id', i, 'rank') })),
        [ranks, labels]);

    const roleItems = useMemo(() =>
        [{ label: 'Todas as Funções', id: null }, ...roles.map(r => ({ label: r.role_name || r.role || r.name || 'Role', id: r.role_id }))]
            .map(i => ({ ...i, action: () => handleFilterChange('role_id', i, 'role') })),
        [roles, labels]);

    const modeItems = useMemo(() =>
        [{ label: 'Todos os Modos', id: null }, ...gameModes.map(g => ({ label: g.game_mode_name || g.mode_name || g.name || 'Modo', id: g.game_mode_id }))]
            .map(i => ({ ...i, action: () => handleFilterChange('game_mode_id', i, 'game_mode') })),
        [gameModes, labels]);

    // --- Renderização do Componente ---
    return (
        <section id="analysis-section" className="w-full min-h-screen bg-white py-20 px-6 relative">
            <div className="max-w-7xl mx-auto">

                {/* --- Barra de Filtros (Estilo Natural Language Form) --- */}
                <div className="sticky top-24 z-40 flex justify-center mb-16">
                    <div className="bg-white/90 backdrop-blur-xl border border-gray-200 shadow-xl rounded-full px-8 py-4 flex flex-col md:flex-row items-center gap-3 md:gap-2 text-lg md:text-xl text-slate-500 transition-all hover:shadow-2xl hover:border-emerald-200/50 flex-wrap justify-center">
                        {/* Ícone de Lupa decorativo */}
                        <Search className="w-5 h-5 text-emerald-500 mr-2 hidden md:block" />

                        <span className="whitespace-nowrap">Analisar</span>

                        {/* --- Dropdown: Herói ou Função --- */}
                        {/* Exibe Dropdown de Heróis apenas se Função NÃO estiver selecionada */}
                        {filters.role_id === null && (
                            <div className="relative group">
                                <Dropdown label={labels.hero} items={heroItems} variant="text" className="min-w-[150px] text-center md:text-left" />
                            </div>
                        )}

                        {/* Exibe Dropdown de Funções apenas se Herói NÃO estiver selecionado */}
                        {filters.hero_id === null && (
                            <>
                                {/* Conectivo "ou" se nenhum dos dois estiver selecionado ainda */}
                                {filters.role_id === null && <span className="text-sm text-gray-300 mx-1">ou</span>}
                                <div className="relative group">
                                    <Dropdown label={labels.role} items={roleItems} variant="text" className="min-w-[150px] text-center md:text-left" />
                                </div>
                            </>
                        )}

                        {/* Conectivo Dinâmico: muda o texto baseado no próximo filtro */}
                        <span className="whitespace-nowrap">
                            {filters.game_mode_id ? 'no modo' : 'em'}
                        </span>

                        {/* --- Dropdown: Mapa ou Modo de Jogo --- */}
                        {/* Exibe Dropdown de Mapas apenas se Modo NÃO estiver selecionado */}
                        {filters.game_mode_id === null && (
                            <div className="relative group">
                                <Dropdown label={labels.map} items={mapItems} variant="text" className="min-w-[150px] text-center md:text-left" />
                            </div>
                        )}

                        {/* Exibe Dropdown de Modos apenas se Mapa NÃO estiver selecionado */}
                        {filters.map_id === null && (
                            <>
                                {filters.game_mode_id === null && <span className="text-sm text-gray-300 mx-1">ou</span>}
                                <div className="relative group">
                                    <Dropdown label={labels.game_mode} items={modeItems} variant="text" className="min-w-[150px] text-center md:text-left" />
                                </div>
                            </>
                        )}

                        <span className="whitespace-nowrap hidden md:inline">no rank</span>
                        <span className="whitespace-nowrap md:hidden">rank</span>

                        {/* --- Dropdown: Rank --- */}
                        <div className="relative group">
                            <Dropdown label={labels.rank} items={rankItems} variant="text" className="min-w-[120px] text-center md:text-left" />
                        </div>
                    </div>
                </div>

                {/* --- Área de Gráficos --- */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
                    {/* Card do Gráfico de Win Rate */}
                    <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
                        <h3 className="text-lg font-bold text-slate-800 mb-4">Tendência de Win Rate</h3>
                        <div className="h-[40vh] min-h-[350px] w-full">
                            <WinRateChart data={chartWinData} heroes={heroes} />
                        </div>
                    </div>
                    {/* Card do Gráfico de Pick Rate */}
                    <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
                        <h3 className="text-lg font-bold text-slate-800 mb-4">Tendência de Pick Rate</h3>
                        <div className="h-[40vh] min-h-[350px] w-full">
                            <PickRateChart data={chartPickData} heroes={heroes} />
                        </div>
                    </div>
                </div>

                {/* --- Área da Tabela de Dados --- */}
                {/* Container com transição de opacidade para efeito de carregamento suave */}
                <div className={`transition-opacity duration-500 ${loading ? 'opacity-50 pointer-events-none' : 'opacity-100'}`}>
                    {/* Overlay de Loading (Spinner) */}
                    {loading && (
                        <div className="absolute inset-0 flex items-start justify-center pt-60 z-50">
                            <div className="bg-white px-6 py-3 rounded-full shadow-lg border border-gray-100 flex items-center gap-3">
                                <Loader2 className="animate-spin text-emerald-600" />
                                <span className="text-slate-600 font-medium">Atualizando dados...</span>
                            </div>
                        </div>
                    )}

                    {/* Componente de Tabela Genérico */}
                    <Table data={tableData} />
                </div>

            </div>
        </section>
    );
};

// Exporta o componente para ser usado na App.jsx
export default AnalysisSection;
