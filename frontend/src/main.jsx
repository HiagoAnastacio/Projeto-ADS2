// Linha 1: Importa o 'StrictMode' do React (para ajudar a encontrar bugs).
import { StrictMode } from 'react'
// Linha 2: Importa a função para renderizar o React no DOM.
import { createRoot } from 'react-dom/client'
// Linha 3: Importa o CSS global.
import './index.css'
// Linha 4: Importa o componente "cérebro" da aplicação.
import App from './App.jsx'

// Linha 6: Encontra a <div> com id="root" no 'index.html' e a torna a raiz do React.
createRoot(document.getElementById('root')).render(
  // Linha 7: Ativa o StrictMode.
  <StrictMode>
    {/* Linha 8: Renderiza o componente App.jsx. */}
    <App />
  </StrictMode>,
)