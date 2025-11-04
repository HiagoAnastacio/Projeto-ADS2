// =======================================================================================
// MÓDULO GERENCIADOR DA API (CAMADA DE SERVIÇO) (v0.2.0 - Completo)
// =======================================================================================
// FLUXO E A LÓGICA:
// 1. Cria uma instância 'apiClient' do Axios com a baseURL correta da nossa API.
// 2. Define e exporta funções assíncronas reutilizáveis para CADA endpoint ou
//    conjunto de endpoints que o frontend precisa consumir.
// 3. Cada função retorna uma "Promise" do Axios, que será tratada (com async/await)
//    nos componentes React (ex: App.jsx).
//
// RAZÃO DE EXISTIR: Aplicar a Separação de Responsabilidades (SoC). Os componentes
// React (a "View") não devem saber *como* os dados são buscados ou de qual URL.
// Eles apenas chamam uma função deste serviço (ex: getHeroes()), tornando o
// código dos componentes mais limpo e a lógica da API mais fácil de manter.
// =======================================================================================

// Linha 17: Importa a biblioteca 'axios', que usamos para fazer requisições HTTP.
import axios from 'axios';

// Linha 20: Cria uma instância configurada do Axios.
const apiClient = axios.create({
  // Linha 22: CORREÇÃO: Define a URL base para a API FastAPI (conforme main.py).
  baseURL: 'http://localhost:8000/API/V1-DATA',
  // Linha 24: Define cabeçalhos padrão para garantir que a API saiba que estamos falando JSON.
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
});

// --- FUNÇÕES DE DIMENSÃO (Para filtros e mapeamento) ---

/**
 * Busca a lista completa de heróis da tabela 'hero'.
 * Usado pelo App.jsx para combinar nomes com estatísticas.
 */
export const getHeroes = () => {
  // Linha 38: Faz um GET para 'http://localhost:8000/api/v1/hero'
  return apiClient.get('/hero');
};

/**
 * Busca a lista completa de roles da tabela 'role'.
 * Usado pelo App.jsx para mapear 'role_id' para 'role_name'.
 */
export const getRoles = () => {
  // Linha 47: Faz um GET para 'http://localhost:8000/api/v1/role'
  return apiClient.get('/role');
};

/**
 * (FUNÇÃO ADICIONADA)
 * Busca a lista completa de ranks da tabela 'rank'.
 * Usado pelo App.jsx para popular o dropdown de filtro de Rank.
 */
export const getRanks = () => {
  // Linha 57: Faz um GET para 'http://localhost:8000/api/v1/rank'
  return apiClient.get('/rank');
};

/**
 * (FUNÇÃO ADICIONADA - CORRIGE O ERRO)
 * Busca a lista completa de modos de jogo da tabela 'game_mode'.
 * Usado pelo App.jsx para popular o dropdown de filtro de Modo de Jogo.
 */
export const getGameModes = () => {
  // Linha 67: Faz um GET para 'http://localhost:8000/api/v1/game_mode'
  return apiClient.get('/game_mode');
};

// --- FUNÇÕES DE DADOS DE FATO (Views _latest) ---

/**
 * (FUNÇÃO ADICIONADA)
 * Busca as estatísticas GERAIS (win/pick) mais recentes de CADA herói.
 * (Consome vw_hero_win_latest e vw_hero_pick_latest em paralelo)
 */
export const getLatestGeneralStats = () => {
  // Linha 80: Usa Promise.all para buscar ambas as views em paralelo. É mais rápido.
  return Promise.all([
    // Linha 82: Chama GET /api/v1/vw_hero_win_latest
    apiClient.get('/vw_hero_win_latest'),
    // Linha 84: Chama GET /api/v1/vw_hero_pick_latest
    apiClient.get('/vw_hero_pick_latest')
  ]);
};

/**
 * (FUNÇÃO ADICIONADA)
 * Busca as estatísticas POR RANK (win/pick) mais recentes de CADA herói.
 * (Consome vw_hero_rank_win_latest e vw_hero_rank_pick_latest)
 */
export const getLatestRankStats = () => {
  // Linha 95: Busca os dados de todas as estatísticas por rank em paralelo.
  return Promise.all([
    // Linha 97: Chama GET /api/v1/vw_hero_rank_win_latest
    apiClient.get('/vw_hero_rank_win_latest'),
    // Linha 99: Chama GET /api/v1/vw_hero_rank_pick_latest
    apiClient.get('/vw_hero_rank_pick_latest')
  ]);
};

/**
 * (FUNÇÃO ADICIONADA)
 * Busca as estatísticas POR MODO DE JOGO (win/pick) mais recentes de CADA herói.
 * (Consome vw_hero_gamemode_win_latest e vw_hero_gamemode_pick_latest)
 */
export const getLatestGameModeStats = () => {
  // Linha 110: Busca os dados de todas as estatísticas por modo de jogo em paralelo.
  return Promise.all([
    // Linha 112: Chama GET /api/v1/vw_hero_gamemode_win_latest
    apiClient.get('/vw_hero_game_mode_win_latest'),
    // Linha 114: Chama GET /api/v1/vw_hero_gamemode_pick_latest
    apiClient.get('/vw_hero_game_mode_pick_latest')
  ]);
};

// NOTA: As funções getLatestHeroWinRates e getLatestHeroPickRates que existiam
// no arquivo anterior foram removidas por serem redundantes. A função
// getLatestGeneralStats agora faz o trabalho de buscar ambas de uma vez.