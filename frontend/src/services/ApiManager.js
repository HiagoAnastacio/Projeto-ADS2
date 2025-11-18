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

import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/API/V1-DATA',
  headers: {
    'Content-Type': 'application/json'
  }
});

export const fetchAnalyticsData = (queryBody) => {
  return apiClient.post('/ANALYSIS/QUERY', queryBody);
};

export default apiClient;