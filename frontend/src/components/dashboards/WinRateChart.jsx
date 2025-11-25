/**
 * WinRateChart.jsx
 *
 * Componente de Gráfico de Linha para Taxa de Vitória.
 * Responsável por processar dados brutos de win rate e exibi-los graficamente.
 * Suporta visualização multi-linhas (vários heróis) ou linha única (agregado).
 */

// Importa componentes da biblioteca Recharts para construção do gráfico
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
// Importa utilitário de log para debug
import ChartLogger from '../../utils/ChartLogger';

/**
 * Componente WinRateChart
 * 
 * @param {Array} data - Dados brutos da API (lista de registros de win_rate)
 * @param {Array} heroes - Lista de metadados dos heróis (para resolver nomes via ID)
 */
const WinRateChart = ({ data, heroes }) => {
    // 1. Log de Recebimento dos dados para debug
    ChartLogger.logReceive('WinRateChart', data);

    // Validação inicial: Se não houver dados, exibe mensagem de estado vazio
    if (!data || data.length === 0) {
        ChartLogger.logRender('WinRateChart', 'RENDER_EMPTY', 'Dados nulos ou vazios.');
        return (
            <div className="h-80 flex items-center justify-center bg-gray-50 rounded-xl border border-dashed border-gray-300">
                <p className="text-gray-500">Sem dados de Win Rate para exibir.</p>
            </div>
        );
    }

    // Variáveis para armazenar dados processados e configuração das linhas
    let chartData = [];
    let lines = [];

    try {
        // Verifica se o dataset contém múltiplos heróis distintos
        // Cria um Set de IDs únicos para contar quantos heróis existem nos dados
        const uniqueHeroIds = [...new Set(data.map(d => d.hero_id))].filter(id => id !== undefined && id !== null);
        const isMultiLine = uniqueHeroIds.length > 1;

        if (isMultiLine) {
            // --- Lógica para Múltiplas Linhas (Vários Heróis) ---

            // Objeto auxiliar para agrupar valores por data
            const groupedByDate = {};

            // Itera sobre os dados brutos para pivotar (transformar linhas em colunas por herói)
            data.forEach(item => {
                const dateKey = item.date_of_the_data;

                // Se a data ainda não existe no agrupamento, inicializa o objeto da data
                if (!groupedByDate[dateKey]) {
                    groupedByDate[dateKey] = {
                        date_of_the_data: dateKey,
                        formattedDate: new Date(dateKey).toLocaleDateString() // Formata data para exibição no eixo X
                    };
                }

                // Tratamento e conversão do valor numérico
                let val = item.win_rate;
                if (typeof val === 'string') val = parseFloat(val.replace(',', '.'));
                if (isNaN(val)) val = 0;

                // Define a chave dinâmica para o herói (ex: hero_1, hero_76)
                const dataKey = `hero_${item.hero_id}`;
                // Atribui o valor ao herói naquela data
                groupedByDate[dateKey][dataKey] = val;
            });

            // Converte o objeto agrupado de volta para array e ordena cronologicamente
            chartData = Object.values(groupedByDate).sort((a, b) => new Date(a.date_of_the_data) - new Date(b.date_of_the_data));

            // Paleta de cores para diferenciar as linhas
            const colors = ["#f97316", "#3b82f6", "#10b981", "#ef4444", "#8b5cf6", "#ec4899", "#f59e0b", "#6366f1"];

            // Gera a configuração de cada linha (uma por herói)
            lines = uniqueHeroIds.map((heroId, index) => {
                // Busca o nome do herói na lista de referência usando o ID
                const heroObj = heroes ? heroes.find(h => h.hero_id === heroId) : null;
                const heroName = heroObj ? heroObj.hero_name : `Herói ${heroId}`;

                return {
                    dataKey: `hero_${heroId}`, // Chave que o Recharts buscará no objeto de dados
                    color: colors[index % colors.length], // Cor cíclica
                    name: heroName // Nome para a legenda e tooltip
                };
            });

        } else {
            // --- Lógica para Linha Única (Um Herói ou Agregado) ---

            chartData = data.map(item => {
                const dateObj = new Date(item.date_of_the_data);
                let val = item.win_rate;

                // Conversão de string para float
                if (typeof val === 'string') val = parseFloat(val.replace(',', '.'));

                return {
                    ...item,
                    formattedDate: !isNaN(dateObj.getTime()) ? dateObj.toLocaleDateString() : (item.date_of_the_data || 'N/A'),
                    win_rate: isNaN(val) ? 0 : val
                };
            });

            // Configuração de linha única fixa
            lines = [{ dataKey: 'win_rate', color: '#f97316', name: 'Win Rate' }];
        }

        // Loga o resultado do processamento
        ChartLogger.logProcess('WinRateChart', chartData);

    } catch (err) {
        // Captura erros de processamento para não quebrar a UI
        console.error("Erro fatal ao formatar dados do gráfico:", err);
        ChartLogger.logRender('WinRateChart', 'RENDER_ERROR', err.message);
        return (
            <div className="h-80 flex items-center justify-center bg-red-50 rounded-xl border border-red-200">
                <p className="text-red-500">Erro ao processar dados do gráfico.</p>
            </div>
        );
    }

    // Verificação final se após processamento sobrou algum dado
    if (chartData.length === 0) {
        ChartLogger.logRender('WinRateChart', 'RENDER_EMPTY', 'Nenhum dado válido após processamento.');
        return (
            <div className="h-80 flex items-center justify-center bg-yellow-50 rounded-xl border border-yellow-200">
                <p className="text-yellow-600">Dados recebidos mas inválidos para exibição.</p>
            </div>
        );
    }

    // Loga sucesso na renderização
    ChartLogger.logRender('WinRateChart', 'RENDER_CHART', `Renderizando ${chartData.length} pontos com ${lines.length} linhas.`);

    return (
        // Card container do gráfico
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 min-w-0">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Evolução da Taxa de Vitória (Win Rate)</h3>
            <div style={{ width: '100%', height: 320 }}>
                {/* ResponsiveContainer ajusta o gráfico ao tamanho do pai */}
                <ResponsiveContainer width="99%" height="100%" debounce={50}>
                    <LineChart data={chartData}>
                        {/* Grade de fundo pontilhada */}
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />

                        {/* Eixo X (Datas) */}
                        <XAxis
                            dataKey="formattedDate"
                            tick={{ fontSize: 12, fill: '#9ca3af' }}
                            axisLine={false}
                            tickLine={false}
                        />

                        {/* Eixo Y (Porcentagem) */}
                        <YAxis
                            tick={{ fontSize: 12, fill: '#9ca3af' }}
                            axisLine={false}
                            tickLine={false}
                            unit="%"
                            domain={['auto', 'auto']} // Ajuste automático da escala
                        />

                        {/* Tooltip interativo ao passar o mouse */}
                        <Tooltip
                            contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                            itemStyle={{ color: '#1f2937' }}
                        />

                        {/* Legenda das linhas */}
                        <Legend />

                        {/* Renderização dinâmica das linhas baseada na configuração gerada */}
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
        </div>
    );
};

// Exporta o componente
export default WinRateChart;
