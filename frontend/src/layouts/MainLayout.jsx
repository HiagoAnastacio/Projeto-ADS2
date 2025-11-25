/**
 * MainLayout.jsx
 *
 * Layout Principal da Aplicação.
 * Define a estrutura base comum a todas as páginas, incluindo:
 * - Cabeçalho (Header) fixo no topo
 * - Área de conteúdo principal (Main)
 * - Rodapé (Footer) fixo na base
 */

// Importa componente Outlet para renderizar rotas filhas
import { Outlet } from 'react-router-dom';
// Importa componentes estruturais
import Header from '../ui/Header';
import Footer from '../ui/Footer';

/**
 * Componente MainLayout
 * 
 * Envolve o conteúdo da aplicação com a estrutura de navegação padrão.
 */
const MainLayout = () => {
    return (
        // Container flexível que ocupa no mínimo toda a altura da tela
        // pt-16 adicionado para compensar a altura do Header fixo (h-16) e evitar sobreposição
        <div className="min-h-screen flex flex-col bg-gray-50 font-sans text-gray-900 pt-16">

            {/* Cabeçalho Fixo */}
            <Header />

            {/* Área de Conteúdo Principal */}
            {/* flex-1 garante que o main ocupe todo o espaço disponível, empurrando o footer para baixo */}
            <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                {/* O Outlet renderiza o componente da rota atual (ex: Dashboard) */}
                <Outlet />
            </main>

            {/* Rodapé */}
            <Footer />
        </div>
    );
};

// Exporta o layout
export default MainLayout;
