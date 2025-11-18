// =======================================================================================
// MÓDULO GERENCIADOR DA API (CAMADA DE SERVIÇO) (v0.4.0 - Adicionada busca de Dimensões)
// =======================================================================================

import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/API/V1-DATA',
  headers: {
    'Content-Type': 'application/json'
  }
});

/**
 * [POST] Envia uma query complexa para o endpoint de análise.
 * @param {object} queryBody - Corpo da consulta (type, metric, filters).
 */
export const fetchAnalyticsData = (queryBody) => {
  return apiClient.post('/ANALYSIS/QUERY', queryBody);
};

/**
 * [GET] Busca a lista de IDs e Nomes para popular os filtros (Dimensões).
 * @param {string} dimensionName - 'hero', 'rank', 'map', ou 'game_mode'.
 */
export const fetchDimensions = (dimensionName) => {
    // Chama a nova rota de dimensões
    return apiClient.get(`/DIMENSIONS/${dimensionName.toLowerCase()}`);
}

export default apiClient;