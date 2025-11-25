/**
 * Footer.jsx
 *
 * Rodapé da Aplicação.
 * Exibe informações de copyright, links sociais e acesso ao FAQ.
 */

// Importa hook de estado
import { useState } from 'react';
// Importa ícones
import { Github, Mail, HelpCircle, Calendar } from 'lucide-react';
// Importa modal de FAQ
import FAQModal from '../components/FAQModal';

const Footer = () => {
    // Estado para controlar a abertura do modal de FAQ
    const [isFAQOpen, setIsFAQOpen] = useState(false);

    return (
        // Rodapé fixo na base ou ao final do conteúdo
        <footer className="bg-white border-t border-gray-200 mt-auto">
            <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                <div className="md:flex md:items-center md:justify-between">

                    {/* Lado Esquerdo: Copyright e Aviso de Atualização */}
                    <div className="flex flex-col space-y-2">
                        <p className="text-base text-gray-400">
                            &copy; {new Date().getFullYear()} OverWatch Analytics. Todos os direitos reservados.
                        </p>
                        <div className="flex items-center text-sm text-gray-500">
                            <Calendar className="h-4 w-4 mr-1 text-orange-500" />
                            <span>Dados atualizados semanalmente (Terças-feiras)</span>
                        </div>
                    </div>

                    {/* Lado Direito: Links Sociais e Botão FAQ */}
                    <div className="mt-8 md:mt-0 flex space-x-6">
                        {/* Link GitHub */}
                        <a
                            href="https://github.com/HiagoAnastacio"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-gray-400 hover:text-gray-500 flex items-center transition-colors"
                        >
                            <span className="sr-only">GitHub</span>
                            <Github className="h-6 w-6" />
                        </a>

                        {/* Link Email */}
                        <a
                            href="mailto:hiagoanastacios@gmail.com"
                            className="text-gray-400 hover:text-gray-500 flex items-center transition-colors"
                        >
                            <span className="sr-only">Email</span>
                            <Mail className="h-6 w-6" />
                        </a>

                        {/* Botão FAQ */}
                        <button
                            onClick={() => setIsFAQOpen(true)}
                            className="text-gray-400 hover:text-orange-600 flex items-center transition-colors group"
                            title="FAQ / Sobre"
                        >
                            <span className="sr-only">FAQ</span>
                            <HelpCircle className="h-6 w-6 group-hover:scale-110 transition-transform" />
                            <span className="ml-2 text-sm font-medium hidden sm:inline-block">FAQ / Sobre</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* Renderiza o Modal de FAQ (controlado pelo estado isFAQOpen) */}
            <FAQModal isOpen={isFAQOpen} onClose={() => setIsFAQOpen(false)} />
        </footer>
    );
};

// Exporta o componente Footer
export default Footer;
