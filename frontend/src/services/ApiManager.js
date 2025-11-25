/**
 * ApiManager.js
 *
 * Camada de Serviço para comunicação HTTP com o Backend.
 * Configura o cliente Axios, interceptadores e define funções tipadas
 * para buscar recursos e realizar consultas analíticas.
 */

// Importa a biblioteca Axios para requisições HTTP
import axios from 'axios';

// =======================================================================================
// CONFIGURAÇÃO DO CLIENTE HTTP
// =======================================================================================

// Cria uma instância do Axios com configurações padrão
const apiClient = axios.create({
    // Base URL da API (Aponta para o endpoint de dados V1)
    // Ajuste conforme ambiente: localhost, docker, prod
    baseURL: 'http://localhost:8000/API/V1-DATA',
    // Define cabeçalhos padrão
    headers: {
        'Content-Type': 'application/json' // Comunicação sempre em JSON
    }
});

// Interceptor de Resposta: Tratamento global de erros
apiClient.interceptors.response.use(
    // Se sucesso, retorna a resposta sem alterações
    (response) => response,
    // Se erro, processa antes de repassar
    (error) => {
        // Extrai a mensagem de erro detalhada do backend ou usa a padrão
        const errorMessage = error.response?.data?.detail || error.message;
        // Loga o erro com a URL que falhou para facilitar o debug
        console.error(`[API Error] ${error.config?.url}:`, errorMessage);
        // Rejeita a promise para que o chamador possa tratar (catch)
        return Promise.reject(error);
    }
);

// =======================================================================================
// 1. BOOTSTRAPPING (CARGA DE DADOS ESTÁTICOS/DIMENSÕES)
// =======================================================================================

/**
 * getGenericResource
 * 
 * Busca todo o conteúdo de uma tabela de dimensão.
 * Usado para popular filtros e listas estáticas no frontend (ex: lista de heróis).
 * 
 * @param {string} resourceName - Nome do recurso/tabela (ex: 'hero', 'map', 'rank')
 * @returns {Promise<Array>} Lista de objetos do recurso.
 */
export const getGenericResource = async (resourceName) => {
    try {
        // Faz GET na rota raiz do recurso (ex: /hero)
        const response = await apiClient.get(`/${resourceName}`);
        // Retorna apenas os dados da resposta
        return response.data;
    } catch (error) {
        // Loga erro específico de recurso
        console.error(`Falha ao buscar recurso [${resourceName}]:`, error);
        // Lança o erro novamente
        throw error;
    }
};

// =======================================================================================
// 2. ANÁLISE (QUERY DINÂMICA)
// =======================================================================================

/**
 * queryAnalytics
 * 
 * Envia uma consulta analítica complexa para o Backend.
 * Utiliza o endpoint POST /ANALYSIS/QUERY para flexibilidade de filtros.
 * Segue o schema definido em `route_schema_analytic.py` no backend.
 * 
 * @param {object} queryBody - Objeto contendo:
 *  - table_name: string (Obrigatório - ex: 'vw_hero_win_latest')
 *  - filters_equal: object (Opcional - ex: { hero_id: 1 })
 *  - filters_in: object (Opcional - ex: { hero_id: [1, 2] })
 *  - start_date: string (Opcional)
 *  - end_date: string (Opcional)
 *  - limit: number (Default: 100)
 * 
 * @returns {Promise<Array>} Lista de resultados da consulta.
 */
export const queryAnalytics = async (queryBody) => {
    try {
        // Faz POST enviando o corpo da query
        const response = await apiClient.post('/ANALYSIS/QUERY', queryBody);
        // Retorna os dados analíticos
        return response.data;
    } catch (error) {
        // Loga erro de consulta analítica
        console.error("Falha na consulta analítica:", error);
        // Lança o erro novamente
        throw error;
    }
};

// Exporta o cliente axios configurado como padrão, caso necessário uso direto
export default apiClient;