import { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check, X } from 'lucide-react';

/**
 * MultiSelectDropdown.jsx
 * 
 * Componente de Dropdown para seleção múltipla.
 * Baseado no design do Dropdown original, mas com checkboxes e gestão de array.
 * 
 * @param {string} label - Rótulo padrão (ex: "Todos os Heróis")
 * @param {array} items - Lista de objetos { label, id }
 * @param {array} selectedIds - Array de IDs atualmente selecionados
 * @param {function} onChange - Callback (newSelectedIds) => void
 */
const MultiSelectDropdown = ({ label, items, selectedIds = [], onChange, className = "", variant = "text" }) => {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    // Fecha ao clicar fora
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    // Toggle de seleção
    const handleToggle = (id) => {
        if (id === null) {
            onChange([]);
            return;
        }

        const newSelected = selectedIds.includes(id)
            ? selectedIds.filter(item => item !== id) // Remove
            : [...selectedIds, id]; // Adiciona

        onChange(newSelected);
    };

    // Label dinâmica formato lista natural
    const getDisplayLabel = () => {
        if (selectedIds.length === 0) return label;

        // Encontra os nomes dos itens selecionados
        const selectedNames = selectedIds.map(id => {
            const found = items.find(i => i.id === id);
            return found ? found.label : id;
        });

        // Formatação: "A", "A e B", "A, B e C"
        if (selectedNames.length === 1) return selectedNames[0];

        const last = selectedNames.pop();
        return `${selectedNames.join(', ')} e ${last}`;
    };

    // Estilos baseados na variante
    const buttonStyles = variant === "text"
        ? "inline-flex items-center font-bold text-slate-900 border-b-2 border-emerald-500/30 hover:border-emerald-500 hover:bg-emerald-50/50 px-1 transition-all cursor-pointer truncate max-w-[300px]" // Aumentado max-w para caber nomes
        : "inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors";

    return (
        <div className={`relative inline-block text-left ${className}`} ref={dropdownRef}>
            <div>
                <button
                    type="button"
                    className={buttonStyles}
                    onClick={() => setIsOpen(!isOpen)}
                    title={getDisplayLabel()} // Tooltip nativo caso corte
                >
                    <span className="truncate">{getDisplayLabel()}</span>
                    <ChevronDown className={`ml-1 h-4 w-4 flex-shrink-0 transition-transform ${isOpen ? 'rotate-180' : ''}`} aria-hidden="true" />
                </button>
            </div>

            {isOpen && (
                <div
                    className="origin-top-right absolute left-0 mt-2 w-64 rounded-xl shadow-xl bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50 animate-fade-in-down overflow-hidden"
                    role="menu"
                >
                    {/* Header com ação rápida (Limpar) */}
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

                    <div className="py-1 max-h-60 overflow-y-auto custom-scrollbar" role="none">
                        {items.map((item, index) => {
                            if (item.id === null) return null;

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
