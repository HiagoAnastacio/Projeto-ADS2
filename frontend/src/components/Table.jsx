/**
 * Table.jsx
 *
 * Componente de Tabela Genérica e Dinâmica.
 * Renderiza uma tabela HTML baseada em um array de objetos JSON.
 * As colunas são geradas automaticamente a partir das chaves do primeiro objeto.
 */

const Table = ({ data }) => {
    // Verifica se há dados para exibir
    if (!data || data.length === 0) {
        // Exibe mensagem amigável se não houver dados
        return (
            <div className="text-center py-10 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                <p className="text-gray-500">Nenhum dado disponível para os filtros selecionados.</p>
            </div>
        );
    }

    // Extrai as chaves do primeiro objeto para criar o cabeçalho dinamicamente
    // Isso permite que a tabela se adapte a qualquer estrutura de dados passada
    const columns = Object.keys(data[0]);

    return (
        // Container com overflow-x para permitir rolagem horizontal em telas pequenas
        <div className="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
            <table className="min-w-full divide-y divide-gray-300">
                {/* Cabeçalho da Tabela */}
                <thead className="bg-gray-50">
                    <tr>
                        {columns.map((col) => (
                            <th
                                key={col}
                                scope="col"
                                // Estilização do cabeçalho: uppercase, negrito, espaçamento
                                className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6 uppercase tracking-wider"
                            >
                                {/* Substitui underscores por espaços para melhor legibilidade (ex: hero_name -> HERO NAME) */}
                                {col.replace(/_/g, ' ')}
                            </th>
                        ))}
                    </tr>
                </thead>
                {/* Corpo da Tabela */}
                <tbody className="divide-y divide-gray-200 bg-white">
                    {data.map((row, rowIndex) => (
                        // Alterna a cor de fundo das linhas (zebra striping)
                        <tr key={rowIndex} className={rowIndex % 2 === 0 ? undefined : 'bg-gray-50'}>
                            {columns.map((col) => (
                                <td
                                    key={`${rowIndex}-${col}`}
                                    className="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-500 sm:pl-6"
                                >
                                    {/* Lógica de Formatação de Célula */}
                                    {/* Se a coluna tem 'date' no nome, formata como data */}
                                    {col.includes('date')
                                        ? new Date(row[col]).toLocaleDateString()
                                        // Se for número, formata com locale (ex: 1.000,00)
                                        : typeof row[col] === 'number'
                                            ? row[col].toLocaleString(undefined, { maximumFractionDigits: 2 })
                                            // Caso contrário, exibe o valor bruto
                                            : row[col]}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

// Exporta o componente Table
export default Table;
