import { Outlet } from 'react-router-dom';
import Header from '../ui/Header';
import Footer from '../ui/Footer';

/**
 * MainLayout
 * 
 * Layout principal da aplicação.
 * Estrutura:
 * - Header (Fixo)
 * - Main Content (Com padding-top para compensar o header fixo)
 * - Footer (Fixo na base se o conteúdo for curto)
 */
const MainLayout = () => {
    return (
        // pt-16 adicionado para compensar a altura do Header fixo (h-16)
        <div className="min-h-screen flex flex-col bg-gray-50 font-sans text-gray-900 pt-16">
            <Header />

            <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                <Outlet />
            </main>

            <Footer />
        </div>
    );
};

export default MainLayout;
