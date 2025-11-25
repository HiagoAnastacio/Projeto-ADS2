/**
 * Dropdown.jsx
 *
 * Componente de Interface de Usuário para seleção de opções.
 * Implementa um menu suspenso acessível e responsivo.
 * Suporta fechamento ao clicar fora (click outside).
 */

// Importa hooks do React para gerenciar estado e referências DOM
import { useState, useRef, useEffect } from 'react';
// Importa ícone de seta para baixo
import { ChevronDown } from 'lucide-react';

/**
 * Componente Dropdown
 * 
 * @param {string} label - Texto exibido no botão principal
 * @param {Array} items - Lista de itens do menu [{ label, action }]
 * @param {function} onSelect - Callback opcional ao selecionar um item
 * @param {string} className - Classes CSS adicionais
 */
const Dropdown = ({ label, items, onSelect, className = "" }) => {
    // Estado para controlar a visibilidade do menu
    const [isOpen, setIsOpen] = useState(false);
    // Referência para o elemento raiz do dropdown (usado para detecção de clique fora)
    const dropdownRef = useRef(null);

    // Efeito para adicionar listener de clique global
    useEffect(() => {
        // Função que verifica se o clique ocorreu fora do componente
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                // Fecha o dropdown se clicou fora
                setIsOpen(false);
            }
        };
        // Adiciona o listener ao documento
        document.addEventListener("mousedown", handleClickOutside);
        // Remove o listener ao desmontar o componente para evitar memory leaks
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    return (
        // Container relativo para posicionamento do menu absoluto
        <div className={`relative inline-block text-left ${className}`} ref={dropdownRef}>
            <div>
                {/* Botão principal do Dropdown */}
                <button
                    type="button"
                    className="inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition-colors"
                    onClick={() => setIsOpen(!isOpen)} // Alterna estado aberto/fechado
                >
                    {label}
                    {/* Ícone de seta indicando dropdown */}
                    <ChevronDown className="-mr-1 ml-2 h-5 w-5" aria-hidden="true" />
                </button>
            </div>

            {/* Renderização condicional do menu suspenso */}
            {isOpen && (
                <div
                    className="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50 animate-fade-in-down"
                    role="menu"
                >
                    <div className="py-1" role="none">
                        {/* Mapeia os itens recebidos para botões */}
                        {items.map((item, index) => (
                            <button
                                key={index}
                                className="text-gray-700 block w-full text-left px-4 py-2 text-sm hover:bg-gray-100 hover:text-gray-900"
                                role="menuitem"
                                onClick={() => {
                                    // Executa a ação específica do item, se houver
                                    if (item.action) item.action();
                                    // Executa o callback genérico de seleção, se houver
                                    if (onSelect) onSelect(item);
                                    // Fecha o menu após a seleção
                                    setIsOpen(false);
                                }}
                            >
                                {item.label}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

// Exporta o componente Dropdown
export default Dropdown;
