/**
 * WinRateChart.jsx
 *
 * Componente de Gráfico de Linha para Taxa de Vitória.
 *
 * REVISÃO FASE 2.4 (Highlight & Dimming):
 * - Adicionado suporte a `hoveredHero` para Highlight sincronizado.
 * - Efeito de "Dimming": Reduz opacidade de linhas não selecionadas.
 * - Interatividade na Legenda.
 */

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import ChartLogger from '../../utils/ChartLogger';

const WinRateChart = ({ data, heroes, hoveredHero, setHoveredHero }) => {
    ChartLogger.logReceive('WinRateChart', data);

    if (!data || data.length === 0) {
        return (
            <div className="h-full flex items-center justify-center bg-gray-50 rounded-xl border border-dashed border-gray-300">
                <p className="text-gray-500">Sem dados de Win Rate para exibir.</p>
            </div>
        );
    }

    let chartData = [];
    let lines = [];

    try {
        const uniqueHeroIds = [...new Set(data.map(d => d.hero_id))].filter(id => id !== undefined && id !== null);
        const isMultiLine = uniqueHeroIds.length > 1;

        if (isMultiLine) {
            const groupedByDate = {};
            data.forEach(item => {
                const dateKey = item.date_of_the_data;
                if (!groupedByDate[dateKey]) {
                    groupedByDate[dateKey] = {
                        date_of_the_data: dateKey,
                        formattedDate: new Date(dateKey).toLocaleDateString()
                    };
                }
                let val = item.win_rate;
                if (typeof val === 'string') val = parseFloat(val.replace(',', '.'));
                if (isNaN(val)) val = 0;
                groupedByDate[dateKey][`hero_${item.hero_id}`] = val;
            });

            chartData = Object.values(groupedByDate).sort((a, b) => new Date(a.date_of_the_data) - new Date(b.date_of_the_data));
            const colors = ["#f97316", "#3b82f6", "#10b981", "#ef4444", "#8b5cf6", "#ec4899", "#f59e0b", "#6366f1"];

            lines = uniqueHeroIds.map((heroId, index) => {
                const heroObj = heroes ? heroes.find(h => h.hero_id === heroId) : null;
                const heroName = heroObj ? heroObj.hero_name : `Herói ${heroId}`;
                return {
                    dataKey: `hero_${heroId}`,
                    color: colors[index % colors.length],
                    name: heroName
                };
            });
        } else {
            chartData = data.map(item => {
                const dateObj = new Date(item.date_of_the_data);
                let val = item.win_rate;
                if (typeof val === 'string') val = parseFloat(val.replace(',', '.'));
                return {
                    ...item,
                    formattedDate: !isNaN(dateObj.getTime()) ? dateObj.toLocaleDateString() : (item.date_of_the_data || 'N/A'),
                    win_rate: isNaN(val) ? 0 : val
                };
            });
            lines = [{ dataKey: 'win_rate', color: '#f97316', name: 'Win Rate' }];
        }
    } catch (err) {
        console.error("Erro chart:", err);
        return <div className="h-full flex items-center justify-center bg-red-50 text-red-500">Erro ao processar gráfico.</div>;
    }

    if (chartData.length === 0) return <div className="h-full flex items-center justify-center bg-yellow-50 text-yellow-600">Dados inválidos.</div>;

    // Handler de Mouse
    const handleMouseEnter = (o) => {
        const { name } = o; // name vem do payload da legenda ou tooltip
        if (setHoveredHero) setHoveredHero(name);
    };
    const handleMouseLeave = () => {
        if (setHoveredHero) setHoveredHero(null);
    };

    return (
        <div className="w-full h-full">
            <ResponsiveContainer width="100%" height="100%" debounce={50}>
                <LineChart data={chartData} onMouseLeave={handleMouseLeave}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                    <XAxis dataKey="formattedDate" tick={{ fontSize: 12, fill: '#9ca3af' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 12, fill: '#9ca3af' }} axisLine={false} tickLine={false} unit="%" domain={['auto', 'auto']} />

                    <Tooltip
                        contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                        itemSorter={(item) => -item.value}
                    />

                    {/* 
                       Legenda Sempre Visível (Até 40 itens) para garantir consistência e interatividade de Highlight.
                       Adiciona interatividade: Ao passar o mouse na legenda, destaca a linha.
                    */}
                    {lines.length <= 40 && (
                        <Legend
                            onMouseEnter={handleMouseEnter}
                            onMouseLeave={handleMouseLeave}
                            wrapperStyle={{ paddingTop: '10px' }}
                        />
                    )}

                    {lines.map(line => {
                        // Lógica de Opacidade:
                        // Se hoveredHero existe e NÃO é desta linha -> Opacidade 0.1 (Dimmed)
                        // Caso contrário -> Opacidade 1.0 (Normal)
                        const isDimmed = hoveredHero && hoveredHero !== line.name;
                        const opacity = isDimmed ? 0.1 : 1;
                        const strokeWidth = hoveredHero === line.name ? 4 : 3; // Linha mais grossa se focado

                        return (
                            <Line
                                key={line.dataKey}
                                type="monotone"
                                dataKey={line.dataKey}
                                name={line.name} // IMPORTANTE: name deve bater com hoveredHero
                                stroke={line.color}
                                strokeWidth={strokeWidth}
                                strokeOpacity={opacity}
                                dot={{ r: 4, fill: line.color, strokeWidth: 2, stroke: '#fff', strokeOpacity: opacity }}
                                activeDot={{ r: 6, strokeOpacity: 1 }}
                                onMouseEnter={(e) => {
                                    // e é o evento nativo, mas podemos disparar o set diretamente
                                    if (setHoveredHero) setHoveredHero(line.name);
                                }}
                                onMouseLeave={() => {
                                    if (setHoveredHero) setHoveredHero(null);
                                }}
                                isAnimationActive={false} // Melhora a resposta visual do highlight
                            />
                        );
                    })}
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default WinRateChart;
