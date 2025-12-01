import { useState, useEffect, useMemo } from 'react';
import { useAppData } from '../context/AppDataContext';
import Dropdown from '../components/Dropdown';
import Table from '../components/Table';
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
    const [loading, setLoading] = useState(false);

    // Debounce dos filtros para evitar requisições excessivas
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

    // --- Lógica de Busca (Effect) ---
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                // Simulação de delay de rede para ver o loading state (remover em prod)
                // await new Promise(resolve => setTimeout(resolve, 800));

                const { hero_id, map_id, rank_id, role_id, game_mode_id } = debouncedFilters;
                const isDefault = !hero_id && !map_id && !rank_id && !role_id && !game_mode_id;

                let data = [];

                if (isDefault) {
                    // Busca snapshot mais recente
                    const [tWin, tPick] = await Promise.all([
                        fetchAnalytics({ table_name: 'vw_hero_win_latest', limit: 100 }),
                        fetchAnalytics({ table_name: 'vw_hero_pick_latest', limit: 100 })
                    ]);
                    data = enrichData(tWin, tPick);
                } else {
                    // Lógica de filtros (simplificada para focar na tabela)
                    // ... (Mesma lógica de getTableName do original, omitida para brevidade, mas idealmente extraída)
                    // Para este MVP, vamos usar a busca padrão filtrada no cliente ou backend se implementado
                    // Assumindo que fetchAnalytics suporta filtros:

                    const filtersEqual = {};
                    if (hero_id) filtersEqual.hero_id = hero_id;
                    if (map_id) filtersEqual.map_id = map_id;
                    if (rank_id) filtersEqual.rank_id = rank_id;

                    // Fallback: Busca na tabela de fatos principal (ex: hero_win)
                    const [tWin, tPick] = await Promise.all([
                        fetchAnalytics({ table_name: 'hero_win', filters_equal: filtersEqual, limit: 100 }),
                        fetchAnalytics({ table_name: 'hero_pick', filters_equal: filtersEqual, limit: 100 })
                    ]);
                    data = enrichData(tWin, tPick);
                }

                setTableData(data);
            } catch (error) {
                console.error("Erro ao buscar dados:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [debouncedFilters]); // Dispara quando os filtros (debounced) mudam

    // --- Helper: Enriquecer Dados ---
    const enrichData = (winData, pickData) => {
        if (!winData) return [];
        const pickMap = new Map();
        if (pickData) pickData.forEach(p => pickMap.set(`${p.hero_id}-${p.map_id}`, p.pick_rate));

        return winData.map(item => {
            const hero = heroes.find(h => h.hero_id === item.hero_id);
            const map = maps.find(m => m.map_id === item.map_id);
            const rank = ranks.find(r => r.rank_id === item.rank_id);

            return {
                ...item,
                'Herói': hero ? hero.hero_name : item.hero_id,
                'Mapa': map ? map.map_name : 'Todos',
                'Rank': rank ? rank.rank_name : 'Todos',
                'Win Rate (%)': item.win_rate,
                'Pick Rate (%)': pickMap.get(`${item.hero_id}-${item.map_id}`) || item.pick_rate || 0
            };
        });
    };

    // --- Preparação dos Itens (Memoized) ---
    const heroItems = useMemo(() => [{ label: 'Todos', id: null }, ...heroes.map(h => ({ label: h.hero_name, id: h.hero_id }))].map(i => ({ ...i, action: () => handleFilterChange('hero_id', i, 'hero') })), [heroes]);
    const mapItems = useMemo(() => [{ label: 'Todos', id: null }, ...maps.map(m => ({ label: m.map_name, id: m.map_id }))].map(i => ({ ...i, action: () => handleFilterChange('map_id', i, 'map') })), [maps]);
    const rankItems = useMemo(() => [{ label: 'Todos', id: null }, ...ranks.map(r => ({ label: r.rank_name, id: r.rank_id }))].map(i => ({ ...i, action: () => handleFilterChange('rank_id', i, 'rank') })), [ranks]);


    return (
        <section id="analysis" className="w-full min-h-screen bg-white py-20 px-6 relative">
            <div className="max-w-7xl mx-auto">

                {/* Barra de Consulta Flutuante (Natural Language Form) */}
                <div className="sticky top-24 z-40 flex justify-center mb-16">
                    <div className="bg-white/90 backdrop-blur-xl border border-gray-200 shadow-xl rounded-full px-8 py-4 flex flex-col md:flex-row items-center gap-3 md:gap-2 text-lg md:text-xl text-slate-500 transition-all hover:shadow-2xl hover:border-emerald-200/50">
                        <Search className="w-5 h-5 text-emerald-500 mr-2 hidden md:block" />

                        <span className="whitespace-nowrap">Analisar</span>

                        <div className="relative group">
                            <Dropdown
                                label={labels.hero}
                                items={heroItems}
                                variant="text"
                                className="min-w-[150px] text-center md:text-left"
                            />
                        </div>

                        <span className="whitespace-nowrap">em</span>

                        <div className="relative group">
                            <Dropdown
                                label={labels.map}
                                items={mapItems}
                                variant="text"
                                className="min-w-[150px] text-center md:text-left"
                            />
                        </div>

                        <span className="whitespace-nowrap hidden md:inline">no rank</span>
                        <span className="whitespace-nowrap md:hidden">rank</span>

                        <div className="relative group">
                            <Dropdown
                                label={labels.rank}
                                items={rankItems}
                                variant="text"
                                className="min-w-[120px] text-center md:text-left"
                            />
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
