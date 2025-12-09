/**
 * MultiSelectDropdown.jsx
 *
 * Componente de Interface para Seleção Múltipla com Formatação em Linguagem Natural.
 * 
 * RAZÃO DE EXISTIR:
 * - Permitir que o usuário selecione múltiplos heróis para comparação simultânea.
 * - Substituir a lista padrão de dropdown por uma interface rica com Checkboxes.
 * - Exibir o resumo da seleção em formato legível ("Ana, Ashe e Baptiste" ao invés de "3 selecionados").
 * 
 * FLUXO DE DADOS:
 * 1. Recebe 'selectedIds' (array) e lista de 'items' do pai.
 * 2. Gerencia estado de abertura do menu (isOpen).
 * 3. Ao clicar em um item, invoca 'onChange' com o novo array de IDs.
 * 4. Calcula dinamicamente o texto do botão (getDisplayLabel) para feedback visual imediato.
 */

import { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check, X } from 'lucide-react';

/**
 * Componente MultiSelectDropdown
 * 
 * @param {string} label - Texto padrão quando nada está selecionado.
 * @param {Array} items - Lista de opções [{ label, id }].
 * @param {Array} selectedIds - IDs atualmente selecionados.
 * @param {Function} onChange - Função chamada ao alterar seleção (retorna novo array).
 * @param {string} className - Classes CSS adicionais.
 * @param {string} variant - Estilo visual ('text' ou 'standard').
 */
const MultiSelectDropdown = ({ label, items, selectedIds = [], onChange, className = "", variant = "text" }) => {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    // Efeito para fechar o dropdown ao clicar fora dele (Click Outside)
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    // Função de Toggle: Adiciona ou remove ID do array de seleção
    const handleToggle = (id) => {
        // Caso especial: Limpar Tudo
        if (id === null) {
            onChange([]);
            return;
        }

        const newSelected = selectedIds.includes(id)
            ? selectedIds.filter(item => item !== id) // Se já existe, remove
            : [...selectedIds, id]; // Se não existe, adiciona

        onChange(newSelected);
    };

    /**
     * Gera o rótulo de exibição em formato de Linguagem Natural.
     * Ex: "Ana" ou "Ana e Ashe" ou "Ana, Ashe e Baptiste".
     */
    const getDisplayLabel = () => {
        if (selectedIds.length === 0) return label;

        // Mapeia IDs para Nomes
        const selectedNames = selectedIds.map(id => {
            const found = items.find(i => i.id === id);
            return found ? found.label : id;
        });

        // Caso base: 1 item
        if (selectedNames.length === 1) return selectedNames[0];

        // Caso múltiplo: Formata com vírgulas e "e" final
        const last = selectedNames.pop();
        return `${selectedNames.join(', ')} e ${last}`;
    };

    // Definição de estilos baseados na variante escolhida
    const buttonStyles = variant === "text"
        ? "inline-flex items-center font-bold text-slate-900 border-b-2 border-primary-500/30 hover:border-primary-500 hover:bg-primary-50 px-1 transition-all cursor-pointer truncate max-w-[300px]"
        : "inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors";

    return (
        <div className={`relative inline-block text-left ${className}`} ref={dropdownRef}>
            <div>
                <button
                    type="button"
                    className={buttonStyles}
                    onClick={() => setIsOpen(!isOpen)}
                    title={getDisplayLabel()} // Tooltip nativo ajuda se o texto for truncado
                >
                    <span className="truncate">{getDisplayLabel()}</span>
                    <ChevronDown className={`ml-1 h-4 w-4 flex-shrink-0 transition-transform ${isOpen ? 'rotate-180' : ''}`} aria-hidden="true" />
                </button>
            </div>

            {/* Menu Dropdown */}
            {isOpen && (
                <div
                    className="origin-top-right absolute left-0 mt-2 w-64 rounded-xl shadow-xl bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50 animate-fade-in-down overflow-hidden"
                    role="menu"
                >
                    {/* Header do Menu com botão 'Limpar' */}
                    <div className="bg-gray-50 px-4 py-2 border-b border-gray-100 flex justify-between items-center">
                        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Múltipla Escolha</span>
                        {selectedIds.length > 0 && (
                            <button
                                onClick={() => handleToggle(null)}
                                className="text-xs text-rose-500 hover:text-rose-700 font-medium flex items-center"
                            >
                                <X className="w-3 h-3 mr-1" /> Limpar
                            </button>
                        )}
                    </div>

                    {/* Lista de Itens com Checkbox visual */}
                    <div className="py-1 max-h-60 overflow-y-auto custom-scrollbar" role="none">
                        {items.map((item, index) => {
                            if (item.id === null) return null; // Pula itens nulos

                            const isSelected = selectedIds.includes(item.id);

                            return (
                                <button
                                    key={index}
                                    className={`relative text-slate-600 block w-full text-left px-4 py-3 text-sm hover:bg-emerald-50 transition-colors border-b border-gray-50 last:border-0 flex items-center justify-between ${isSelected ? 'bg-emerald-50/50 text-emerald-800 font-medium' : ''}`}
                                    role="menuitem"
                                    onClick={(e) => {
                                        e.preventDefault();
                                        handleToggle(item.id);
                                    }}
                                >
                                    <span>{item.label}</span>
                                    {isSelected && <Check className="w-4 h-4 text-emerald-600" />}
                                </button>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
};

export default MultiSelectDropdown;
