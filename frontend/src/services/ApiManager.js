// =======================================================================================
// GERENCIADOR DE API (SERVICE LAYER) - Bootstrapping & Análise
// =======================================================================================
// Responsabilidade: Centralizar chamadas HTTP.
// Padrão: Usa a rota GET genérica já existente no Backend para buscar metadados.
// =======================================================================================

import axios from 'axios';

// Configuração base do cliente HTTP
const apiClient = axios.create({
  // Ajuste a URL se estiver rodando em Docker ou porta diferente
  baseURL: 'http://localhost:8000/API/V1-DATA',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para logs de erro globais
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("Erro na API:", error.response?.data?.detail || error.message);
    return Promise.reject(error);
  }
);

// =======================================================================================
// 1. BOOTSTRAPPING (CARGA DE METADADOS VIA ROTA GENÉRICA)
// O Frontend chama isso para baixar as tabelas inteiras de dimensão (Lookup Tables).
// Usa a rota: GET /API/V1-DATA/{table_name} (definida em routes_get.py)
// =======================================================================================

/**
 * Busca todo o conteúdo de uma tabela (recurso) via rota genérica.
 * @param {string} resourceName - Nome da tabela (ex: 'hero', 'rank', 'map').
 * @returns {Promise<Array>} Lista completa de registros.
 */
export const getGenericResource = async (resourceName) => {
    try {
        const response = await apiClient.get(`/${resourceName}`);
        return response.data;
    } catch (error) {
        console.error(`Falha ao buscar recurso [${resourceName}]:`, error);
        throw error;
    }
};

/**
 * Helper para carregar TODAS as dimensões necessárias de uma vez.
 * Deve ser chamado no useEffect inicial do App.jsx (ou Provider).
 */
export const fetchAllMetadata = async () => {
    try {
        // Dispara requisições em paralelo para ganhar tempo
        const [heroes, ranks, gameModes, maps, roles] = await Promise.all([
            getGenericResource('hero'),
            getGenericResource('rank'),
            getGenericResource('game_mode'),
            getGenericResource('map'),
            getGenericResource('role')
        ]);

        return {
            heroes,
            ranks,
            gameModes,
            maps,
            roles
        };
    } catch (error) {
        console.error("Erro crítico no Bootstrapping de metadados:", error);
        throw error;
    }
};


// =======================================================================================
// 2. ANÁLISE (DADOS DINÂMICOS)
// Busca apenas os números (IDs e Taxas). O Frontend fará o JOIN com os metadados acima.
// =======================================================================================

/**
 * Envia uma consulta para o motor de análise.
 * Rota: POST /API/V1-DATA/ANALYSIS/QUERY
 * @param {object} queryBody - Objeto { table_name, filters_equal, etc. }
 */
export const queryAnalytics = async (queryBody) => {
    try {
        const response = await apiClient.post('/ANALYSIS/QUERY', queryBody);
        return response.data;
    } catch (error) {
        console.error("Falha na consulta analítica:", error);
        throw error;
    }
};

export default apiClient;