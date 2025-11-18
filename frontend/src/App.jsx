// Arquivo: frontend/src/App.jsx

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// Importando o layout do novo caminho
import Header from './components/layout/header/Header'; 
import Footer from './components/layout/footer/Footer';
// Importando a página principal do novo caminho
import DashboardPage from './pages/Dashboard'; 
import ScrollToTop from './utils/ScrollToTop'; 

function App() {
  
  return (
    <Router>
      {/* Componente utilitário para a funcionalidade de scroll suave */}
      <ScrollToTop /> 

      {/* O Header é fixo e compensa o padding-top na tag <main> */}
      <Header />

      {/* Padding superior para que o conteúdo não fique escondido sob o Header fixo (height-20 do tailwind) */}
      <main className="pt-20 min-h-screen bg-gray-50"> 
        <Routes>
          {/* Rota principal (página única) */}
          <Route path="/" element={<DashboardPage />} />
          
          {/* Exemplo de rota futura: */}
          {/* <Route path="/sobre" element={<AboutPage />} /> */}
        </Routes>
      </main>
      
      {/* O Footer no final de todo o conteúdo */}
      <Footer />
    </Router>
  );
}

export default App;