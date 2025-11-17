// =======================================================================================
// MÓDULO GERENCIADOR DA API (CAMADA DE SERVIÇO) (v0.3.0 - Refatorado)
// =======================================================================================
// FLUXO E A LÓGICA:
// 1. Cria a instância 'apiClient' do Axios com a baseURL correta.
// 2. (REFATORADO) Remove todas as funções GET específicas (ex: getLatestRankStats).
// 3. (REFATORADO) Exporta UMA ÚNICA função: `fetchAnalyticsData`.
// 4. Esta função chama o endpoint genérico `POST /analysis/query` do backend,
//    passando o corpo da consulta (queryBody) que o componente React solicitar.
//
// RAZÃO DE EXISTIR: Aplicar SoC e DRY. Centraliza 100% do acesso aos
// dados analíticos em uma única função, espelhando a arquitetura do backend.
// =======================================================================================

// Linha 17: Importa a biblioteca 'axios'.
import axios from 'axios';

// Linha 20: Cria uma instância configurada do Axios.
const apiClient = axios.create({
  // Linha 22: Define a URL base para a API FastAPI (conforme main.py).
  baseURL: 'http://localhost:8000/API/V1-DATA',
  headers: {
    'Content-Type': 'application/json'
  }
});

/**
 * (NOVA FUNÇÃO ÚNICA)
 * Busca dados (atuais ou históricos) usando a rota de análise genérica.
 *
 * @param {object} queryBody - O corpo da requisição (conforme analytic_model.py)
 * (ex: { table_name: "hero_win", filters_equal: {"hero_id": 1} })
 * (ex: { table_name: "vw_hero_win_latest" })
 */
export const fetchAnalyticsData = (queryBody) => {
  // Linha 40: Faz um POST para 'http://localhost:8000/API/V1-DATA/analysis/query'
  // O `queryBody` é o JSON que o backend espera (modelo AnalysisQuery).
  return apiClient.post('/ANALYSIS/QUERY', queryBody);
};

// Exporta o cliente para usos simples (se houver rotas GET futuras)
export default apiClient;