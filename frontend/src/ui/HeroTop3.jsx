import { useState, useEffect } from 'react';
import { useAppData } from '../context/AppDataContext';
import Sparkline from '../components/Sparkline';
import { ArrowDown, TrendingUp, Trophy } from 'lucide-react';

const HeroTop3 = () => {
    // --- LÓGICA DE DADOS REAIS (Do HEAD) ---
    const { heroes, fetchAnalytics } = useAppData();
    const [topHeroes, setTopHeroes] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadTopHeroes = async () => {
            try {
                // Busca os dados mais recentes de Win Rate (snapshot)
                const data = await fetchAnalytics({
                    table_name: 'vw_hero_win_latest',
                    limit: 100
                });

                const parseValue = (val) => {
                    if (val === null || val === undefined) return 0;
                    if (typeof val === 'number') return val;
                    if (typeof val === 'string') return parseFloat(val.replace(',', '.'));
                    return 0;
                };

                // Ordena e pega Top 3
                const sorted = data.sort((a, b) => parseValue(b.win_rate) - parseValue(a.win_rate)).slice(0, 3);

                // Busca Histórico Real
                const topHeroIds = sorted.map(h => h.hero_id);
                let historyData = [];
                if (topHeroIds.length > 0) {
                    historyData = await fetchAnalytics({
                        table_name: 'hero_win',
                        limit: 500,
                        filters_in: { hero_id: topHeroIds }
                    });
                }

                // Enriquece os dados
                const enriched = sorted.map(item => {
                    const heroInfo = heroes.find(h => h.hero_id === item.hero_id);
                    const winRateVal = parseValue(item.win_rate);

                    const heroHistory = historyData
                        .filter(h => h.hero_id === item.hero_id)
                        .sort((a, b) => new Date(a.date_of_the_data) - new Date(b.date_of_the_data))
                        .map(h => ({ value: parseValue(h.win_rate) }));

                    return {
                        ...item,
                        hero_name: heroInfo?.hero_name || 'Unknown',
                        role_name: heroInfo?.role_name || 'Role',
                        win_rate: winRateVal,
                        trend: heroHistory.length > 0 ? heroHistory : [{ value: winRateVal }],
                        // Tenta usar imagem do contexto se disponível, senão null para fallback
                        image: heroInfo?.hero_icon_img_link || null
                    };
                });

                setTopHeroes(enriched);
            } catch (error) {
                console.error("Erro ao carregar Top 3:", error);
            } finally {
                setLoading(false);
            }
        };

        if (heroes.length > 0) {
            loadTopHeroes();
        }
    }, [heroes, fetchAnalytics]);

    const handleScrollToAnalysis = () => {
        const analysisSection = document.getElementById('analysis-section'); // ID corrigido para o usado no AnalysisSection
        if (analysisSection) {
            analysisSection.scrollIntoView({ behavior: 'smooth' });
        }
    };

    // --- UI POLIDA (Do origin/17-11) ---

    if (loading) {
        return (
            <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="h-48 bg-gray-200 rounded-xl animate-pulse"></div>
                    ))}
                </div>
            </div>
        );
    }

    if (topHeroes.length === 0) return null;

    return (
        <section className="relative min-h-[85vh] flex flex-col justify-center items-center bg-gray-50 px-6 pt-20 pb-10">
            {/* Background Decorativo */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-100/30 rounded-full blur-3xl" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-rose-100/30 rounded-full blur-3xl" />
            </div>

            <div className="relative z-10 w-full max-w-6xl text-center">
                <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4 tracking-tight">
                    Destaques do Meta
                    <span className="block text-lg md:text-xl font-normal text-slate-500 mt-2">
                        Semana Atual • Competitivo Global
                    </span>
                </h1>

                {/* Grid de Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 mb-16">
                    {topHeroes.map((hero, index) => (
                        <div
                            key={hero.hero_id || index}
                            className="group bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-100 flex flex-col items-center"
                        >
                            <div className="relative mb-4">
                                <div className="w-20 h-20 rounded-full bg-gray-200 overflow-hidden ring-4 ring-gray-50 group-hover:ring-emerald-50 transition-all">
                                    {/* Imagem ou Fallback */}
                                    {hero.image ? (
                                        <img src={hero.image} alt={hero.hero_name} className="w-full h-full object-cover" />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center bg-slate-100 text-slate-400 font-bold text-xl">
                                            {hero.hero_name ? hero.hero_name[0] : '?'}
                                        </div>
                                    )}
                                </div>
                                <div className="absolute -bottom-2 -right-2 bg-white rounded-full p-1 shadow-sm border border-gray-100">
                                    {index === 0 && <span className="text-xl">🥇</span>}
                                    {index === 1 && <span className="text-xl">🥈</span>}
                                    {index === 2 && <span className="text-xl">🥉</span>}
                                </div>
                            </div>

                            <h3 className="text-lg font-semibold text-slate-900">{hero.hero_name}</h3>
                            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-4">{hero.role_name}</span>

                            <div className="flex items-end gap-2 mb-4">
                                <span className="text-4xl font-light text-slate-900 tracking-tighter">
                                    {hero.win_rate}%
                                </span>
                                {/* Mock de variação percentual, já que não calculamos isso no backend ainda */}
                                <span className="flex items-center text-emerald-600 text-sm font-medium mb-1">
                                    <TrendingUp size={16} className="mr-1" />
                                    +1.2%
                                </span>
                            </div>

                            <div className="w-full h-12 opacity-70 group-hover:opacity-100 transition-opacity">
                                <Sparkline data={hero.trend} color="#10b981" />
                            </div>
                        </div>
                    ))}
                </div>

                {/* CTA Button */}
                <button
                    onClick={handleScrollToAnalysis}
                    className="inline-flex items-center gap-2 px-6 py-3 rounded-full border border-slate-200 text-slate-600 hover:text-slate-900 hover:border-slate-400 hover:bg-white transition-all duration-300 group"
                >
                    <span>Explore o Meta</span>
                    <ArrowDown size={18} className="group-hover:translate-y-1 transition-transform" />
                </button>
            </div>
        </section>
    );
};

export default HeroTop3;
