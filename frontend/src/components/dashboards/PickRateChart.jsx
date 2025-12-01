/**
 * PickRateChart.jsx
 *
 * Componente de Gráfico de Linha para Taxa de Escolha (Pick Rate).
 * Responsável por processar dados brutos de pick rate e exibi-los graficamente.
 * Segue a mesma lógica de implementação do WinRateChart.
 */

// Importa componentes da biblioteca Recharts
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
// Importa utilitário de log
import ChartLogger from '../../utils/ChartLogger';

/**
 * Componente PickRateChart
 * 
 * @param {Array} data - Dados brutos da API (lista de registros de pick_rate)
 * @param {Array} heroes - Lista de metadados dos heróis (para resolver nomes via ID)
 */
const PickRateChart = ({ data, heroes }) => {
    // 1. Log de Recebimento
    ChartLogger.logReceive('PickRateChart', data);

    // Validação de dados vazios
    if (!data || data.length === 0) {
        ChartLogger.logRender('PickRateChart', 'RENDER_EMPTY', 'Dados nulos ou vazios.');
        return (
            <div className="h-full flex items-center justify-center bg-gray-50 rounded-xl border border-dashed border-gray-300">
                <p className="text-gray-500">Sem dados de Pick Rate para exibir.</p>
            </div>
        );
    }

    // Variáveis de estado local para renderização
    let chartData = [];
    let lines = [];

    try {
        // Identifica IDs únicos para determinar se é multi-linha
        const uniqueHeroIds = [...new Set(data.map(d => d.hero_id))].filter(id => id !== undefined && id !== null);
        const isMultiLine = uniqueHeroIds.length > 1;

        if (isMultiLine) {
            // --- Modo Multi-Linha ---

            // Agrupamento por data
            const groupedByDate = {};

            data.forEach(item => {
                const dateKey = item.date_of_the_data;
                if (!groupedByDate[dateKey]) {
                    groupedByDate[dateKey] = {
                        date_of_the_data: dateKey,
                        formattedDate: new Date(dateKey).toLocaleDateString()
                    };
                }

                // Tratamento numérico
                let val = item.pick_rate;
                if (typeof val === 'string') val = parseFloat(val.replace(',', '.'));
                if (isNaN(val)) val = 0;

                // Chave composta pelo ID do herói
                const dataKey = `hero_${item.hero_id}`;
                groupedByDate[dateKey][dataKey] = val;
            });

            // Ordenação cronológica
            chartData = Object.values(groupedByDate).sort((a, b) => new Date(a.date_of_the_data) - new Date(b.date_of_the_data));

            // Cores distintas para as linhas (mesma paleta do WinRate para consistência)
            const colors = ["#3b82f6", "#f97316", "#10b981", "#ef4444", "#8b5cf6", "#ec4899", "#f59e0b", "#6366f1"];

            // Mapeia os IDs para objetos de configuração de linha
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
            // --- Modo Linha Única ---

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

        ChartLogger.logProcess('PickRateChart', chartData);

    } catch (err) {
        // Tratamento de erro fatal no processamento
        console.error("Erro fatal ao formatar dados do gráfico:", err);
        ChartLogger.logRender('PickRateChart', 'RENDER_ERROR', err.message);
        return (
            <div className="h-full flex items-center justify-center bg-red-50 rounded-xl border border-red-200">
                <p className="text-red-500">Erro ao processar dados do gráfico.</p>
            </div>
        );
    }

    // Verificação pós-processamento
    if (chartData.length === 0) {
        ChartLogger.logRender('PickRateChart', 'RENDER_EMPTY', 'Nenhum dado válido após processamento.');
        return (
            <div className="h-full flex items-center justify-center bg-yellow-50 rounded-xl border border-yellow-200">
                <p className="text-yellow-600">Dados recebidos mas inválidos para exibição.</p>
            </div>
        );
    }

    ChartLogger.logRender('PickRateChart', 'RENDER_CHART', `Renderizando ${chartData.length} pontos com ${lines.length} linhas.`);

    return (
        <div className="w-full h-full">
            <ResponsiveContainer width="100%" height="100%" debounce={50}>
                <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                    <XAxis
                        dataKey="formattedDate"
                        tick={{ fontSize: 12, fill: '#9ca3af' }}
                        axisLine={false}
                        tickLine={false}
                    />
                    <YAxis
                        tick={{ fontSize: 12, fill: '#9ca3af' }}
                        axisLine={false}
                        tickLine={false}
                        unit="%"
                        domain={['auto', 'auto']}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                        itemStyle={{ color: '#1f2937' }}
                        itemSorter={(item) => -item.value}
                    />
                    {lines.length <= 12 && <Legend />}
                    {lines.map(line => (
                        <Line
                            key={line.dataKey}
                            type="monotone"
                            dataKey={line.dataKey}
                            name={line.name}
                            stroke={line.color}
                            strokeWidth={3}
                            dot={{ r: 4, fill: line.color, strokeWidth: 2, stroke: '#fff' }}
                            activeDot={{ r: 6 }}
                        />
                    ))}
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

// Exporta o componente
export default PickRateChart;
