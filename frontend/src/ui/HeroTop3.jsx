/**
 * HeroTop3.jsx
 *
 * Componente de Destaque (Showcase).
 * Exibe os 3 heróis com maior taxa de vitória (Win Rate) globalmente.
 * Inclui cards com estatísticas e um mini-gráfico de tendência (Sparkline).
 */

// Importa hooks e contexto
import { useState, useEffect } from 'react';
import { useAppData } from '../context/AppDataContext';
// Importa componentes visuais
import Sparkline from '../components/Sparkline';
import { Trophy, TrendingUp } from 'lucide-react';

/**
 * Componente HeroTop3
 * 
 * Busca dados da view 'vw_hero_win_latest' e filtra os top 3.
 */
const HeroTop3 = () => {
    // Acessa dados globais e função de fetch
    const { heroes, fetchAnalytics } = useAppData();
    // Estado local para armazenar os top heróis processados
    const [topHeroes, setTopHeroes] = useState([]);
    // Estado de carregamento
    const [loading, setLoading] = useState(true);

    // Efeito para carregar dados ao montar o componente
    useEffect(() => {
        const loadTopHeroes = async () => {
            try {
                // Busca os dados mais recentes de Win Rate (snapshot)
                const data = await fetchAnalytics({
                    table_name: 'vw_hero_win_latest',
                    limit: 100 // Busca um lote grande para garantir que temos todos os heróis para ordenar
                });

                // Helper para garantir que os valores sejam numéricos
                const parseValue = (val) => {
                    if (val === null || val === undefined) return 0;
                    if (typeof val === 'number') return val;
                    if (typeof val === 'string') {
                        return parseFloat(val.replace(',', '.'));
                    }
                    return 0;
                };

                // Ordena os dados por Win Rate decrescente e pega os 3 primeiros
                const sorted = data.sort((a, b) => parseValue(b.win_rate) - parseValue(a.win_rate)).slice(0, 3);

                // --- BUSCA DE HISTÓRICO REAL (Sparkline) ---
                // Extrai os IDs dos top 3 heróis
                const topHeroIds = sorted.map(h => h.hero_id);

                // Busca histórico apenas para esses heróis na tabela 'hero_win'
                // Usa filters_in para buscar múltiplos IDs de uma vez
                let historyData = [];
                if (topHeroIds.length > 0) {
                    historyData = await fetchAnalytics({
                        table_name: 'hero_win',
                        limit: 500, // Garante histórico suficiente
                        filters_in: { hero_id: topHeroIds }
                    });
                }

                // Enriquece os dados com informações de metadados e histórico real
                const enriched = sorted.map(item => {
                    // Busca info do herói na lista estática
                    const heroInfo = heroes.find(h => h.hero_id === item.hero_id);
                    const winRateVal = parseValue(item.win_rate);

                    // Filtra o histórico específico deste herói e ordena por data
                    const heroHistory = historyData
                        .filter(h => h.hero_id === item.hero_id)
                        .sort((a, b) => new Date(a.date_of_the_data) - new Date(b.date_of_the_data))
                        .map(h => ({ value: parseValue(h.win_rate) }));

                    return {
                        ...item,
                        hero_name: heroInfo?.hero_name || 'Unknown',
                        role_name: heroInfo?.role_name || 'Role',
                        win_rate: winRateVal, // Garante número para exibição correta
                        // Usa o histórico real se existir, senão usa um fallback (apenas o valor atual)
                        trend: heroHistory.length > 0 ? heroHistory : [{ value: winRateVal }]
                    };
                });

                setTopHeroes(enriched);
            } catch (error) {
                console.error("Erro ao carregar Top 3:", error);
            } finally {
                setLoading(false);
            }
        };

        // Só carrega se já tivermos a lista de heróis (dependência do contexto)
        if (heroes.length > 0) {
            loadTopHeroes();
        }
    }, [heroes, fetchAnalytics]);

    // Renderização de Loading (Skeleton UI)
    if (loading) {
        return (
            <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Cria 3 placeholders pulsantes */}
                    {[1, 2, 3].map(i => (
                        <div key={i} className="h-48 bg-gray-200 rounded-xl animate-pulse"></div>
                    ))}
                </div>
            </div>
        );
    }

    // Se não houver dados, não renderiza nada
    if (topHeroes.length === 0) return null;

    return (
        <section className="w-full bg-white border-b border-gray-200 mb-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
                {/* Título da Seção */}
                <div className="flex items-center mb-6">
                    <Trophy className="h-6 w-6 text-yellow-500 mr-2" />
                    <h2 className="text-2xl font-bold text-gray-900">Top 3 Heróis (Win Rate)</h2>
                </div>

                {/* Grid de Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {topHeroes.map((hero, index) => (
                        <div key={hero.hero_id || index} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow relative overflow-hidden">
                            {/* Medalha de Rank (Número de fundo) */}
                            <div className="absolute top-4 right-4 text-6xl font-black text-gray-50 opacity-50 z-0 select-none">
                                #{index + 1}
                            </div>

                            <div className="relative z-10">
                                {/* Header do Card: Nome e Ícone */}
                                <div className="flex items-center justify-between mb-4">
                                    <div>
                                        <h3 className="text-lg font-bold text-gray-900">{hero.hero_name}</h3>
                                        <span className="text-sm text-gray-500">Win Rate Global</span>
                                    </div>
                                    {/* Avatar do Herói (Placeholder ou Imagem) */}
                                    <div className="h-12 w-12 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 font-bold text-xl overflow-hidden">
                                        {hero.hero_icon_img_link ? (
                                            <img src={hero.hero_icon_img_link} alt={hero.hero_name} className="h-full w-full object-cover" />
                                        ) : (
                                            '' // Fallback vazio
                                        )}
                                    </div>
                                </div>

                                {/* Estatísticas Principais */}
                                <div className="flex items-end justify-between">
                                    <div>
                                        <p className="text-sm text-gray-500 mb-1">Win Rate</p>
                                        <p className="text-3xl font-extrabold text-gray-900">{hero.win_rate}%</p>
                                    </div>
                                </div>

                                {/* Gráfico de Tendência (Sparkline) */}
                                <div className="mt-4 pt-4 border-t border-gray-50">
                                    <p className="text-xs text-gray-400 mb-2 uppercase tracking-wide">Tendência (Estimada)</p>
                                    {/* Container com altura fixa para o gráfico */}
                                    <div className="h-16">
                                        <Sparkline data={hero.trend} color={index === 0 ? "#eab308" : "#f97316"} />
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

// Exporta o componente
export default HeroTop3;
