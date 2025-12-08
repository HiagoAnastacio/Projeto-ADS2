/**
 * AnalysisSection.jsx
 *
 * Componente Principal de Análise de Metadados do Overwatch 2.
 *
 * RAZÃO DE EXISTIR:
 * - Ser o painel central onde o usuário interage com os dados.
 * - Gerenciar o estado complexo de filtros (Heróis, Mapas, Ranks, Datas).
 * - Orquestrar a busca de dados na API (backend) e distribuí-los para os gráficos e tabelas.
 * - Implementar lógica de UX avançada: Highlight sincronizado, Sticky Header inteligente e Filtros Derivados.
 *
 * FLUXO DE DADOS:
 * 1. Recebe metadados (heróis, mapas, etc.) do Contexto (AppDataContext).
 * 2. Mantém estado local de 'filters' (IDs selecionados pelo usuário).
 * 3. Usa Derived State para calcular os 'labels' dos dropdowns (garantindo consistência visual).
 * 4. Ao alterar filtros, dispara 'fetchData' (debounced) para buscar estatísticas de Win/Pick Rate.
 * 5. Processa (enrichData) e passa os dados para <WinRateChart>, <PickRateChart> e <Table>.
 * 6. Gerencia estado 'hoveredHero' para sincronizar o destaque visual entre os gráficos.
 */

// Importação de hooks do React para gerenciamento de estado e efeitos colaterais
import { useState, useEffect, useMemo } from 'react';
// Importação do contexto global de dados da aplicação
import { useAppData } from '../context/AppDataContext';
// Importação de componentes de UI reutilizáveis
import Dropdown from '../components/Dropdown';
import MultiSelectDropdown from '../components/MultiSelectDropdown';
// Importação dos componentes de visualização de dados
import Table from '../components/Table';
import WinRateChart from '../components/dashboards/WinRateChart';
import PickRateChart from '../components/dashboards/PickRateChart';
// Importação de ícones para enriquecimento visual
import { Search, Loader2, Calendar as CalendarIcon, ChevronRight } from 'lucide-react';

/**
 * Hook customizado para atrasar a atualização de um valor (Debounce).
 * Utilizado para evitar chamadas excessivas à API enquanto o usuário filtra.
 */
function useDebounce(value, delay) {
    const [debouncedValue, setDebouncedValue] = useState(value);
    useEffect(() => {
        // Define um timer para atualizar o valor após 'delay' ms
        const handler = setTimeout(() => {
            setDebouncedValue(value);
        }, delay);
        // Limpa o timer se o valor mudar antes do tempo (cancelando a execução anterior)
        return () => clearTimeout(handler);
    }, [value, delay]);
    return debouncedValue;
}

const AnalysisSection = () => {
    // Desestruturação dos dados estáticos e função de busca do contexto
    const { heroes, maps, ranks, roles, gameModes, fetchAnalytics } = useAppData();

    // --- Estado dos Filtros ---
    // Mantém os IDs selecionados para cada critério de filtragem
    const [filters, setFilters] = useState({
        hero_ids: [],     // Array para seleção múltipla de heróis
        map_id: null,     // ID do mapa único
        rank_id: null,    // ID do rank
        role_id: null,    // ID da função (Role)
        game_mode_id: null, // ID do modo de jogo
        start_date: '',   // Data inicial (ISO string)
        end_date: ''      // Data final (ISO string)
    });

    // --- Lógica de Ações dos Dropdowns ---
    // Criação memorizada dos itens dos menus. 
    // Cada item possui um 'label', 'id' e uma função 'action' que atualiza o filtro correspondente.
    // O uso de useMemo evita recriação desnecessária desses arrays em cada render.

    // Menu de Mapas: Inclui opção "Todos" (null) + lista de mapas
    const mapItems = useMemo(() => [{ label: 'Todos os Mapas', id: null, action: () => handleFilterChange('map_id', null) }, ...maps.map(m => ({ label: m.map_name, id: m.map_id, action: () => handleFilterChange('map_id', m.map_id) }))], [maps]);
    
    // Menu de Ranks: Inclui opção "Todos" (null) + lista de ranks
    const rankItems = useMemo(() => [{ label: 'Todos os Ranks', id: null, action: () => handleFilterChange('rank_id', null) }, ...ranks.map(r => ({ label: r.rank_name || r.rank, id: r.rank_id, action: () => handleFilterChange('rank_id', r.rank_id) }))], [ranks]);
    
    // Menu de Funções (Roles): Inclui opção "Todas" (null) + lista de roles
    const roleItems = useMemo(() => [{ label: 'Todas as Funções', id: null, action: () => handleFilterChange('role_id', null) }, ...roles.map(r => ({ label: r.role_name || r.role, id: r.role_id, action: () => handleFilterChange('role_id', r.role_id) }))], [roles]);
    
    // Menu de Modos de Jogo: Inclui opção "Todos" (null) + lista de modos
    const modeItems = useMemo(() => [{ label: 'Todos os Modos', id: null, action: () => handleFilterChange('game_mode_id', null) }, ...gameModes.map(g => ({ label: g.game_mode_name, id: g.game_mode_id, action: () => handleFilterChange('game_mode_id', g.game_mode_id) }))], [gameModes]);
    
    // Lista simples de heróis para o componente MultiSelect
    const heroItemsForMulti = useMemo(() => heroes.map(h => ({ label: h.hero_name, id: h.hero_id })), [heroes]);

    // --- Derived State (Labels Calculados) ---
    // Calcula os textos exibidos nos botões com base nos IDs selecionados ('filters').
    // Isso é crucial para evitar dessincronização entre o estado interno e a UI (Bug Fix Fase 2).
    // Se filters.map_id for 5, a UI buscará o nome do mapa 5. Se for null, mostra "Todos os Mapas".
    const currentLabels = {
        map: filters.map_id ? (maps.find(m => m.map_id === filters.map_id)?.map_name || 'Mapa Desconhecido') : 'Todos os Mapas',
        rank: filters.rank_id ? (ranks.find(r => r.rank_id === filters.rank_id)?.rank_name || 'Rank Desconhecido') : 'Todos os Ranks',
        role: filters.role_id ? (roles.find(r => r.role_id === filters.role_id)?.role || 'Role Desconhecida') : 'Todas as Funções', // Busca 'role' (nome da coluna no DB)
        game_mode: filters.game_mode_id ? (gameModes.find(g => g.game_mode_id === filters.game_mode_id)?.game_mode_name || 'Modo Desconhecido') : 'Todos os Modos',
    };

    // --- Estado Highlight Compartilhado ---
    // Armazena qual herói está sendo "focado" pelo mouse (nos gráficos ou legendas).
    // Passado para os gráficos para aplicar o efeito de "Dimming" (escurecer os outros).
    const [hoveredHero, setHoveredHero] = useState(null);

    // Estados locais de dados e UI
    const [availableDates, setAvailableDates] = useState([]); // Datas disponíveis (Patchs) baseadas nos dados
    const [tableData, setTableData] = useState([]);          // Dados formatados para a tabela
    const [chartWinData, setChartWinData] = useState([]);    // Dados para o gráfico de Win Rate
    const [chartPickData, setChartPickData] = useState([]);  // Dados para o gráfico de Pick Rate
    const [loading, setLoading] = useState(false);           // Indicador de carregamento

    // Versão "Debounced" dos filtros (só atualiza após o usuário parar de mexer por 800ms)
    // Usado como dependência do useEffect de busca para evitar spam de requisições.
    const debouncedFilters = useDebounce(filters, 800);

    // --- Handlers de Interação do Usuário ---
    
    // Handler para alteração na seleção múltipla de heróis
    const handleHeroesChange = (selectedIds) => {
        setFilters(prev => ({ 
            ...prev, 
            hero_ids: selectedIds,
            role_id: null // Regra de Negócio: Se selecionar heróis específicos, o filtro de Role (grupo) é desativado.
        }));
    };

    // Handler genérico para alteração de filtros simples (Map, Rank, etc)
    const handleFilterChange = (key, newId) => {
        setFilters(prev => {
            const newFilters = { ...prev, [key]: newId };

            // Regras de Exclusão Mútua para UX Limpa:
            if (key === 'role_id') newFilters.hero_ids = []; // Selecionar Role limpa seleção de Heróis
            if (key === 'map_id' && newId !== null) newFilters.game_mode_id = null; // Mapa implica um Modo, então limpa Modo genérico
            if (key === 'game_mode_id' && newId !== null) newFilters.map_id = null; // Modo genérico limpa Mapa específico

            return newFilters;
        });
    };

    // Handler para seleção de datas (Patches)
    const handleDateSelect = (type, item) => {
        const val = (!item || !item.id) ? '' : item.id;
        setFilters(prev => ({ ...prev, [type]: val }));
    };

    // --- Lógica de Decisão de Tabelas do Banco (Smart Query) ---
    // Determina qual tabela do banco consultar baseado na combinação de filtros,
    // otimizando a performance e garantindo a granularidade correta dos dados.
    const getTableNames = (f) => {
        let winTable = 'hero_win';
        let pickTable = 'hero_pick';
        if (f.map_id && f.rank_id) { winTable = 'hero_rank_map_win'; pickTable = 'hero_rank_map_pick'; } // Granularidade Máxima
        else if (f.game_mode_id && f.rank_id) { winTable = 'hero_game_mode_rank_win'; pickTable = 'hero_game_mode_rank_pick'; }
        else if (f.map_id) { winTable = 'hero_map_win'; pickTable = 'hero_map_pick'; }
        else if (f.game_mode_id) { winTable = 'hero_game_mode_win'; pickTable = 'hero_game_mode_pick'; }
        else if (f.rank_id) { winTable = 'hero_rank_win'; pickTable = 'hero_rank_pick'; }
        return { winTable, pickTable };
    };

    // --- Effect: Busca de Dados (O Coração da Análise) ---
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const { hero_ids, map_id, rank_id, role_id, game_mode_id, start_date, end_date } = debouncedFilters;
                
                // Verifica se está no "Estado Padrão" (sem filtros)
                const isDefault = hero_ids.length === 0 && !map_id && !rank_id && !role_id && !game_mode_id && !start_date && !end_date;
                
                const sortAsc = (a, b) => new Date(a.date_of_the_data) - new Date(b.date_of_the_data);

                let winRes, pickRes;

                if (isDefault) {
                    // Estratégia de Carga Inicial Otimizada:
                    // Busca dados 'latest' (mais recentes) para a Tabela e histórico genérico para Gráficos.
                    const [latestWin, latestPick, histWin, histPick] = await Promise.all([
                        fetchAnalytics({ table_name: 'vw_hero_win_latest', limit: 100 }),
                        fetchAnalytics({ table_name: 'vw_hero_pick_latest', limit: 100 }),
                        fetchAnalytics({ table_name: 'hero_win', limit: 600 }), 
                        fetchAnalytics({ table_name: 'hero_pick', limit: 600 })
                    ]);
                    winRes = (histWin || []).sort(sortAsc);
                    pickRes = (histPick || []).sort(sortAsc);
                    setTableData(enrichData(latestWin || [], latestPick || []));
                } else {
                    // Estratégia de Busca Filtrada:
                    // 1. Determina as tabelas corretas.
                    const { winTable, pickTable } = getTableNames(debouncedFilters);
                    const filtersEqual = {};
                    const filtersIn = {};

                    // 2. Constrói os objetos de filtro para a API
                    if (map_id) filtersEqual.map_id = map_id;
                    if (rank_id) filtersEqual.rank_id = rank_id;
                    if (game_mode_id) filtersEqual.game_mode_id = game_mode_id;
                    
                    if (hero_ids.length > 0) {
                        filtersIn.hero_id = hero_ids;
                    } else if (role_id) {
                         // Transforma Role ID em Lista de Hero IDs (Backend não filtra direto por role nas tabelas de fato)
                         const heroesInRole = heroes.filter(h => h.role_id === role_id).map(h => h.hero_id);
                         if (heroesInRole.length > 0) filtersIn.hero_id = heroesInRole;
                         else { setTableData([]); setLoading(false); return; }
                    }

                    const queryParams = { filters_equal: filtersEqual, filters_in: filtersIn, limit: 400 };
                    if (start_date) queryParams.start_date = start_date;
                    if (end_date) queryParams.end_date = end_date;

                    // 3. Executa as queries em paralelo
                    const [resW, resP] = await Promise.all([
                         fetchAnalytics({ table_name: winTable, ...queryParams }),
                         fetchAnalytics({ table_name: pickTable, ...queryParams })
                    ]);
                    winRes = (resW || []).sort(sortAsc);
                    pickRes = (resP || []).sort(sortAsc);
                    setTableData(enrichData(resW, resP));
                }

                // Atualiza o estado dos gráficos
                setChartWinData(winRes);
                setChartPickData(pickRes);

                // Se estiver no padrão, popula a lista de datas disponíveis (Patches)
                if (isDefault && winRes.length > 0) {
                    const uniqueDates = [...new Set(winRes.map(item => item.date_of_the_data))];
                    uniqueDates.sort((a, b) => new Date(b) - new Date(a)); // Datas mais recentes primeiro
                    setAvailableDates(uniqueDates);
                }

            } catch (error) {
                console.error("Erro ao buscar dados:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [debouncedFilters, heroes]); // Re-executa quando filtros ou lista de heróis mudam

    // --- Função Auxiliar: Enriquecimento de Dados ---
    // Combina dados crus de Win Rate e Pick Rate e adiciona metadados (ícones, nomes de mapa, etc)
    // para exibição amigável na Tabela.
    const enrichData = (winData, pickData) => {
        if (!winData) return [];
        // Cria Map de Pick Rate para acesso O(1)
        const pickMap = new Map();
        if (pickData) pickData.forEach(p => pickMap.set(`${p.hero_id}-${p.date_of_the_data}`, p.pick_rate));
        
        return winData.map(item => {
            const hero = heroes.find(h => h.hero_id === item.hero_id);
            const map = maps.find(m => m.map_id === item.map_id);
            const rank = ranks.find(r => r.rank_id === item.rank_id);
            const mode = gameModes.find(g => g.game_mode_id === item.game_mode_id);
            const formattedDate = new Date(item.date_of_the_data).toLocaleDateString('pt-BR');

            return {
                'Ícone': hero ? hero.hero_icon_img_link : null,
                'Herói': hero ? hero.hero_name : `ID ${item.hero_id}`,
                'Win Rate (%)': item.win_rate,
                'Pick Rate (%)': pickMap.get(`${item.hero_id}-${item.date_of_the_data}`) || item.pick_rate || '-',
                'Data': formattedDate,
                _raw_date: item.date_of_the_data, // Usado para ordenação na tabela
                ...(map && { 'Mapa': map.map_name }),
                ...(rank && { 'Rank': rank.rank_name }),
                ...(mode && { 'Modo': mode.game_mode_name }),
            };
        });
    };

    // Cria os itens de data para os dropdowns de Patch
    const dateItems = useMemo(() => {
        const items = availableDates.map(dateStr => {
            const fmt = new Date(dateStr).toLocaleDateString('pt-BR');
            return { label: fmt, id: dateStr }; 
        });
        return [{ label: 'Qualquer Data', id: null }, ...items];
    }, [availableDates]);

    return (
        <section 
            id="analysis-section" 
            className="scroll-mt-28 w-full max-w-[95%] mx-auto mt-8 mb-16 bg-white rounded-[3rem] shadow-[0_20px_50px_rgba(0,0,0,0.08)] relative overflow-visible ring-1 ring-slate-100 pb-12"
        >
            {/* 
               --- CÁPSULA FLUTUANTE DE FILTROS --- 
               Mobile: 'relative' (flui com a página para economizar espaço).
               Desktop (lg+): 'sticky top-20' (acompanha o scroll para fácil acesso).
               Estilo 'Box Shadow' e 'Border Radius' criam o efeito de cartão flutuante.
            */}
            <div className="relative lg:sticky lg:top-20 z-50 flex justify-center pt-8 pb-4 pointer-events-none"> 
                <div className="pointer-events-auto bg-white/95 backdrop-blur-xl border border-gray-200 shadow-xl rounded-[2.5rem] px-4 md:px-8 py-5 flex flex-col items-center gap-4 transition-all hover:shadow-2xl hover:border-emerald-200/50 w-full max-w-5xl mx-4">
                        
                    {/* Linha 1: Filtros de Linguagem Natural 
                       Usa flex-wrap para quebrar linha graciosamente em telas menores.
                    */}
                    <div className="flex flex-wrap justify-center items-center gap-x-2 gap-y-3 text-lg md:text-xl text-slate-500 font-light text-center">
                        <Search className="w-5 h-5 text-emerald-500 mr-1" />
                        <span>Analisar</span>
                        
                        {/* SELEÇÃO DE HERÓIS INTELIGENTE:
                           - Se nao tem role, pode escolher heróis avulsos.
                           - Se escolhe role, o multi-select some e vira um dropdown de role.
                        */}
                        {filters.role_id === null && (
                            <div className="relative z-50">
                                <MultiSelectDropdown 
                                    label="Todos os Heróis" 
                                    items={heroItemsForMulti} 
                                    selectedIds={filters.hero_ids} 
                                    onChange={handleHeroesChange}
                                    variant="text"
                                />
                            </div>
                        )}

                        {filters.hero_ids.length === 0 && (
                            <>
                                {filters.role_id === null && <span className="text-sm text-gray-300 mx-1">ou</span>}
                                
                                <div className="relative group z-40">
                                    <Dropdown 
                                        label={currentLabels.role} 
                                        items={roleItems} 
                                        variant="text" 
                                    />
                                </div>
                            </>
                        )}

                        <span>{filters.game_mode_id ? 'no modo' : 'em'}</span>

                        {filters.game_mode_id === null && (
                            <div className="relative group z-30">
                                <Dropdown label={currentLabels.map} items={mapItems} variant="text" />
                            </div>
                        )}
                        
                        {filters.map_id === null && (
                            <>
                                {filters.game_mode_id === null && <span className="text-sm text-gray-300 mx-1">ou</span>}
                                <div className="relative group z-30">
                                    <Dropdown label={currentLabels.game_mode} items={modeItems} variant="text" />
                                </div>
                            </>
                        )}

                        <span className="hidden md:inline">no rank</span>
                        <div className="relative group z-20">
                            <Dropdown label={currentLabels.rank} items={rankItems} variant="text" />
                        </div>
                    </div>

                    {/* Linha 2: Seletor de Intervalo de Datas/Patches */}
                    <div className="flex flex-wrap justify-center items-center gap-3 w-full border-t border-gray-100 pt-3 mt-1 px-4">
                        <span className="text-xs text-slate-400 font-bold uppercase tracking-wider flex items-center bg-slate-50 px-3 py-1 rounded-full border border-slate-100">
                            <CalendarIcon className="w-3 h-3 mr-2 text-emerald-500" /> Patch / Data
                        </span>
                        
                        <div className="flex items-center gap-2">
                             <Dropdown 
                                label={filters.start_date ? new Date(filters.start_date).toLocaleDateString('pt-BR') : 'Início'} 
                                items={dateItems.map(i => ({ ...i, action: () => handleDateSelect('start_date', i) }))}
                                variant="standard"
                                className="w-32 md:w-36" // Largura responsiva
                            />
                            <span className="text-slate-300"><ChevronRight className="w-4 h-4" /></span>
                            <Dropdown 
                                label={filters.end_date ? new Date(filters.end_date).toLocaleDateString('pt-BR') : 'Fim'}
                                items={dateItems.map(i => ({ ...i, action: () => handleDateSelect('end_date', i) }))}
                                variant="standard"
                                className="w-32 md:w-36"
                            />
                        </div>
                    </div>

                </div>
            </div>

            {/* Conteúdo Principal (Gráficos e Tabela) */}
            <div className="max-w-7xl mx-auto px-4 md:px-10 pt-4">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
                     <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
                        <h3 className="text-lg font-bold text-slate-800 mb-4">Tendência de Win Rate</h3>
                        <div className="h-[40vh] min-h-[350px] w-full">
                            <WinRateChart 
                                data={chartWinData} 
                                heroes={heroes}
                                hoveredHero={hoveredHero}
                                setHoveredHero={setHoveredHero}
                            />
                        </div>
                    </div>
                    <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
                        <h3 className="text-lg font-bold text-slate-800 mb-4">Tendência de Pick Rate</h3>
                        <div className="h-[40vh] min-h-[350px] w-full">
                            <PickRateChart 
                                data={chartPickData} 
                                heroes={heroes} 
                                hoveredHero={hoveredHero}
                                setHoveredHero={setHoveredHero}
                            />
                        </div>
                    </div>
                </div>

                {/* Tabela com Loading State Overlay */}
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
