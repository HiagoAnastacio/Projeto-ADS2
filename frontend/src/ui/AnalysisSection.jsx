/**
 * AnalysisSection.jsx
 *
 * Seção Principal de Análise de Dados.
 * Contém os filtros globais, gráficos de Win Rate e Pick Rate, e a tabela detalhada.
 * Gerencia o estado local dos filtros e a busca de dados na API.
 */

// Importa hooks do React
import { useState, useEffect } from 'react';
// Importa hook do contexto global para acessar listas de dimensões e função de fetch
import { useAppData } from '../context/AppDataContext';
// Importa componentes de UI
import Dropdown from '../components/Dropdown';
import WinRateChart from '../components/dashboards/WinRateChart';
import PickRateChart from '../components/dashboards/PickRateChart';
import Table from '../components/Table';
// Importa ícones
import { Filter, Search, RotateCcw } from 'lucide-react';

/**
 * Componente AnalysisSection
 * 
 * Responsável por:
 * 1. Renderizar a barra de filtros (Herói, Mapa, Rank, etc.)
 * 2. Buscar dados analíticos baseados nos filtros selecionados.
 * 3. Gerenciar a lógica de separação de dados para gráficos (histórico) e tabela (snapshot).
 */
const AnalysisSection = () => {
    // Desestrutura dados e funções do contexto global
    const { heroes, maps, ranks, roles, gameModes, fetchAnalytics } = useAppData();

    // --- Estado dos Filtros ---
    // Armazena os IDs selecionados para cada dimensão
    const [filters, setFilters] = useState({
        hero_id: null,
        map_id: null,
        rank_id: null,
        role_id: null,
        game_mode_id: null
    });

    // --- Estado dos Dados ---
    // Dados específicos para os gráficos (podem conter histórico)
    const [chartWinData, setChartWinData] = useState([]);
    const [chartPickData, setChartPickData] = useState([]);
    // Dados específicos para a tabela (snapshot mais recente)
    const [tableWinData, setTableWinData] = useState([]);
    const [tablePickData, setTablePickData] = useState([]);
    // Estado de carregamento da busca
    const [loading, setLoading] = useState(false);

    // --- Estado das Labels ---
    // Controla o texto exibido nos botões dos dropdowns
    const [labels, setLabels] = useState({
        hero: 'Todos os Heróis',
        map: 'Todos os Mapas',
        rank: 'Todos os Ranks',
        role: 'Todas as Funções',
        game_mode: 'Todos os Modos'
    });

    /**
     * handleFilterChange
     * Atualiza o estado dos filtros e labels, aplicando regras de exclusão mútua.
     * 
     * @param {string} key - Chave do filtro (ex: 'hero_id')
     * @param {object} item - Objeto selecionado { id, label }
     * @param {string} labelKey - Chave da label (ex: 'hero')
     */
    const handleFilterChange = (key, item, labelKey) => {
        setFilters(prev => {
            const newFilters = { ...prev, [key]: item.id };
            const newLabels = { ...labels, [labelKey]: item.label };

            // Regra de Negócio: Herói e Função são mutuamente exclusivos
            // Se selecionar um herói, limpa a seleção de função
            if (key === 'hero_id' && item.id !== null) {
                newFilters.role_id = null;
                newLabels.role = 'Todas as Funções';
            }
            // Se selecionar uma função, limpa a seleção de herói
            if (key === 'role_id' && item.id !== null) {
                newFilters.hero_id = null;
                newLabels.hero = 'Todos os Heróis';
            }

            // Regra de Negócio: Mapa e Modo de Jogo são mutuamente exclusivos
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

    /**
     * clearFilters
     * Reseta todos os filtros para o estado inicial (null/Todos).
     */
    const clearFilters = () => {
        setFilters({ hero_id: null, map_id: null, rank_id: null, role_id: null, game_mode_id: null });
        setLabels({ hero: 'Todos os Heróis', map: 'Todos os Mapas', rank: 'Todos os Ranks', role: 'Todas as Funções', game_mode: 'Todos os Modos' });
    };

    /**
     * getTableName
     * Determina qual tabela do banco de dados consultar com base na combinação de filtros ativos.
     * Isso é necessário porque temos tabelas pré-agregadas para performance (ex: hero_map_win).
     * 
     * @param {string} metricType - Tipo da métrica ('win' ou 'pick')
     */
    const getTableName = (metricType) => {
        const { hero_id, map_id, rank_id, game_mode_id, role_id } = filters;
        let base = 'hero';

        // Prioridade 1: Game Mode
        if (game_mode_id) {
            if (rank_id) return `${base}_game_mode_rank_${metricType}`;
            return `${base}_game_mode_${metricType}`;
        }

        // Prioridade 2: Mapa
        if (map_id) {
            if (rank_id) return `${base}_rank_map_${metricType}`;
            return `${base}_map_${metricType}`;
        }

        // Prioridade 3: Rank (sem mapa/modo)
        if (rank_id) return `${base}_rank_${metricType}`;

        // Default: Apenas Herói (ou Função, que filtra na tabela de herói)
        return `${base}_${metricType}`;
    };

    /**
     * handleSearch
     * Executa a busca de dados na API.
     * Gerencia a lógica de buscar dados diferentes para gráfico e tabela no modo default.
     */
    const handleSearch = async () => {
        setLoading(true);
        try {
            const { hero_id, map_id, rank_id, role_id, game_mode_id } = filters;
            // Verifica se nenhum filtro está ativo
            const isDefault = !hero_id && !map_id && !rank_id && !role_id && !game_mode_id;

            if (isDefault) {
                // --- Cenario Padrão (Sem Filtros) ---
                // Gráficos: Buscam histórico completo (tabelas 'hero_win', 'hero_pick')
                // Tabela: Busca apenas o snapshot mais recente (views 'vw_hero_win_latest', etc)
                // Isso evita que a tabela mostre múltiplas linhas para o mesmo herói em datas diferentes.

                const [cWin, cPick, tWin, tPick] = await Promise.all([
                    fetchAnalytics({ table_name: 'hero_win', limit: 500 }), // Histórico para gráficos
                    fetchAnalytics({ table_name: 'hero_pick', limit: 500 }),
                    fetchAnalytics({ table_name: 'vw_hero_win_latest', limit: 100 }), // Latest para tabela
                    fetchAnalytics({ table_name: 'vw_hero_pick_latest', limit: 100 })
                ]);

                setChartWinData(cWin);
                setChartPickData(cPick);
                setTableWinData(tWin);
                setTablePickData(tPick);
            } else {
                // --- Cenário com Filtros ---
                const filtersEqual = {};
                const filtersIn = {};

                // Mapeia filtros diretos para o objeto da query
                if (hero_id) filtersEqual.hero_id = hero_id;
                if (map_id) filtersEqual.map_id = map_id;
                if (rank_id) filtersEqual.rank_id = rank_id;
                if (game_mode_id) filtersEqual.game_mode_id = game_mode_id;

                // Tratamento Especial para Role:
                // Como as tabelas de fatos não têm 'role_id', filtramos por uma lista de 'hero_id' que pertencem àquela role.
                if (role_id) {
                    const heroesInRole = heroes.filter(h => h.role_id === role_id).map(h => h.hero_id);
                    if (heroesInRole.length > 0) {
                        filtersIn.hero_id = heroesInRole; // Usa filtro IN [id1, id2...]
                    } else {
                        filtersEqual.hero_id = -1; // Força resultado vazio se role não tiver heróis
                    }
                }

                // Determina as tabelas corretas a consultar
                const winTable = getTableName('win');
                const pickTable = getTableName('pick');

                // Configura payload da requisição
                const payload = { limit: 500 }; // Limite maior para garantir histórico nos gráficos filtrados
                if (Object.keys(filtersEqual).length > 0) payload.filters_equal = filtersEqual;
                if (Object.keys(filtersIn).length > 0) payload.filters_in = filtersIn;

                // Busca dados (neste caso, usamos os mesmos dados para gráfico e tabela)
                const [winData, pickData] = await Promise.all([
                    fetchAnalytics({ table_name: winTable, ...payload }),
                    fetchAnalytics({ table_name: pickTable, ...payload })
                ]);

                setChartWinData(winData);
                setChartPickData(pickData);
                setTableWinData(winData);
                setTablePickData(pickData);
            }
        } catch (error) {
            console.error("Erro ao buscar dados:", error);
        } finally {
            setLoading(false);
        }
    };

    // Efeito para carregar dados iniciais ao montar o componente
    useEffect(() => {
        handleSearch();
    }, []);

    // --- Preparação dos Itens dos Dropdowns ---
    // Adiciona a opção "Todos" no início de cada lista

    const heroItems = [{ label: 'Todos', id: null, action: () => handleFilterChange('hero_id', { id: null, label: 'Todos os Heróis' }, 'hero') },
    ...heroes.map(h => ({ label: h.hero_name, id: h.hero_id, action: () => handleFilterChange('hero_id', { id: h.hero_id, label: h.hero_name }, 'hero') }))];

    const mapItems = [{ label: 'Todos', id: null, action: () => handleFilterChange('map_id', { id: null, label: 'Todos os Mapas' }, 'map') },
    ...maps.map(m => ({ label: m.map_name, id: m.map_id, action: () => handleFilterChange('map_id', { id: m.map_id, label: m.map_name }, 'map') }))];

    const rankItems = [{ label: 'Todos', id: null, action: () => handleFilterChange('rank_id', { id: null, label: 'Todos os Ranks' }, 'rank') },
    ...ranks.map(r => ({ label: r.rank_name, id: r.rank_id, action: () => handleFilterChange('rank_id', { id: r.rank_id, label: r.rank_name }, 'rank') }))];

    const roleItems = [{ label: 'Todos', id: null, action: () => handleFilterChange('role_id', { id: null, label: 'Todas as Funções' }, 'role') },
    ...roles.map(r => ({ label: r.role, id: r.role_id, action: () => handleFilterChange('role_id', { id: r.role_id, label: r.role }, 'role') }))];

    const gameModeItems = [{ label: 'Todos', id: null, action: () => handleFilterChange('game_mode_id', { id: null, label: 'Todos os Modos' }, 'game_mode') },
    ...gameModes.map(g => ({ label: g.game_mode_name, id: g.game_mode_id, action: () => handleFilterChange('game_mode_id', { id: g.game_mode_id, label: g.game_mode_name }, 'game_mode') }))];

    /**
     * enrichData
     * Combina dados de Win Rate e Pick Rate em um único array para a tabela.
     * Também resolve os IDs (hero_id, map_id) para seus nomes legíveis.
     */
    const enrichData = (winData, pickData) => {
        if (!winData || winData.length === 0) return [];

        // Cria um mapa para acesso rápido aos dados de Pick Rate
        // Chave composta garante unicidade: hero + map + rank + date
        const pickMap = new Map();
        if (pickData) {
            pickData.forEach(p => {
                const key = `${p.hero_id}-${p.map_id}-${p.rank_id}-${p.date_of_the_data}`;
                pickMap.set(key, p.pick_rate);
            });
        }

        // Mapeia os dados de Win Rate, adicionando Pick Rate e nomes
        return winData.map(item => {
            const newItem = {};

            // Resolução de IDs para Nomes usando as listas do contexto
            if (item.hero_id) {
                const hero = heroes.find(h => h.hero_id === item.hero_id);
                newItem['Herói'] = hero ? hero.hero_name : item.hero_id;
            }
            if (item.map_id) {
                const map = maps.find(m => m.map_id === item.map_id);
                newItem['Mapa'] = map ? map.map_name : item.map_id;
            }
            if (item.rank_id) {
                const rank = ranks.find(r => r.rank_id === item.rank_id);
                newItem['Rank'] = rank ? rank.rank_name : item.rank_id;
            }
            if (item.role_id) {
                const role = roles.find(r => r.role_id === item.role_id);
                newItem['Função'] = role ? role.role : item.role_id;
            }
            if (item.game_mode_id) {
                const gm = gameModes.find(g => g.game_mode_id === item.game_mode_id);
                newItem['Modo de Jogo'] = gm ? gm.game_mode_name : item.game_mode_id;
            }

            // Adiciona métrica de Win Rate
            if (item.win_rate !== undefined) newItem['Win Rate (%)'] = item.win_rate;

            // Tenta encontrar o Pick Rate correspondente no mapa criado anteriormente
            const key = `${item.hero_id}-${item.map_id}-${item.rank_id}-${item.date_of_the_data}`;
            if (pickMap.has(key)) {
                newItem['Pick Rate (%)'] = pickMap.get(key);
            } else if (item.pick_rate !== undefined) {
                // Fallback caso o próprio item já tenha pick_rate (algumas views podem ter)
                newItem['Pick Rate (%)'] = item.pick_rate;
            }

            // Adiciona Data
            if (item.date_of_the_data) {
                newItem['Data'] = item.date_of_the_data;
            }

            return newItem;
        });
    };

    return (
        <section id="analysis-section" className="w-full py-8 scroll-mt-20">
            <div className="flex flex-col mb-8 gap-6">
                {/* Cabeçalho da Seção */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center">
                        <Filter className="h-6 w-6 text-orange-600 mr-2" />
                        <h2 className="text-2xl font-bold text-gray-900">Análise Detalhada</h2>
                    </div>
                    {/* Botão de Limpar Filtros */}
                    <button onClick={clearFilters} className="text-sm text-gray-500 hover:text-orange-600 flex items-center">
                        <RotateCcw className="h-4 w-4 mr-1" /> Limpar Filtros
                    </button>
                </div>

                {/* Área de Filtros - Layout Responsivo */}
                <div className="flex flex-col lg:flex-row gap-4 w-full">
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 flex-1">
                        {/* Dropdowns de Filtro */}
                        {/* Aplica classe de opacidade se o filtro mutuamente exclusivo estiver ativo */}
                        <div className={filters.role_id ? 'opacity-50 pointer-events-none' : ''}>
                            <Dropdown label={labels.hero} items={heroItems} className="w-full" />
                        </div>
                        <div className={filters.hero_id ? 'opacity-50 pointer-events-none' : ''}>
                            <Dropdown label={labels.role} items={roleItems} className="w-full" />
                        </div>

                        <div className={filters.game_mode_id ? 'opacity-50 pointer-events-none' : ''}>
                            <Dropdown label={labels.map} items={mapItems} className="w-full" />
                        </div>
                        <div className={filters.map_id ? 'opacity-50 pointer-events-none' : ''}>
                            <Dropdown label={labels.game_mode} items={gameModeItems} className="w-full" />
                        </div>

                        <Dropdown label={labels.rank} items={rankItems} className="w-full" />
                    </div>

                    {/* Botão de Filtrar */}
                    <button
                        onClick={handleSearch}
                        disabled={loading}
                        className="lg:w-auto w-full inline-flex justify-center items-center rounded-md border border-transparent shadow-sm px-6 py-2 bg-orange-600 text-base font-medium text-white hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 transition-colors whitespace-nowrap"
                    >
                        {loading ? 'Buscando...' : <><Search className="h-4 w-4 mr-2" /> Filtrar</>}
                    </button>
                </div>
            </div>

            {/* Gráficos (Separados) - Passa os dados de gráfico e a lista de heróis */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                <WinRateChart data={chartWinData} heroes={heroes} />
                <PickRateChart data={chartPickData} heroes={heroes} />
            </div>

            {/* Tabela de Dados Detalhados - Passa os dados de tabela enriquecidos */}
            <div className="mt-8">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Dados Detalhados (Win & Pick Rate)</h3>
                <Table data={enrichData(tableWinData, tablePickData)} />
            </div>
        </section>
    );
};

// Exporta o componente
export default AnalysisSection;
