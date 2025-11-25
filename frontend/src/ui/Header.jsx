/**
 * Header.jsx
 *
 * Cabeçalho de Navegação da Aplicação.
 * Contém o logo, links de navegação principais e menu responsivo para mobile.
 */

// Importa hooks e componentes
import { useState } from 'react';
import Dropdown from '../components/Dropdown';
import { Menu, X, BarChart2 } from 'lucide-react';

const Header = () => {
    // Estado para controlar o menu mobile (aberto/fechado)
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    // Função para rolar suavemente até a seção de análise
    const scrollToAnalysis = () => {
        const section = document.getElementById('analysis-section');
        if (section) {
            section.scrollIntoView({ behavior: 'smooth' });
            // Fecha o menu mobile se estiver aberto
            setIsMobileMenuOpen(false);
        }
    };

    // Lista de links externos para o Dropdown
    const blizzardLinks = [
        { label: 'Overwatch 2 Oficial', action: () => window.open('https://overwatch.blizzard.com/pt-br/', '_blank') },
        { label: 'Battle.net', action: () => window.open('https://us.shop.battle.net/pt-br', '_blank') },
        { label: 'Overwatch League', action: () => window.open('https://overwatchleague.com/', '_blank') },
    ];

    return (
        // Header fixo no topo com z-index alto
        <header className="bg-white shadow-sm fixed top-0 w-full z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    {/* Logo e Título da Aplicação */}
                    <div className="flex items-center">
                        <div className="flex-shrink-0 flex items-center text-orange-600">
                            <BarChart2 className="h-8 w-8 mr-2" />
                            <span className="font-bold text-xl tracking-tight text-gray-900">OverWatch<span className="text-orange-600">Analytics</span></span>
                        </div>
                    </div>

                    {/* Menu Desktop (visível apenas em telas sm ou maiores) */}
                    <div className="hidden sm:flex sm:items-center sm:space-x-8">
                        <button
                            onClick={scrollToAnalysis}
                            className="text-gray-500 hover:text-orange-600 px-3 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer"
                        >
                            Ir para Análise
                        </button>

                        {/* Dropdown de Links Externos */}
                        <Dropdown
                            label="Links Blizzard"
                            items={blizzardLinks}
                        />
                    </div>

                    {/* Botão do Menu Mobile (visível apenas em telas pequenas) */}
                    <div className="flex items-center sm:hidden">
                        <button
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                            className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-orange-500"
                        >
                            {/* Alterna ícone entre Menu (hambúrguer) e X (fechar) */}
                            {isMobileMenuOpen ? (
                                <X className="block h-6 w-6" aria-hidden="true" />
                            ) : (
                                <Menu className="block h-6 w-6" aria-hidden="true" />
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Menu Mobile (Renderização Condicional) */}
            {isMobileMenuOpen && (
                <div className="sm:hidden bg-white border-t border-gray-200">
                    <div className="pt-2 pb-3 space-y-1 px-4">
                        {/* Link de Navegação Mobile */}
                        <button
                            onClick={scrollToAnalysis}
                            className="block w-full text-left text-base font-medium text-gray-500 hover:text-orange-600 hover:bg-gray-50 px-3 py-2 rounded-md"
                        >
                            Ir para Análise
                        </button>

                        {/* Seção de Links Externos Mobile */}
                        <div className="border-t border-gray-100 pt-2 mt-2">
                            <p className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Links Blizzard</p>
                            {blizzardLinks.map((link, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => {
                                        link.action();
                                        setIsMobileMenuOpen(false);
                                    }}
                                    className="block w-full text-left text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 px-3 py-2 rounded-md"
                                >
                                    {link.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </header>
    );
};

// Exporta o componente Header
export default Header;
