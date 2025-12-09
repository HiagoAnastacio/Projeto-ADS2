/**
 * Sparkline.jsx
 *
 * Componente de Visualização de Dados (Micro-Chart).
 * Renderiza um gráfico de linha simplificado e compacto para exibir tendências
 * em espaços reduzidos, como cards ou células de tabela.
 */

// Importa componentes do Recharts para desenhar o gráfico
import { Line, LineChart, ResponsiveContainer, YAxis } from 'recharts';
// Importa logger (opcional, usado para debug se descomentado)
import ChartLogger from '../utils/ChartLogger';

/**
 * Sparkline Component
 * 
 * @param {Object[]} data - Array de objetos com a chave 'value'. Ex: [{ value: 10 }, { value: 20 }]
 * @param {string} color - Cor da linha (Hex ou nome). Default: #f97316 (Orange-500)
 */
const Sparkline = ({ data, color = "#f97316" }) => {
    // 1. Log de Recebimento (Opcional: pode ser muito verboso para sparklines, descomente se necessário)
    // ChartLogger.logReceive('Sparkline', data);

    // Validação de dados: Se vazio ou nulo, exibe um placeholder (skeleton)
    if (!data || data.length === 0) {
        // Retorna um retângulo cinza pulsante indicando carregamento
        return <div className="h-full w-full bg-gray-100 rounded animate-pulse" title="Carregando tendência..."></div>;
    }

    // Tratamento de dados para garantir que 'value' seja número
    const processedData = data.map(d => {
        let val = d.value;
        // Converte string numérica (ex: "10,5") para float (10.5)
        if (typeof val === 'string') {
            val = parseFloat(val.replace(',', '.'));
        }
        // Retorna 0 se não for um número válido
        return { ...d, value: isNaN(val) ? 0 : val };
    });

    return (
        // Container com altura fixa pequena (40px) para o efeito "sparkline"
        <div className="w-full min-w-0" style={{ height: 40 }}>
            {/* ResponsiveContainer ajusta o gráfico ao tamanho do pai */}
            <ResponsiveContainer width="99%" height="100%">
                <LineChart data={processedData}>
                    <YAxis domain={['dataMin', 'dataMax']} hide={true} />
                    <Line
                        type="monotone" // Suavização da linha
                        dataKey="value" // Chave dos dados a ser plotada
                        stroke={color}  // Cor da linha
                        strokeWidth={2} // Espessura da linha
                        dot={false}     // Remove os pontos para visual limpo
                        isAnimationActive={true} // Garante animação suave na entrada
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

// Exporta o componente Sparkline
export default Sparkline;
