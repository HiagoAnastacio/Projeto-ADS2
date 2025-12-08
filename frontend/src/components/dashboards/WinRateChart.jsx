/**
 * WinRateChart.jsx
 *
 * Componente de Visualização Gráfica: Taxa de Vitória (Win Rate) ao Longo do Tempo.
 *
 * RAZÃO DE EXISTIR:
 * - Permitir a análise visual de tendências de balanceamento (Buffs/Nerfs impactando win rate).
 * - Comparar a performance de um ou múltiplos heróis lado-a-lado.
 * - Oferecer interatividade avançada (Highlight, Tooltip Focado) para facilitar a leitura.
 *
 * FLUXO DE DADOS:
 * 1. Recebe 'data' (lista de registros com data, hero_id, win_rate).
 * 2. Processa os dados para o formato do Recharts (Agrupamento por Data).
 * 3. Se múltiplos heróis, gera uma linha para cada um com cor distinta.
 * 4. Implementa lógica de 'hoveredHero' para destacar a linha focada e diminuir a opacidade das outras.
 * 5. Renderiza a Legenda e Tooltip com comportamento condicional (Foco vs Visão Geral).
 */

import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import ChartLogger from '../../utils/ChartLogger';

/**
 * CustomTooltip
 * 
 * Componente de Tooltip personalizado para o Recharts.
 * LÓGICA: Se houver um 'hoveredHero' ativo, filtra a lista para mostrar APENAS aquele herói.
 * Isso limpa a poluição visual quando o usuário está focado em um dado específico.
 */
const CustomTooltip = ({ active, payload, label, hoveredHero }) => {
    if (active && payload && payload.length) {
        // Filtragem Inteligente do Payload
        const filteredPayload = hoveredHero
            ? payload.filter(item => item.name === hoveredHero)
            : payload;

        if (filteredPayload.length === 0) return null;

        return (
            <div className="bg-white p-3 border border-gray-200 shadow-lg rounded-lg outline-none">
                <p className="text-sm font-bold text-gray-700 mb-2">{label}</p>
                {filteredPayload.map((entry, index) => (
                    <p key={index} style={{ color: entry.color }} className="text-sm font-medium">
                        {/* Exibe Nome e Valor formatado */}
                        {entry.name}: {entry.value}%
                    </p>
                ))}
            </div>
        );
    }
    return null;
};

const WinRateChart = ({ data, heroes, hoveredHero, setHoveredHero }) => {
    // Estado local para controlar se o mouse está sobre a LEGENDA (evita loops de estado)
    const [isLegendHovered, setIsLegendHovered] = useState(false);

    // Logging para debug de dados recebidos
    ChartLogger.logReceive('WinRateChart', data);

    // Fallback para ausência de dados
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
        // --- Processamento de Dados ---
        // Identifica IDs únicos de heróis presentes nos dados
        const uniqueHeroIds = [...new Set(data.map(d => d.hero_id))].filter(id => id !== undefined && id !== null);
        const isMultiLine = uniqueHeroIds.length > 1;

        if (isMultiLine) {
            // MODO MÚLTIPLAS LINHAS: Pivoteamento dos dados por Data
            const groupedByDate = {};
            data.forEach(item => {
                const dateKey = item.date_of_the_data;
                if (!groupedByDate[dateKey]) {
                    groupedByDate[dateKey] = {
                        date_of_the_data: dateKey,
                        formattedDate: new Date(dateKey).toLocaleDateString()
                    };
                }
                // Tratamento numérico (converte string locale para float)
                let val = item.win_rate;
                if (typeof val === 'string') val = parseFloat(val.replace(',', '.'));
                if (isNaN(val)) val = 0;

                // Chave dinâmica para o Recharts (ex: hero_1, hero_76)
                groupedByDate[dateKey][`hero_${item.hero_id}`] = val;
            });

            // Ordenação Cronológica
            chartData = Object.values(groupedByDate).sort((a, b) => new Date(a.date_of_the_data) - new Date(b.date_of_the_data));

            // Paleta de cores rotativa
            const colors = ["#f97316", "#3b82f6", "#10b981", "#ef4444", "#8b5cf6", "#ec4899", "#f59e0b", "#6366f1"];

            // Gera configuração das linhas
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
            // MODO LINHA ÚNICA: Mapeamento direto
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

    // --- Formatter da Legenda (Dimming Text) ---
    // Aplica opacidade ao texto da legenda para itens não focados
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

                    {/* Tooltip controla o que é exibido ao passar o mouse no gráfico */}
                    <Tooltip content={<CustomTooltip hoveredHero={hoveredHero} />} />

                    {/* Legenda interativa com suporte a Dimming */}
                    {lines.length <= 40 && (
                        <Legend
                            onMouseEnter={(o) => { setIsLegendHovered(true); if (setHoveredHero) setHoveredHero(o.value); }}
                            onMouseLeave={() => { setIsLegendHovered(false); if (setHoveredHero) setHoveredHero(null); }}
                            wrapperStyle={{ paddingTop: '10px' }}
                            formatter={renderLegendText}
                        />
                    )}

                    {/* Mapeamento das Linhas do Gráfico */}
                    {lines.map(line => {
                        // Lógica de Estilo Dinâmico (Highlight/Dimming)
                        const isDimmed = hoveredHero && hoveredHero !== line.name;
                        const opacity = isDimmed ? 0.1 : 1; // 10% opacidade se não focado
                        const strokeWidth = hoveredHero === line.name ? 4 : 3; // Mais grosso se focado

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
                                // Eventos para ativar o Highlight no hover da linha
                                onMouseEnter={() => setHoveredHero && setHoveredHero(line.name)}
                                onMouseLeave={() => setHoveredHero && setHoveredHero(null)}
                                isAnimationActive={false} // Desativa animação de entrada para resposta mais rápida no highlight
                            />
                        );
                    })}
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default WinRateChart;
