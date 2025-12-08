/**
 * PickRateChart.jsx
 *
 * Componente de Visualização Gráfica: Taxa de Escolha (Pick Rate) ao Longo do Tempo.
 *
 * RAZÃO DE EXISTIR:
 * - Permitir a análise visual da popularidade de heróis (Meta Trends).
 * - Identificar picos de uso após patches ou mudanças de balanceamento.
 * - Funciona em paridade com o WinRateChart, compartilhando a lógica de interação.
 *
 * FLUXO DE DADOS:
 * 1. Recebe 'data' (lista de registros com data, hero_id, pick_rate).
 * 2. Processa os dados para agrupar por data (Pivot).
 * 3. Renderiza linhas com cores consistentes para cada herói.
 * 4. Implementa Highlight Sincronizado (via 'hoveredHero').
 */

import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import ChartLogger from '../../utils/ChartLogger';

/**
 * CustomTooltip
 * Exibe apenas o herói focado para reduzir ruído visual.
 */
const CustomTooltip = ({ active, payload, label, hoveredHero }) => {
    if (active && payload && payload.length) {
        const filteredPayload = hoveredHero
            ? payload.filter(item => item.name === hoveredHero)
            : payload;

        if (filteredPayload.length === 0) return null;

        return (
            <div className="bg-white p-3 border border-gray-200 shadow-lg rounded-lg outline-none">
                <p className="text-sm font-bold text-gray-700 mb-2">{label}</p>
                {filteredPayload.map((entry, index) => (
                    <p key={index} style={{ color: entry.color }} className="text-sm font-medium">
                        {entry.name}: {entry.value}%
                    </p>
                ))}
            </div>
        );
    }
    return null;
};

const PickRateChart = ({ data, heroes, hoveredHero, setHoveredHero }) => {
    const [isLegendHovered, setIsLegendHovered] = useState(false);

    ChartLogger.logReceive('PickRateChart', data);

    if (!data || data.length === 0) {
        return (
            <div className="h-full flex items-center justify-center bg-gray-50 rounded-xl border border-dashed border-gray-300">
                <p className="text-gray-500">Sem dados de Pick Rate para exibir.</p>
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
                let val = item.pick_rate;
                // Formatação local para float
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
                let val = item.pick_rate;
                if (typeof val === 'string') val = parseFloat(val.replace(',', '.'));
                return {
                    ...item,
                    formattedDate: !isNaN(dateObj.getTime()) ? dateObj.toLocaleDateString() : (item.date_of_the_data || 'N/A'),
                    pick_rate: isNaN(val) ? 0 : val
                };
            });
            lines = [{ dataKey: 'pick_rate', color: '#3b82f6', name: 'Pick Rate' }];
        }
    } catch (err) {
        console.error("Erro chart:", err);
        return <div className="h-full flex items-center justify-center bg-red-50 text-red-500">Erro ao processar gráfico.</div>;
    }

    if (chartData.length === 0) return <div className="h-full flex items-center justify-center bg-yellow-50 text-yellow-600">Dados inválidos.</div>;

    const renderLegendText = (value, entry) => {
        const isDimmed = hoveredHero && hoveredHero !== value;
        return <span style={{ color: '#374151', opacity: isDimmed ? 0.3 : 1, fontWeight: isDimmed ? 'normal' : 'bold' }}>{value}</span>;
    };

    return (
        <div className="w-full h-full">
            <ResponsiveContainer width="100%" height="100%" debounce={50}>
                <LineChart data={chartData} onMouseLeave={() => setHoveredHero && setHoveredHero(null)}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                    <XAxis dataKey="formattedDate" tick={{ fontSize: 12, fill: '#9ca3af' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 12, fill: '#9ca3af' }} axisLine={false} tickLine={false} unit="%" domain={['auto', 'auto']} />

                    <Tooltip content={<CustomTooltip hoveredHero={hoveredHero} />} />

                    {lines.length <= 40 && (
                        <Legend
                            onMouseEnter={(o) => { setIsLegendHovered(true); if (setHoveredHero) setHoveredHero(o.value); }}
                            onMouseLeave={() => { setIsLegendHovered(false); if (setHoveredHero) setHoveredHero(null); }}
                            wrapperStyle={{ paddingTop: '10px' }}
                            formatter={renderLegendText}
                        />
                    )}

                    {lines.map(line => {
                        const isDimmed = hoveredHero && hoveredHero !== line.name;
                        const opacity = isDimmed ? 0.1 : 1;
                        const strokeWidth = hoveredHero === line.name ? 4 : 3;

                        return (
                            <Line
                                key={line.dataKey}
                                type="monotone"
                                dataKey={line.dataKey}
                                name={line.name}
                                stroke={line.color}
                                strokeWidth={strokeWidth}
                                strokeOpacity={opacity}
                                dot={{ r: 4, fill: line.color, strokeWidth: 2, stroke: '#fff', strokeOpacity: opacity }}
                                activeDot={{ r: 6, strokeOpacity: 1 }}
                                onMouseEnter={() => setHoveredHero && setHoveredHero(line.name)}
                                onMouseLeave={() => setHoveredHero && setHoveredHero(null)}
                                isAnimationActive={false}
                            />
                        );
                    })}
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default PickRateChart;
