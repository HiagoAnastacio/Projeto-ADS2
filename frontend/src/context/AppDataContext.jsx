/**
 * AppDataContext.jsx
 *
 * Gerenciamento de Estado Global da Aplicação.
 * Utiliza a Context API do React para fornecer dados essenciais (dimensões)
 * e funções de utilidade (fetchAnalytics) para toda a árvore de componentes.
 */

// Importa hooks e funções do React para criar e gerenciar o contexto
import { createContext, useState, useEffect, useContext } from 'react';
// Importa funções do gerenciador de API para buscar dados
import { getGenericResource, queryAnalytics } from '../services/ApiManager';

// Cria o objeto de Contexto vazio inicialmente
const AppDataContext = createContext({});

/**
 * AppDataProvider
 * 
 * Componente Provedor que envolve a aplicação.
 * Responsável por:
 * 1. Carregar dados de dimensão (Bootstrapping) na inicialização.
 * 2. Fornecer funções de acesso à API para os componentes filhos.
 * 3. Gerenciar estado de carregamento global inicial.
 */
export const AppDataProvider = ({ children }) => {
    // --- Estados das Dimensões (Listas Estáticas carregadas no início) ---
    // Lista de heróis disponíveis
    const [heroes, setHeroes] = useState([]);
    // Lista de mapas disponíveis
    const [maps, setMaps] = useState([]);
    // Lista de ranks competitivos
    const [ranks, setRanks] = useState([]);
    // Lista de funções (Tank, Damage, Support)
    const [roles, setRoles] = useState([]);
    // Lista de modos de jogo
    const [gameModes, setGameModes] = useState([]);

    // --- Estados de Controle ---
    // Indica se a aplicação ainda está carregando os dados iniciais
    const [isLoading, setIsLoading] = useState(true);
    // Armazena mensagens de erro caso o carregamento falhe
    const [error, setError] = useState(null);

    // --- Bootstrapping (Efeito de Inicialização) ---
    useEffect(() => {
        // Função assíncrona para carregar todos os dados necessários
        const loadInitialData = async () => {
            try {
                // Inicia o estado de carregamento
                setIsLoading(true);

                // Busca paralela de todas as dimensões para otimizar tempo de carga (Promise.all)
                const [heroesData, mapsData, ranksData, rolesData, gameModesData] = await Promise.all([
                    getGenericResource('hero'),      // Busca heróis
                    getGenericResource('map'),       // Busca mapas
                    getGenericResource('rank'),      // Busca ranks
                    getGenericResource('role'),      // Busca funções
                    getGenericResource('game_mode')  // Busca modos de jogo
                ]);

                // Atualiza os estados com os dados recebidos
                setHeroes(heroesData);
                setMaps(mapsData);
                setRanks(ranksData);
                setRoles(rolesData);
                setGameModes(gameModesData);
            } catch (err) {
                // Loga o erro no console para debug
                console.error("Erro crítico ao carregar dados iniciais:", err);
                // Define uma mensagem de erro amigável para a UI
                setError("Falha ao conectar com o servidor. Verifique sua conexão.");
            } finally {
                // Finaliza o estado de carregamento, independentemente de sucesso ou erro
                setIsLoading(false);
            }
        };

        // Executa a função de carga
        loadInitialData();
    }, []); // Array de dependências vazio garante execução única na montagem

    /**
     * fetchAnalytics
     * 
     * Wrapper para a função de analytics do ApiManager.
     * Permite que componentes busquem dados sem importar o ApiManager diretamente,
     * mantendo o acoplamento baixo e centralizando a lógica de acesso a dados.
     * 
     * @param {object} filters - Objeto de query (ver ApiManager.queryAnalytics)
     */
    const fetchAnalytics = async (filters) => {
        try {
            // Chama o serviço de API
            const data = await queryAnalytics(filters);
            // Retorna os dados para o componente solicitante
            return data;
        } catch (err) {
            // Loga erros específicos de analytics
            console.error("Erro no contexto ao buscar analytics:", err);
            // Repassa o erro para que o componente possa tratar (ex: mostrar mensagem)
            throw err;
        }
    };

    // Renderiza o Provider com os valores e funções expostos
    return (
        <AppDataContext.Provider value={{
            heroes,      // Lista de heróis
            maps,        // Lista de mapas
            ranks,       // Lista de ranks
            roles,       // Lista de funções
            gameModes,   // Lista de modos de jogo
            isLoading,   // Estado de carregamento global
            error,       // Erro global
            fetchAnalytics // Função para buscar dados analíticos
        }}>
            {/* Renderiza os componentes filhos dentro do contexto */}
            {children}
        </AppDataContext.Provider>
    );
};

// Hook personalizado para facilitar o acesso ao contexto em outros componentes
export const useAppData = () => {
    return useContext(AppDataContext);
};

// Exporta o contexto (embora o uso via hook seja preferido)
export default AppDataContext;
