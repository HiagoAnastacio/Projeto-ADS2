// =======================================================================================
// COMPONENTE DE APRESENTAÇÃO - StatTable.jsx
// =======================================================================================
// RAZÃO DE EXISTIR: Isolar (SoC) a lógica de renderização da
// tabela de dados. Este componente é "burro". Ele recebe 'data'
// via props e apenas os "mapeia" para <tr> e <td>
// (conforme Texto2.txt - Divulgação Progressiva).
// =======================================================================================

import React from 'react';

const StatTable = ({ data }) => {

  if (!data || data.length === 0) {
    return <div className="text-center p-4">Sem dados para exibir na tabela.</div>;
  }

  // Pega os cabeçalhos dinamicamente do primeiro item
  const headers = Object.keys(data[0]);

  // Função de formatação (copiada do App.jsx antigo)
  const formatRate = (rate) => {
    if (rate === null || rate === undefined) return 'N/A';
    return `${(parseFloat(rate) * 100).toFixed(2)}%`;
  };

  return (
    <div className="overflow-x-auto shadow-md rounded-lg">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {headers.map((key) => (
              <th
                key={key}
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {key.replace(/_/g, ' ')} {/* (Substitui _ por espaço) */}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((row, index) => (
            <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
              {headers.map((key) => (
                <td key={key} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {/* (Formatação especial para "rates") */}
                  {key.includes('_rate') ? formatRate(row[key]) : row[key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StatTable;