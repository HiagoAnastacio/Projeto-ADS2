// =======================================================================================
// COMPONENTE DE APRESENTAÇÃO - StatDashboard.jsx
// =======================================================================================
// RAZÃO DE EXISTIR: Isolar (SoC) a lógica de renderização do
// gráfico Recharts. Este componente é "burro". Ele não sabe
// de onde vêm os dados; ele apenas os recebe via 'props'
// e os plota (conforme Texto1.txt - Hierarquia Visual).
// =======================================================================================

import React from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts'; // Importa o Recharts

const StatDashboard = ({ data }) => {
  
  if (!data || data.length === 0) {
    return <div className="text-center p-4">Sem dados históricos para exibir o gráfico.</div>;
  }

  // Formata o eixo Y para ser (ex: 50.1%)
  const percentFormatter = (value) => `${(value * 100).toFixed(1)}%`;

  return (
    // ResponsiveContainer faz o gráfico preencher o espaço do <div>
    <div style={{ width: '100%', height: 400 }}>
      <ResponsiveContainer>
        <LineChart
          data={data}
          margin={{
            top: 5, right: 30, left: 20, bottom: 5,
          }}
        >
          {/* Grid de fundo */}
          <CartesianGrid strokeDasharray="3 3" />
          
          {/* Eixo X (Data) */}
          <XAxis 
            dataKey="date_of_the_data" 
            // (Opcional: formata a data se ela for muito longa)
            // tickFormatter={(dateStr) => new Date(dateStr).toLocaleDateString()}
          />
          
          {/* Eixo Y (Win Rate) */}
          <YAxis 
            tickFormatter={percentFormatter} 
            domain={[0.40, 0.60]} // Força o eixo (conforme discutimos)
          />
          
          {/* Tooltip (Interatividade) */}
          <Tooltip formatter={percentFormatter} />
          <Legend />
          
          {/* A Linha */}
          <Line 
            type="monotone" 
            dataKey="win_rate" 
            stroke="#8884d8" 
            activeDot={{ r: 8 }} 
            name="Taxa de Vitória"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StatDashboard;