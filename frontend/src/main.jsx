/**
 * main.jsx
 *
 * Ponto de entrada principal da aplicação React.
 * Responsável por encontrar o elemento raiz no HTML e renderizar a árvore de componentes.
 */

// Importa o modo estrito do React para destacar potenciais problemas na aplicação
import { StrictMode } from 'react'
// Importa a função createRoot para inicializar a renderização concorrente do React 18+
import { createRoot } from 'react-dom/client'
// Importa os estilos globais da aplicação
import './index.css'
// Importa o componente raiz da aplicação
import App from './App.jsx'

// Seleciona o elemento DOM com id 'root' e cria a raiz do React
createRoot(document.getElementById('root')).render(
  // Envolve a aplicação no StrictMode para verificações adicionais durante o desenvolvimento
  <StrictMode>
    <App />
  </StrictMode>,
)