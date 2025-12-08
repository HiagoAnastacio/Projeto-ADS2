import React, { memo, useState, useMemo } from 'react';
import { ArrowUp, ArrowDown, ArrowUpDown } from 'lucide-react';

/**
 * Table.jsx
 * 
 * Componente de Tabela com:
 * - Ordenação Inteligente: Ao ordenar por métrica, reordena os PATches (Grupos) baseados no valor MÁXIMO daquela métrica no grupo.
 * - Suporte a Data BR (DD/MM/YYYY).
 * - Estilização aprimorada.
 */

const Table = memo(({ data }) => {
    // Padrão: Ordenar por 'Data' de forma Decrescente ('desc')
    const [sortConfig, setSortConfig] = useState({ key: 'Data', direction: 'desc' });

    // --- Helper: Parse Data BR ---
    // (Definido antes de uso no useMemo)
    const parseDate = (dateStr, rawDate) => {
        if (rawDate) return new Date(rawDate).getTime();
        // Fallback para DD/MM/YYYY
        if (typeof dateStr === 'string' && dateStr.includes('/')) {
            const [day, month, year] = dateStr.split('/');
            return new Date(`${year}-${month}-${day}`).getTime();
        }
        return 0;
    };

    // --- Helper: Parse Número ---
    const parseNum = (val) => {
        if (typeof val === 'number') return val;
        if (typeof val === 'string') return parseFloat(val.replace(',', '.').replace('%', ''));
        return 0;
    };

    const groupedAndSortedData = useMemo(() => {
        if (!data || data.length === 0) return [];

        // 1. Agrupar
        const groups = {};
        data.forEach(item => {
            const dateKey = item['Data'];
            if (!groups[dateKey]) {
                groups[dateKey] = {
                    dateLabel: dateKey,
                    timestamp: parseDate(dateKey, item._raw_date),
                    items: []
                };
            }
            groups[dateKey].items.push(item);
        });

        // 2. Ordenar os GRUPOS
        const sortedGroups = Object.values(groups).sort((groupA, groupB) => {
            // Se ordenar por DATA
            if (sortConfig.key === 'Data') {
                return sortConfig.direction === 'asc'
                    ? groupA.timestamp - groupB.timestamp
                    : groupB.timestamp - groupA.timestamp;
            }

            // Se ordenar por Métrica (Win Rate / Pick Rate)
            const maxValA = Math.max(...groupA.items.map(i => parseNum(i[sortConfig.key])));
            const maxValB = Math.max(...groupB.items.map(i => parseNum(i[sortConfig.key])));

            return sortConfig.direction === 'asc' ? maxValA - maxValB : maxValB - maxValA;
        });

        // 3. Ordenar ITENS dentro dos grupos
        sortedGroups.forEach(group => {
            group.items.sort((a, b) => {
                const key = sortConfig.key === 'Data' ? 'Win Rate (%)' : sortConfig.key;
                const dir = sortConfig.key === 'Data' ? 'desc' : sortConfig.direction;

                const valA = parseNum(a[key]);
                const valB = parseNum(b[key]);

                return dir === 'asc' ? valA - valB : valB - valA;
            });
        });

        return sortedGroups;
    }, [data, sortConfig]);

    // Handle Empty State no Render
    if (!data || data.length === 0 || !data[0]) {
        return (
            <div className="text-center py-20 bg-gray-50/50 rounded-xl border border-dashed border-gray-200 shadow-sm">
                <p className="text-slate-400 font-light text-lg">Nenhum dado encontrado para esta análise.</p>
            </div>
        );
    }

    const columns = Object.keys(data[0]).filter(col => !col.startsWith('_'));
    const sortableColumns = ['Data', 'Win Rate (%)', 'Pick Rate (%)'];

    const handleSort = (key) => {
        if (!sortableColumns.includes(key)) return;
        setSortConfig(prev => {
            if (prev.key === key) {
                return { key, direction: prev.direction === 'asc' ? 'desc' : 'asc' };
            }
            return { key, direction: 'desc' };
        });
    };

    const getSortIcon = (colName) => {
        if (!sortableColumns.includes(colName)) return null;
        if (sortConfig.key !== colName) return <ArrowUpDown className="w-4 h-4 text-slate-300 ml-1 inline-block opacity-50 group-hover:opacity-100" />;
        return sortConfig.direction === 'asc'
            ? <ArrowUp className="w-4 h-4 text-orange-500 ml-1 inline-block" />
            : <ArrowDown className="w-4 h-4 text-orange-500 ml-1 inline-block" />;
    };

    const renderCell = (col, value, row) => {
        if (col === 'Ícone') {
            return (
                <div className="w-10 h-10 rounded-full bg-slate-100 overflow-hidden ring-1 ring-slate-200">
                    {value ? <img src={value} alt="H" className="w-full h-full object-cover" /> : <div className="text-xs text-slate-400 font-bold p-2">?</div>}
                </div>
            );
        }
        if (col === 'Herói') return <span className="font-semibold text-slate-900">{value}</span>;
        if (col === 'Win Rate (%)') {
            const num = parseNum(value);
            let color = "bg-slate-100 text-slate-600";
            if (num >= 52) color = "bg-emerald-100 text-emerald-700";
            if (num <= 48) color = "bg-rose-100 text-rose-700";
            return <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium ${color}`}>{num.toFixed(2)}%</span>;
        }
        if (typeof value === 'number') return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
        return value;
    };

    return (
        <div className="overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.04)] ring-1 ring-slate-100 rounded-2xl bg-white">
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-100">
                    <thead className="bg-gray-50/50">
                        <tr>
                            {columns.map((col) => (
                                <th
                                    key={col}
                                    onClick={() => handleSort(col)}
                                    className={`py-4 pl-6 pr-3 text-left text-xs font-semibold uppercase tracking-wider select-none transition-colors 
                                        ${sortableColumns.includes(col) ? 'cursor-pointer hover:bg-gray-100/80 text-orange-600/80' : 'cursor-default text-slate-500'}`}
                                >
                                    <div className="flex items-center">{col} {getSortIcon(col)}</div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="bg-white">
                        {groupedAndSortedData.map((group) => (
                            <React.Fragment key={group.dateLabel}>
                                <tr className="bg-slate-50/80 border-y border-slate-100/50">
                                    <td colSpan={columns.length} className="py-2 px-6 text-[11px] font-bold text-slate-400 uppercase tracking-widest">
                                        Análise de: <span className="text-slate-600">{group.dateLabel}</span>
                                    </td>
                                </tr>
                                {group.items.map((row, idx) => (
                                    <tr key={`${group.dateLabel}-${idx}`} className="hover:bg-orange-50/30 transition-colors duration-200 border-b border-gray-50 last:border-none">
                                        {columns.map(col => (
                                            <td key={col} className="whitespace-nowrap py-4 pl-6 pr-3 text-sm text-slate-600">
                                                {renderCell(col, row[col], row)}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </React.Fragment>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
});

export default Table;
