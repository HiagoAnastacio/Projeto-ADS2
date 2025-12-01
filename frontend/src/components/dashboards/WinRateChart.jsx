/**
 * WinRateChart.jsx
 *
 * Componente de Gráfico de Linha para Taxa de Vitória.
 *
 * RAZÃO DE EXISTIR:
 * - Visualizar graficamente a evolução do desempenho (Win Rate) dos heróis ao longo do tempo.
 * - Permitir a comparação visual entre múltiplos heróis (quando filtrado por função, por exemplo).
 * - Fornecer feedback visual imediato sobre tendências de meta.
 *
 * POSIÇÃO NO FLUXO DE DADOS:
 * 1. Recebe dados brutos (`data`) e metadados (`heroes`) do componente pai (`AnalysisSection`).
 * 2. Processa os dados brutos para o formato exigido pela biblioteca Recharts (pivoteamento por data).
 * 3. Define dinamicamente as cores e legendas das linhas baseando-se nos heróis presentes.
 * 4. Renderiza o gráfico interativo.
 */

// Importa componentes da biblioteca Recharts para construção do gráfico
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
// Importa utilitário de log para debug de dados do gráfico
import ChartLogger from '../../utils/ChartLogger';

/**
 * Componente WinRateChart
 * 
 * @param {Array} data - Dados brutos da API (lista de registros de win_rate)
 * @param {Array} heroes - Lista de metadados dos heróis (para resolver nomes via ID)
 */
const WinRateChart = ({ data, heroes }) => {
    // 1. Log de Recebimento dos dados para debug no console
    ChartLogger.logReceive('WinRateChart', data);

    // Validação inicial: Se não houver dados ou o array for vazio...
    if (!data || data.length === 0) {
        // ...loga o motivo da renderização vazia
        ChartLogger.logRender('WinRateChart', 'RENDER_EMPTY', 'Dados nulos ou vazios.');
        // ...e retorna um componente visual de "Sem Dados"
        return (
            <div className="h-full flex items-center justify-center bg-gray-50 rounded-xl border border-dashed border-gray-300">
                <p className="text-gray-500">Sem dados de Win Rate para exibir.</p>
            </div>
        );
    }

    // Variáveis para armazenar dados processados e configuração das linhas do gráfico
    let chartData = [];
    let lines = [];

    try {
        // --- Lógica de Detecção de Múltiplas Linhas ---
        // Cria um Set de IDs únicos presentes nos dados para saber quantos heróis distintos temos
        const uniqueHeroIds = [...new Set(data.map(d => d.hero_id))].filter(id => id !== undefined && id !== null);
        // Se houver mais de 1 ID único, estamos no modo multi-linha
        const isMultiLine = uniqueHeroIds.length > 1;

        if (isMultiLine) {
            // --- Lógica para Múltiplas Linhas (Vários Heróis) ---

            // Objeto auxiliar para agrupar valores por data (Pivot Table)
            // Estrutura: { '2023-01-01': { date: '...', hero_1: 50.5, hero_2: 48.0 } }
            const groupedByDate = {};

            // Itera sobre cada registro de dado bruto
            data.forEach(item => {
                const dateKey = item.date_of_the_data;

                // Se a data ainda não existe no agrupamento, inicializa o objeto da data
                if (!groupedByDate[dateKey]) {
                    groupedByDate[dateKey] = {
                        date_of_the_data: dateKey,
                        // Formata a data para exibição amigável no eixo X
                        formattedDate: new Date(dateKey).toLocaleDateString()
                    };
                }

                // Tratamento e conversão do valor numérico (garante que seja float)
                let val = item.win_rate;
                if (typeof val === 'string') val = parseFloat(val.replace(',', '.'));
                if (isNaN(val)) val = 0;

                // Define a chave dinâmica para o herói (ex: hero_1, hero_76) que será usada pelo Recharts
                const dataKey = `hero_${item.hero_id}`;
                // Atribui o valor ao herói naquela data específica
                groupedByDate[dateKey][dataKey] = val;
            });

            // Converte o objeto agrupado de volta para array e ordena cronologicamente
            chartData = Object.values(groupedByDate).sort((a, b) => new Date(a.date_of_the_data) - new Date(b.date_of_the_data));

            // Paleta de cores pré-definida para diferenciar as linhas dos heróis
            const colors = ["#f97316", "#3b82f6", "#10b981", "#ef4444", "#8b5cf6", "#ec4899", "#f59e0b", "#6366f1"];

            // Gera a configuração de cada linha (uma por herói identificado)
            lines = uniqueHeroIds.map((heroId, index) => {
                // Busca o nome do herói na lista de referência usando o ID
                const heroObj = heroes ? heroes.find(h => h.hero_id === heroId) : null;
                // Se não encontrar o nome, usa um fallback genérico
                const heroName = heroObj ? heroObj.hero_name : `Herói ${heroId}`;

                return {
                    dataKey: `hero_${heroId}`, // Chave que o Recharts buscará no objeto de dados
                    color: colors[index % colors.length], // Seleciona cor ciclicamente da paleta
                    name: heroName // Nome que aparecerá na legenda e tooltip
                };
            });

        } else {
            // --- Lógica para Linha Única (Um Herói ou Agregado Geral) ---

            // Mapeia diretamente os dados, apenas formatando a data e garantindo numéricos
            chartData = data.map(item => {
                const dateObj = new Date(item.date_of_the_data);
                let val = item.win_rate;

                // Conversão de string para float
                if (typeof val === 'string') val = parseFloat(val.replace(',', '.'));

                return {
                    ...item,
                    // Garante data válida ou N/A
                    formattedDate: !isNaN(dateObj.getTime()) ? dateObj.toLocaleDateString() : (item.date_of_the_data || 'N/A'),
                    win_rate: isNaN(val) ? 0 : val
                };
            });

            // Configuração de linha única fixa (cor laranja padrão para Win Rate)
            lines = [{ dataKey: 'win_rate', color: '#f97316', name: 'Win Rate' }];
        }

        // Loga o resultado do processamento para conferência
        ChartLogger.logProcess('WinRateChart', chartData);

    } catch (err) {
        // Captura erros de processamento para não quebrar a UI inteira (Error Boundary local)
        console.error("Erro fatal ao formatar dados do gráfico:", err);
        ChartLogger.logRender('WinRateChart', 'RENDER_ERROR', err.message);
        // Retorna componente de erro visual
        return (
            <div className="h-full flex items-center justify-center bg-red-50 rounded-xl border border-red-200">
                <p className="text-red-500">Erro ao processar dados do gráfico.</p>
            </div>
        );
    }

    // Verificação final: se após processamento não sobrou nenhum dado válido...
    if (chartData.length === 0) {
        ChartLogger.logRender('WinRateChart', 'RENDER_EMPTY', 'Nenhum dado válido após processamento.');
        return (
            <div className="h-full flex items-center justify-center bg-yellow-50 rounded-xl border border-yellow-200">
                <p className="text-yellow-600">Dados recebidos mas inválidos para exibição.</p>
            </div>
        );
    }

    // Loga sucesso na renderização
    ChartLogger.logRender('WinRateChart', 'RENDER_CHART', `Renderizando ${chartData.length} pontos com ${lines.length} linhas.`);

    // --- Renderização do Gráfico ---
    return (
        <div className="w-full h-full">
            {/* Container Responsivo que se adapta ao tamanho do pai */}
            <ResponsiveContainer width="100%" height="100%" debounce={50}>
                <LineChart data={chartData}>
                    {/* Grade de fundo pontilhada para facilitar leitura */}
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
                        unit="%" // Adiciona símbolo de %
                        domain={['auto', 'auto']} // Ajuste automático da escala vertical
                    />

                    {/* Tooltip interativo ao passar o mouse */}
                    <Tooltip
                        contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                        itemStyle={{ color: '#1f2937' }}
                        itemSorter={(item) => -item.value} // Ordena tooltip do maior para o menor valor
                    />

                    {/* Legenda das linhas (Oculta se houver muitas linhas para evitar poluição visual) */}
                    {lines.length <= 12 && <Legend />}

                    {/* Renderização dinâmica das linhas baseada na configuração gerada (lines) */}
                    {lines.map(line => (
                        <Line
                            key={line.dataKey}
                            type="monotone" // Suavização da curva
                            dataKey={line.dataKey}
                            name={line.name}
                            stroke={line.color}
                            strokeWidth={3}
                            dot={{ r: 4, fill: line.color, strokeWidth: 2, stroke: '#fff' }} // Pontos nos dados
                            activeDot={{ r: 6 }} // Destaque ao passar o mouse
                        />
                    ))}
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

// Exporta o componente para uso na AnalysisSection
export default WinRateChart;
