import React from 'react';
import { ArrowDown, TrendingUp, TrendingDown } from 'lucide-react';
import Sparkline from '../components/Sparkline';

const HeroTop3 = () => {
    // Mock Data (Substituir por API real depois)
    const topHeroes = [
        {
            id: 1,
            name: 'Sojourn',
            role: 'Damage',
            winRate: 54.2,
            trend: [45, 48, 52, 51, 54, 53, 54.2],
            image: 'https://d15f34w2p97es5.cloudfront.net/avatars/sojourn.png' // Placeholder
        },
        {
            id: 2,
            name: 'Kiriko',
            role: 'Support',
            winRate: 52.8,
            trend: [50, 51, 51, 52, 52.5, 53, 52.8],
            image: 'https://d15f34w2p97es5.cloudfront.net/avatars/kiriko.png'
        },
        {
            id: 3,
            name: 'Junker Queen',
            role: 'Tank',
            winRate: 51.5,
            trend: [48, 49, 48, 50, 51, 51.2, 51.5],
            image: 'https://d15f34w2p97es5.cloudfront.net/avatars/junker-queen.png'
        }
    ];

    const handleScrollToAnalysis = () => {
        const analysisSection = document.getElementById('analysis');
        if (analysisSection) {
            analysisSection.scrollIntoView({ behavior: 'smooth' });
        }
    };

    return (
        <section className="relative min-h-[85vh] flex flex-col justify-center items-center bg-gray-50 px-6 pt-20 pb-10">
            {/* Background Decorativo (Sutil) */}
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
                            key={hero.id}
                            className="group bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-100 flex flex-col items-center"
                        >
                            <div className="relative mb-4">
                                <div className="w-20 h-20 rounded-full bg-gray-200 overflow-hidden ring-4 ring-gray-50 group-hover:ring-emerald-50 transition-all">
                                    {/* Fallback para imagem se não carregar */}
                                    <div className="w-full h-full flex items-center justify-center bg-slate-100 text-slate-400 font-bold text-xl">
                                        {hero.name[0]}
                                    </div>
                                    {/* <img src={hero.image} alt={hero.name} className="w-full h-full object-cover" /> */}
                                </div>
                                <div className="absolute -bottom-2 -right-2 bg-white rounded-full p-1 shadow-sm border border-gray-100">
                                    {index === 0 && <span className="text-xl">🥇</span>}
                                    {index === 1 && <span className="text-xl">🥈</span>}
                                    {index === 2 && <span className="text-xl">🥉</span>}
                                </div>
                            </div>

                            <h3 className="text-lg font-semibold text-slate-900">{hero.name}</h3>
                            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-4">{hero.role}</span>

                            <div className="flex items-end gap-2 mb-4">
                                <span className="text-4xl font-light text-slate-900 tracking-tighter">
                                    {hero.winRate}%
                                </span>
                                <span className="flex items-center text-emerald-600 text-sm font-medium mb-1">
                                    <TrendingUp size={16} className="mr-1" />
                                    +1.2%
                                </span>
                            </div>

                            <div className="w-full h-12 opacity-70 group-hover:opacity-100 transition-opacity">
                                <Sparkline data={hero.trend.map(v => ({ value: v }))} color="#10b981" />
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
