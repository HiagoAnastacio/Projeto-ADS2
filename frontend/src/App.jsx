/**
 * App.jsx
 *
 * Componente Raiz da Aplicação.
 * Configura o Roteamento (Router) e o Provedor de Contexto Global (AppDataProvider).
 * Define a estrutura de navegação principal.
 */

// Importa componentes de roteamento do React Router
import { BrowserRouter, Routes, Route } from 'react-router-dom';
// Importa o provedor de contexto que gerencia o estado global da aplicação
import { AppDataProvider } from './context/AppDataContext';
// Importa o layout principal que envolve as páginas
import MainLayout from './layouts/MainLayout';
// Importa o componente de destaque dos Top 3 Heróis
import HeroTop3 from './ui/HeroTop3';
// Importa a seção de análise detalhada (gráficos e tabelas)
import AnalysisSection from './ui/AnalysisSection';

// Função principal do componente App
function App() {
    return (
        // Envolve toda a aplicação no provedor de dados para acesso global ao estado
        <AppDataProvider>
            {/* Configura o roteador para navegação baseada em browser history */}
            <BrowserRouter>
                {/* Define as rotas da aplicação */}
                <Routes>
                    {/* Rota Pai: Usa o MainLayout como estrutura base para todas as rotas aninhadas */}
                    <Route path="/" element={<MainLayout />}>
                        {/* Rota Index: Renderiza a página inicial (Dashboard) quando o caminho é '/' */}
                        <Route index element={
                            // Fragmento para agrupar múltiplos componentes na mesma rota
                            <>
                                {/* Exibe os Top 3 Heróis */}
                                <HeroTop3 />
                                {/* Exibe a Seção de Análise com Gráficos e Tabelas */}
                                <AnalysisSection />
                            </>
                        } />
                    </Route>
                </Routes>
            </BrowserRouter>
        </AppDataProvider>
    );
}

// Exporta o componente App para ser usado no main.jsx
export default App;
