/**
 * Header.jsx
 *
 * Cabeçalho de Navegação da Aplicação.
 *
 * RAZÃO DE EXISTIR:
 * - Fornecer uma navegação consistente e acessível em todas as páginas.
 * - Exibir a identidade visual da marca (Logo e Nome).
 * - Permitir acesso rápido a links externos importantes (Blizzard, Patch Notes).
 * - Garantir usabilidade em dispositivos móveis através de um menu responsivo.
 *
 * POSIÇÃO NO FLUXO DE DADOS:
 * - Componente de UI puro, não consome dados do contexto global.
 * - Gerencia seu próprio estado de UI (menu mobile aberto/fechado).
 * - Dispara eventos de navegação (scroll) para outras partes da página.
 */

// Importa hooks do React
import { useState } from 'react';
// Importa componente de Dropdown reutilizável
import Dropdown from '../components/Dropdown';
// Importa ícones da biblioteca Lucide React
import { Menu, X, BarChart2 } from 'lucide-react';

// --- Componente Header ---
const Header = () => {
    // --- Estado Local ---
    // Controla se o menu mobile está visível ou oculto
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    // --- Handlers ---
    // Função para rolar suavemente a página até a seção de análise principal
    const scrollToAnalysis = () => {
        // Busca o elemento alvo pelo ID
        const section = document.getElementById('analysis-section');
        // Se o elemento existir na página...
        if (section) {
            // ...executa o scroll suave
            section.scrollIntoView({ behavior: 'smooth' });
            // Fecha o menu mobile automaticamente para melhor UX
            setIsMobileMenuOpen(false);
        }
    };

    // --- Configuração de Links ---
    // Lista de objetos contendo rótulos e ações para o dropdown de links externos
    const blizzardLinks = [
        { label: 'Overwatch 2 Oficial', action: () => window.open('https://overwatch.blizzard.com/pt-br/', '_blank') },
        { label: 'Overwatch 2 Patch Notes', action: () => window.open('https://overwatch.blizzard.com/pt-br/news/patch-notes/', '_blank') },
        { label: 'Battle.net', action: () => window.open('https://us.shop.battle.net/pt-br', '_blank') },
    ];

    // --- Renderização ---
    return (
        // Container principal do cabeçalho
        // 'fixed top-0': Mantém o header fixo no topo da tela durante a rolagem
        // 'z-50': Garante que fique acima de outros elementos
        <header className="bg-white shadow-sm fixed top-0 w-full z-50">

            {/* Container centralizado com largura máxima */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">

                    {/* --- Logo e Título --- */}
                    <div className="flex items-center">
                        {/* Botão que rola para o topo ao clicar no logo */}
                        <button
                            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                            className="flex-shrink-0 flex items-center text-orange-600 cursor-pointer hover:opacity-80 transition-opacity"
                        >
                            {/* Ícone do Logo */}
                            <BarChart2 className="h-8 w-8 mr-2" />
                            {/* Nome da Aplicação com destaque de cor */}
                            <span className="font-bold text-xl tracking-tight text-gray-900">Overwatch<span className="text-orange-600">MetaAnalyzer</span></span>
                        </button>
                    </div>

                    {/* --- Navegação Desktop --- */}
                    {/* 'hidden sm:flex': Oculta em mobile, exibe em telas maiores (sm+) */}
                    <div className="hidden sm:flex sm:items-center sm:space-x-8">
                        {/* Botão de Navegação Interna */}
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

                    {/* --- Botão Menu Mobile --- */}
                    {/* 'sm:hidden': Exibe apenas em telas pequenas */}
                    <div className="flex items-center sm:hidden">
                        <button
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                            className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-orange-500"
                        >
                            {/* Alterna o ícone dependendo do estado (Aberto/Fechado) */}
                            {isMobileMenuOpen ? (
                                <X className="block h-6 w-6" aria-hidden="true" />
                            ) : (
                                <Menu className="block h-6 w-6" aria-hidden="true" />
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* --- Menu Mobile (Expandido) --- */}
            {/* Renderização condicional baseada no estado */}
            {isMobileMenuOpen && (
                <div className="sm:hidden bg-white border-t border-gray-200">
                    <div className="pt-2 pb-3 space-y-1 px-4">
                        {/* Link de Navegação Interna (Mobile) */}
                        <button
                            onClick={scrollToAnalysis}
                            className="block w-full text-left text-base font-medium text-gray-500 hover:text-orange-600 hover:bg-gray-50 px-3 py-2 rounded-md"
                        >
                            Ir para Análise
                        </button>

                        {/* Seção de Links Externos (Mobile) */}
                        <div className="border-t border-gray-100 pt-2 mt-2">
                            <p className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Links Blizzard</p>
                            {/* Mapeia os links para botões individuais */}
                            {blizzardLinks.map((link, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => {
                                        link.action(); // Executa a ação (abrir link)
                                        setIsMobileMenuOpen(false); // Fecha o menu
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

// Exporta o componente Header para uso global
export default Header;
