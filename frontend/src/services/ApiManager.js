// =======================================================================================
// GERENCIADOR DE API (SERVICE LAYER)
// =======================================================================================
// Responsabilidade: Centralizar chamadas HTTP.
// Integração Atual:
// 1. Bootstrapping (getGenericResource)
// 2. Discovery de Modelo (getQueryTemplate) -> Conectado ao route_schema_analytic.py
// 3. Análise (queryAnalytics)
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
    // Tenta extrair a mensagem de erro detalhada do FastAPI (ex: detail)
    const errorMessage = error.response?.data?.detail || error.message;
    console.error("Erro na API:", errorMessage);
    return Promise.reject(error);
  }
);

// =======================================================================================
// 1. DISCOVERY & SCHEMAS (Conexão com route_schema_analytic.py)
// =======================================================================================

/**
 * [GET] Busca o Modelo de Requisição Analítica (Template JSON).
 * Rota Backend: /MODELS/Analysis_Query/EXEMPLE
 * * Objetivo: Obter o JSON "esqueleto" que o Backend espera (definido em AnalysisQuery),
 * garantindo que o Frontend monte a query com os campos corretos.
 */
export const getQueryTemplate = async () => {
    try {
        const response = await apiClient.get('/MODELS/Analysis_Query/EXEMPLE');
        // Retorna o objeto (ex: { table_name: "string", filters_equal: {}, ... })
        return response.data; 
    } catch (error) {
        console.error("Erro crítico ao obter template de query (Schema):", error);
        throw error;
    }
};

// =======================================================================================
// 2. BOOTSTRAPPING (CARGA DE DADOS ESTÁTICOS)
// =======================================================================================

/**
 * [GET] Busca todo o conteúdo de uma tabela genérica (Dimensão).
 * Rota: /{resourceName} (ex: /hero, /rank, /map)
 * Usado para popular a memória do Frontend na inicialização.
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

// =======================================================================================
// 3. ANÁLISE (QUERY DINÂMICA)
// =======================================================================================

/**
 * [POST] Envia a consulta analítica para o Backend.
 * Rota: /ANALYSIS/QUERY
 * * @param {object} queryBody - O objeto JSON montado (baseado no template acima).
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