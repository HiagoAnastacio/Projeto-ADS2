import { useState, useEffect, useMemo } from 'react';
import { useAppData } from '../context/AppDataContext';
import Dropdown from '../components/Dropdown';
import Table from '../components/Table';
import WinRateChart from '../components/dashboards/WinRateChart';
import PickRateChart from '../components/dashboards/PickRateChart';
import { Search, Loader2 } from 'lucide-react';

// Hook de Debounce personalizado
function useDebounce(value, delay) {
    const [debouncedValue, setDebouncedValue] = useState(value);
    useEffect(() => {
        const handler = setTimeout(() => {
            setDebouncedValue(value);
        }, delay);
        return () => {
            clearTimeout(handler);
        };
    }, [value, delay]);
    return debouncedValue;
}

const AnalysisSection = () => {
    const { heroes, maps, ranks, roles, gameModes, fetchAnalytics } = useAppData();

    // --- Estado dos Filtros ---
    const [filters, setFilters] = useState({
        hero_id: null,
        map_id: null,
        rank_id: null,
        role_id: null,
        game_mode_id: null
    });

    // Estado das Labels para os Dropdowns
    const [labels, setLabels] = useState({
        hero: 'Todos os Heróis',
        map: 'Todos os Mapas',
        rank: 'Todos os Ranks',
        role: 'Todas as Funções',
        game_mode: 'Todos os Modos'
    });

    // --- Estado dos Dados ---
    const [tableData, setTableData] = useState([]);
    const [chartWinData, setChartWinData] = useState([]);
    const [chartPickData, setChartPickData] = useState([]);
    const [loading, setLoading] = useState(false);

    // Debounce dos filtros
    const debouncedFilters = useDebounce(filters, 500);

    // --- Handlers ---
    const handleFilterChange = (key, item, labelKey) => {
        setFilters(prev => {
            const newFilters = { ...prev, [key]: item.id };
            const newLabels = { ...labels, [labelKey]: item.label };

            // Exclusão Mútua: Herói vs Função
            if (key === 'hero_id' && item.id !== null) {
                newFilters.role_id = null;
                newLabels.role = 'Todas as Funções';
            }
            if (key === 'role_id' && item.id !== null) {
                newFilters.hero_id = null;
                newLabels.hero = 'Todos os Heróis';
            }

            // Exclusão Mútua: Mapa vs Modo
            if (key === 'map_id' && item.id !== null) {
                newFilters.game_mode_id = null;
                newLabels.game_mode = 'Todos os Modos';
            }
            if (key === 'game_mode_id' && item.id !== null) {
                newFilters.map_id = null;
                newLabels.map = 'Todos os Mapas';
            }

            setLabels(newLabels);
            return newFilters;
        });
    };

    // --- Lógica de Seleção de Tabela Dinâmica ---
    const getTableNames = (f) => {
        let winTable = 'hero_win';
        let pickTable = 'hero_pick';

        // Combinações com Rank (Prioridade Alta)
        if (f.map_id && f.rank_id) {
            winTable = 'hero_rank_map_win';
            pickTable = 'hero_rank_map_pick';
        } else if (f.game_mode_id && f.rank_id) {
            winTable = 'hero_game_mode_rank_win';
            pickTable = 'hero_game_mode_rank_pick';
        }
        // Filtros Únicos
        else if (f.map_id) {
            winTable = 'hero_map_win';
            pickTable = 'hero_map_pick';
        } else if (f.game_mode_id) {
            winTable = 'hero_game_mode_win';
            pickTable = 'hero_game_mode_pick';
        } else if (f.rank_id) {
            winTable = 'hero_rank_win';
            pickTable = 'hero_rank_pick';
        }

        return { winTable, pickTable };
    };

    // --- Lógica de Busca (Effect) ---
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const { hero_id, map_id, rank_id, role_id, game_mode_id } = debouncedFilters;
                const isDefault = !hero_id && !map_id && !rank_id && !role_id && !game_mode_id;

                let tWin = [], tPick = [];

                if (isDefault) {
                    // Busca snapshot mais recente para a tabela
                    const [latestWin, latestPick] = await Promise.all([
                        fetchAnalytics({ table_name: 'vw_hero_win_latest', limit: 100 }),
                        fetchAnalytics({ table_name: 'vw_hero_pick_latest', limit: 100 })
                    ]);
                    tWin = latestWin;
                    tPick = latestPick;

                    // Para gráficos, buscamos histórico (hero_win)
                    const [histWin, histPick] = await Promise.all([
                        fetchAnalytics({ table_name: 'hero_win', limit: 500 }),
                        fetchAnalytics({ table_name: 'hero_pick', limit: 500 })
                    ]);
                    setChartWinData(histWin);
                    setChartPickData(histPick);

                } else {
                    // 1. Determina quais tabelas consultar
                    const { winTable, pickTable } = getTableNames(debouncedFilters);

                    // 2. Monta os filtros
                    const filtersEqual = {};
                    const filtersIn = {};

                    if (hero_id) filtersEqual.hero_id = hero_id;
                    if (map_id) filtersEqual.map_id = map_id;
                    if (rank_id) filtersEqual.rank_id = rank_id;
                    if (game_mode_id) filtersEqual.game_mode_id = game_mode_id;

                    // Lógica de Role (Filtro IN)
                    if (role_id) {
                        // Encontra todos os heróis com essa role_id
                        const heroesInRole = heroes.filter(h => h.role_id === role_id).map(h => h.hero_id);
                        if (heroesInRole.length > 0) {
                            filtersIn.hero_id = heroesInRole;
                        } else {
                            // Se não tem heróis nessa role, retorna vazio e aborta
                            setTableData([]);
                            setLoading(false);
                            return;
                        }
                    }

                    // 3. Busca os dados
                    const [resWin, resPick] = await Promise.all([
                        fetchAnalytics({ table_name: winTable, filters_equal: filtersEqual, filters_in: filtersIn, limit: 200 }),
                        fetchAnalytics({ table_name: pickTable, filters_equal: filtersEqual, filters_in: filtersIn, limit: 200 })
                    ]);
                    tWin = resWin;
                    tPick = resPick;

                    // Atualiza gráficos com os mesmos dados filtrados
                    setChartWinData(resWin);
                    setChartPickData(resPick);
                }

                // 4. Enriquece e formata para a tabela
                const enriched = enrichData(tWin, tPick);
                setTableData(enriched);

            } catch (error) {
                console.error("Erro ao buscar dados:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [debouncedFilters, heroes]);

    // --- Helper: Enriquecer Dados ---
    const enrichData = (winData, pickData) => {
        if (!winData) return [];

        const pickMap = new Map();
        if (pickData) {
            pickData.forEach(p => {
                const key = `${p.hero_id}-${p.date_of_the_data}`;
                pickMap.set(key, p.pick_rate);
            });
        }

        return winData.map(item => {
            const hero = heroes.find(h => h.hero_id === item.hero_id);
            const map = maps.find(m => m.map_id === item.map_id);
            const rank = ranks.find(r => r.rank_id === item.rank_id);
            const mode = gameModes.find(g => g.game_mode_id === item.game_mode_id);

            const dateObj = new Date(item.date_of_the_data);
            const formattedDate = dateObj.toLocaleDateString('pt-BR');

            return {
                'Ícone': hero ? hero.hero_icon_img_link : null,
                'Herói': hero ? hero.hero_name : `ID ${item.hero_id}`,
                'Win Rate (%)': item.win_rate,
                'Pick Rate (%)': pickMap.get(`${item.hero_id}-${item.date_of_the_data}`) || item.pick_rate || '-',
                'Data': formattedDate,
                ...(map && { 'Mapa': map.map_name }),
                ...(rank && { 'Rank': rank.rank_name }),
                ...(mode && { 'Modo': mode.game_mode_name }),
            };
        });
    };

    // --- Preparação dos Itens (Memoized) ---
    // Adicionado labels e handleFilterChange às dependências para evitar stale closures
    const heroItems = useMemo(() => [{ label: 'Todos os Heróis', id: null }, ...heroes.map(h => ({ label: h.hero_name, id: h.hero_id }))].map(i => ({ ...i, action: () => handleFilterChange('hero_id', i, 'hero') })), [heroes, labels]);
    const mapItems = useMemo(() => [{ label: 'Todos os Mapas', id: null }, ...maps.map(m => ({ label: m.map_name, id: m.map_id }))].map(i => ({ ...i, action: () => handleFilterChange('map_id', i, 'map') })), [maps, labels]);
    const rankItems = useMemo(() => [{ label: 'Todos os Ranks', id: null }, ...ranks.map(r => ({ label: r.rank_name || r.rank || r.name || 'Rank', id: r.rank_id }))].map(i => ({ ...i, action: () => handleFilterChange('rank_id', i, 'rank') })), [ranks, labels]);
    const roleItems = useMemo(() => [{ label: 'Todas as Funções', id: null }, ...roles.map(r => ({ label: r.role_name || r.role || r.name || 'Role', id: r.role_id }))].map(i => ({ ...i, action: () => handleFilterChange('role_id', i, 'role') })), [roles, labels]);
    const modeItems = useMemo(() => [{ label: 'Todos os Modos', id: null }, ...gameModes.map(g => ({ label: g.game_mode_name || g.mode_name || g.name || 'Modo', id: g.game_mode_id }))].map(i => ({ ...i, action: () => handleFilterChange('game_mode_id', i, 'game_mode') })), [gameModes, labels]);

    return (
        <section id="analysis-section" className="w-full min-h-screen bg-white py-20 px-6 relative">
            <div className="max-w-7xl mx-auto">

                {/* Barra de Consulta Flutuante (Natural Language Form) */}
                <div className="sticky top-24 z-40 flex justify-center mb-16">
                    <div className="bg-white/90 backdrop-blur-xl border border-gray-200 shadow-xl rounded-full px-8 py-4 flex flex-col md:flex-row items-center gap-3 md:gap-2 text-lg md:text-xl text-slate-500 transition-all hover:shadow-2xl hover:border-emerald-200/50 flex-wrap justify-center">
                        <Search className="w-5 h-5 text-emerald-500 mr-2 hidden md:block" />

                        <span className="whitespace-nowrap">Analisar</span>

                        {/* Dropdown Herói ou Role (Mutuamente Exclusivos) */}
                        {filters.role_id === null && (
                            <div className="relative group">
                                <Dropdown label={labels.hero} items={heroItems} variant="text" className="min-w-[150px] text-center md:text-left" />
                            </div>
                        )}

                        {filters.hero_id === null && (
                            <>
                                {filters.role_id === null && <span className="text-sm text-gray-300 mx-1">ou</span>}
                                <div className="relative group">
                                    <Dropdown label={labels.role} items={roleItems} variant="text" className="min-w-[150px] text-center md:text-left" />
                                </div>
                            </>
                        )}

                        {/* Conectivo Dinâmico */}
                        <span className="whitespace-nowrap">
                            {filters.game_mode_id ? 'no modo' : 'em'}
                        </span>

                        {/* Dropdown Mapa ou Modo (Mutuamente Exclusivos) */}
                        {filters.game_mode_id === null && (
                            <div className="relative group">
                                <Dropdown label={labels.map} items={mapItems} variant="text" className="min-w-[150px] text-center md:text-left" />
                            </div>
                        )}

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

                        <div className="relative group">
                            <Dropdown label={labels.rank} items={rankItems} variant="text" className="min-w-[120px] text-center md:text-left" />
                        </div>
                    </div>
                </div>

                {/* Área de Gráficos (Restaurada e com mais espaço) */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
                    <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
                        <h3 className="text-lg font-bold text-slate-800 mb-4">Tendência de Win Rate</h3>
                        <div className="h-[40vh] min-h-[350px] w-full">
                            <WinRateChart data={chartWinData} heroes={heroes} />
                        </div>
                    </div>
                    <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
                        <h3 className="text-lg font-bold text-slate-800 mb-4">Tendência de Pick Rate</h3>
                        <div className="h-[40vh] min-h-[350px] w-full">
                            <PickRateChart data={chartPickData} heroes={heroes} />
                        </div>
                    </div>
                </div>

                {/* Área de Conteúdo (Tabela) */}
                <div className={`transition-opacity duration-500 ${loading ? 'opacity-50 pointer-events-none' : 'opacity-100'}`}>
                    {loading && (
                        <div className="absolute inset-0 flex items-start justify-center pt-60 z-50">
                            <div className="bg-white px-6 py-3 rounded-full shadow-lg border border-gray-100 flex items-center gap-3">
                                <Loader2 className="animate-spin text-emerald-600" />
                                <span className="text-slate-600 font-medium">Atualizando dados...</span>
                            </div>
                        </div>
                    )}

                    <Table data={tableData} />
                </div>

            </div>
        </section>
    );
};

export default AnalysisSection;
