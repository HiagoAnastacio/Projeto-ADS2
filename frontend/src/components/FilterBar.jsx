// =======================================================================================
// COMPONENTE DE APRESENTAÇÃO - FilterBar.jsx
// =======================================================================================
// ... (Comentários de cabeçalho) ...
// =======================================================================================

import React from 'react';

// Linha 13: Define o componente "burro". Recebe 'dimensions' e 'onFilterChange' do App.jsx.
const FilterBar = ({ dimensions, onFilterChange }) => {
  
  // Linha 16: Função interna chamada quando o <select> muda.
  const handleHeroChange = (e) => {
    // Linha 17: Pega o novo valor (ID do herói).
    const newHeroId = parseInt(e.target.value, 10);
    // Linha 19: (Levantamento de Estado) Chama a função que veio do PAI (App.jsx).
    // Isso atualiza o estado 'filters' DENTRO do App.jsx.
    onFilterChange({ hero_id: newHeroId });
  };

  // Linha 23: Renderiza o HTML/JSX.
  return (
    <div className="bg-gray-100 p-4 rounded-lg shadow">
      {/* ... Título ... */}
      <div className="flex space-x-4">
        
        {/* Dropdown de Heróis */}
        <div>
          {/* ... Label ... */}
          <select
            id="hero-select"
            className="..." // Estilos Tailwind
            // Linha 39: Quando mudar, chama a função interna.
            onChange={handleHeroChange}
            // Linha 40: Define o valor padrão (Ana).
            defaultValue={1}
          >
            {/* Linha 42: Faz um loop nos dados de 'dimensions.hero' (vindos do App.jsx). */}
            {dimensions.hero.map((hero) => (
              // Linha 43: Cria um <option> para cada herói.
              <option key={hero.id} value={hero.id}>
                {hero.hero_name}
              </option>
            ))}
          </select>
        </div>
        
        {/* ... (Seção de Ranks futuros comentada) ... */}

      </div>
    </div>
  );
};

export default FilterBar;