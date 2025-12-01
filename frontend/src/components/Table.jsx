import React, { memo } from 'react';

const Table = memo(({ data }) => {
    if (!data || data.length === 0) {
        return (
            <div className="text-center py-20 bg-gray-50/50 rounded-xl border border-dashed border-gray-200">
                <p className="text-slate-400 font-light text-lg">Nenhum dado encontrado para esta análise.</p>
            </div>
        );
    }

    const columns = Object.keys(data[0]);

    // Função auxiliar para renderizar células com formatação especial
    const renderCell = (col, value, row) => {
        // 1. Coluna de Herói com Avatar
        if (col === 'Herói') {
            return (
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-500 ring-2 ring-white">
                        {value[0]}
                    </div>
                    <span className="font-medium text-slate-900">{value}</span>
                </div>
            );
        }

        // 2. Coluna de Win Rate com Badges
        if (col === 'Win Rate (%)') {
            const numValue = parseFloat(value);
            let badgeColor = "bg-slate-100 text-slate-600"; // Neutro

            if (numValue >= 52) badgeColor = "bg-emerald-100 text-emerald-700"; // Positivo
            if (numValue <= 48) badgeColor = "bg-rose-100 text-rose-700"; // Negativo

            return (
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badgeColor}`}>
                    {numValue.toFixed(2)}%
                </span>
            );
        }

        // 3. Formatação Padrão
        if (typeof value === 'number') {
            return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
        }
        return value;
    };

    return (
        <div className="overflow-hidden shadow-sm ring-1 ring-black ring-opacity-5 rounded-xl bg-white">
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-100">
                    <thead className="bg-gray-50/50">
                        <tr>
                            {columns.map((col) => (
                                <th
                                    key={col}
                                    scope="col"
                                    className="py-4 pl-6 pr-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider"
                                >
                                    {col}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50 bg-white">
                        {data.map((row, rowIndex) => (
                            <tr
                                key={rowIndex}
                                className="hover:bg-gray-50/80 transition-colors duration-150"
                            >
                                {columns.map((col) => (
                                    <td
                                        key={`${rowIndex}-${col}`}
                                        className="whitespace-nowrap py-4 pl-6 pr-3 text-sm text-slate-600"
                                    >
                                        {renderCell(col, row[col], row)}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
});

export default Table;
