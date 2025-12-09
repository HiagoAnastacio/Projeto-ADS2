/**
 * HeroTop3.jsx
 *
 * Componente responsável por exibir os 3 heróis com melhor desempenho (Win Rate) no meta atual.
 *
 * RAZÃO DE EXISTIR:
 * - Fornecer ao usuário uma visão rápida e impactante dos "Líderes do Meta" assim que a página carrega.
 * - Servir como um "gancho" visual (Hero Section) para engajar o usuário antes da análise detalhada.
 * - Exibir tendências de curto prazo (Sparklines) para mostrar se o herói está em ascensão ou queda.
 *
 * POSIÇÃO NO FLUXO DE DADOS:
 * 1. Busca dados independentemente via `fetchAnalytics` (não depende dos filtros da AnalysisSection).
 * 2. Consulta a view `vw_hero_win_latest` para obter o snapshot mais recente de todos os heróis.
 * 3. Ordena os dados por Win Rate decrescente e seleciona os top 3.
 * 4. Para cada um dos top 3, faz uma nova busca na tabela histórica `hero_win` para gerar o gráfico de tendência (Sparkline).
 * 5. Renderiza os cards com medalhas (Ouro, Prata, Bronze) e botão de rolagem para a seção de análise.
 */

// Importa hooks do React
import { useState, useEffect } from 'react';
// Importa contexto para acesso à API e lista de heróis
import { useAppData } from '../context/AppDataContext';
// Importa componente de mini-gráfico (Sparkline)
import Sparkline from '../components/Sparkline';
// Importa ícones
import { ArrowDown, Trophy } from 'lucide-react';

// --- Componente HeroTop3 ---
const HeroTop3 = () => {
    // --- Hooks e Estado ---
    // Acessa a função de busca e a lista de heróis (para nomes e imagens) do contexto
    const { heroes, fetchAnalytics } = useAppData();
    // Estado para armazenar a lista dos top 3 heróis processados
    const [topHeroes, setTopHeroes] = useState([]);
    // Estado de carregamento
    const [loading, setLoading] = useState(true);

    // --- Efeito de Carga de Dados ---
    // Executa ao montar o componente ou quando a lista de heróis muda
    useEffect(() => {
        const loadTopHeroes = async () => {
            try {
                // 1. Busca os dados mais recentes de Win Rate (snapshot global)
                // Usa a view 'vw_hero_win_latest' para garantir apenas o último dado de cada herói
                const data = await fetchAnalytics({
                    table_name: 'vw_hero_win_latest',
                    limit: 100 // Busca o suficiente para cobrir todos os heróis
                });

                // Função auxiliar para tratar valores numéricos que podem vir como string do banco
                const parseValue = (val) => {
                    if (val === null || val === undefined) return 0;
                    if (typeof val === 'number') return val;
                    // Substitui vírgula por ponto se for string (formato PT-BR ou erro de banco)
                    if (typeof val === 'string') return parseFloat(val.replace(',', '.'));
                    return 0;
                };

                // 2. Ordena por Win Rate decrescente e pega os 3 primeiros
                const sorted = data.sort((a, b) => parseValue(b.win_rate) - parseValue(a.win_rate)).slice(0, 3);

                // 3. Busca Histórico para Sparklines
                // Extrai os IDs dos top 3 heróis
                const topHeroIds = sorted.map(h => h.hero_id);
                let historyData = [];

                // Se houver heróis selecionados, busca o histórico deles na tabela 'hero_win'
                if (topHeroIds.length > 0) {
                    historyData = await fetchAnalytics({
                        table_name: 'hero_win',
                        limit: 500, // Limite seguro para histórico de 3 heróis
                        filters_in: { hero_id: topHeroIds } // Filtra apenas pelos IDs dos vencedores
                    });
                }

                // 4. Enriquece os dados (Junta Snapshot + Histórico + Metadados)
                const enriched = sorted.map(item => {
                    // Encontra os metadados do herói (nome, role, imagem) na lista estática
                    const heroInfo = heroes.find(h => h.hero_id === item.hero_id);
                    const winRateVal = parseValue(item.win_rate);

                    // Filtra e ordena o histórico específico deste herói
                    const heroHistory = historyData
                        .filter(h => h.hero_id === item.hero_id)
                        .sort((a, b) => new Date(a.date_of_the_data) - new Date(b.date_of_the_data))
                        .map(h => ({ value: parseValue(h.win_rate) }));

                    // Retorna o objeto completo para renderização
                    return {
                        ...item,
                        hero_name: heroInfo?.hero_name || 'Unknown',
                        role_name: heroInfo?.role_name || 'Role',
                        win_rate: winRateVal,
                        // Se não tiver histórico (ex: herói novo), usa o valor atual como ponto único
                        trend: heroHistory.length > 0 ? heroHistory : [{ value: winRateVal }],
                        // Tenta usar imagem do contexto se disponível, senão null para fallback
                        image: heroInfo?.hero_icon_img_link || null
                    };
                });

                // Atualiza o estado com os dados finais
                setTopHeroes(enriched);
            } catch (error) {
                console.error("Erro ao carregar Top 3:", error);
            } finally {
                setLoading(false);
            }
        };

        // Só inicia a busca se já tivermos a lista de heróis carregada (para poder cruzar nomes/imagens)
        if (heroes.length > 0) {
            loadTopHeroes();
        }
    }, [heroes, fetchAnalytics]);

    // --- Handler de Scroll ---
    // Rola a página suavemente até a seção de análise principal
    const handleScrollToAnalysis = () => {
        const analysisSection = document.getElementById('analysis-section');
        if (analysisSection) {
            analysisSection.scrollIntoView({ behavior: 'smooth' });
        }
    };

    // --- Renderização: Estado de Loading (Skeleton) ---
    if (loading) {
        return (
            <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Renderiza 3 placeholders pulsantes */}
                    {[1, 2, 3].map(i => (
                        <div key={i} className="h-48 bg-gray-200 rounded-xl animate-pulse"></div>
                    ))}
                </div>
            </div>
        );
    }

    // --- Renderização: Estado Vazio (Sem Dados) ---
    if (topHeroes.length === 0) {
        return (
            <div className="w-full min-h-[50vh] flex flex-col items-center justify-center text-gray-500">
                <Trophy className="h-12 w-12 mb-4 text-gray-300" />
                <p className="text-lg font-medium">Ainda não há dados suficientes para o ranking.</p>
                <p className="text-sm">Verifique se o backend completou a carga de dados.</p>
            </div>
        );
    }

    return (
        <section className="relative min-h-[85vh] flex flex-col justify-center items-center bg-gray-50 px-6 pt-20 pb-10">
            {/* --- Background Decorativo --- */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                {/* Bolhas de cor desfocadas para dar um visual moderno */}
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-100/30 rounded-full blur-3xl" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-rose-100/30 rounded-full blur-3xl" />
            </div>

            <div className="relative z-10 w-full max-w-6xl text-center">
                {/* Título Principal */}
                <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4 tracking-tight">
                    Líderes de Vitória no Meta
                    <span className="block text-lg md:text-xl font-normal text-slate-500 mt-2">
                        Semana Atual • Competitivo Global
                    </span>
                </h1>

                {/* --- Grid de Cards dos Heróis --- */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 mb-16">
                    {topHeroes.map((hero, index) => (
                        <div
                            key={hero.hero_id || index}
                            className="group bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-100 flex flex-col items-center"
                        >
                            {/* Avatar do Herói com Medalha */}
                            <div className="relative mb-4">
                                <div className="w-20 h-20 rounded-full bg-gray-200 overflow-hidden ring-4 ring-gray-50 group-hover:ring-primary-50 transition-all">
                                    {/* Imagem ou Fallback (Inicial do nome) */}
                                    {hero.image ? (
                                        <img src={hero.image} alt={hero.hero_name} className="w-full h-full object-cover" />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center bg-slate-100 text-slate-400 font-bold text-xl">
                                            {hero.hero_name ? hero.hero_name[0] : '?'}
                                        </div>
                                    )}
                                </div>
                                {/* Medalha de Posicionamento (1º, 2º, 3º) */}
                                <div className="absolute -bottom-2 -right-2 bg-white rounded-full p-1 shadow-sm border border-gray-100">
                                    {index === 0 && <span className="text-xl">🥇</span>}
                                    {index === 1 && <span className="text-xl">🥈</span>}
                                    {index === 2 && <span className="text-xl">🥉</span>}
                                </div>
                            </div>

                            {/* Informações do Herói */}
                            <h3 className="text-lg font-semibold text-slate-900">{hero.hero_name}</h3>
                            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-4">{hero.role_name || hero.role || 'Função'}</span>

                            {/* Estatística Principal (Win Rate) */}
                            <div className="flex flex-col items-center mb-4">
                                <span className="text-4xl font-light text-slate-900 tracking-tighter">
                                    {hero.win_rate}%
                                </span>
                                <span className="text-xs font-medium text-primary-600 mt-1">
                                    Taxa de Vitória
                                </span>
                            </div>

                            {/* Mini Gráfico de Tendência (Sparkline) */}
                            <div className="w-full h-12 opacity-70 group-hover:opacity-100 transition-opacity">
                                <Sparkline data={hero.trend} color="#10b981" />
                            </div>
                        </div>
                    ))}
                </div>

                {/* --- Botão CTA (Call to Action) --- */}
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

// Exporta o componente
export default HeroTop3;
