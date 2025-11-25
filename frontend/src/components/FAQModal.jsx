/**
 * FAQModal.jsx
 *
 * Componente Modal para exibir Perguntas Frequentes (FAQ) e informações sobre o projeto.
 * Utiliza um overlay fixo e centraliza o conteúdo na tela.
 */

// Importa ícone de fechar (X)
import { X } from 'lucide-react';

/**
 * Componente FAQModal
 * 
 * @param {boolean} isOpen - Controla a visibilidade do modal
 * @param {function} onClose - Função chamada ao solicitar o fechamento
 */
const FAQModal = ({ isOpen, onClose }) => {
    // Se não estiver aberto, não renderiza nada (null)
    if (!isOpen) return null;

    return (
        // Container principal do modal com z-index alto e overlay
        <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
            <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">

                {/* Overlay de fundo escuro com opacidade */}
                <div
                    className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
                    aria-hidden="true"
                    onClick={onClose} // Fecha ao clicar no fundo
                ></div>

                {/* Espaçador para centralização vertical em telas maiores */}
                <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

                {/* Conteúdo do Modal (Card Branco) */}
                <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                    <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                        <div className="sm:flex sm:items-start">
                            <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                                {/* Cabeçalho do Modal */}
                                <div className="flex justify-between items-center mb-4">
                                    <h3 className="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                                        Perguntas Frequentes & Sobre
                                    </h3>
                                    {/* Botão de Fechar (X) */}
                                    <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
                                        <X className="h-6 w-6" />
                                    </button>
                                </div>

                                {/* Corpo do Modal com as Perguntas */}
                                <div className="mt-2 space-y-4">
                                    {/* Item 1: Dados Oficiais */}
                                    <div className="bg-orange-50 p-3 rounded-md border border-orange-100">
                                        <p className="font-semibold text-orange-800 text-sm">Os dados são oficiais?</p>
                                        <p className="text-sm text-gray-600 mt-1">
                                            Não. Os dados são coletados via extratores independentes e não possuem vínculo direto com a Blizzard Entertainment.
                                        </p>
                                    </div>

                                    {/* Item 2: Frequência de Atualização */}
                                    <div className="bg-blue-50 p-3 rounded-md border border-blue-100">
                                        <p className="font-semibold text-blue-800 text-sm">Com que frequência os dados são atualizados?</p>
                                        <p className="text-sm text-gray-600 mt-1">
                                            Nossos pipelines de dados rodam semanalmente, todas as <strong>Terças-feiras</strong>.
                                        </p>
                                    </div>

                                    {/* Rodapé Informativo */}
                                    <div className="text-xs text-gray-500 mt-4 pt-4 border-t border-gray-100">
                                        <p>Desenvolvido para fins educacionais e de análise da comunidade.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    {/* Botões de Ação do Modal */}
                    <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                        <button
                            type="button"
                            className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-orange-600 text-base font-medium text-white hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 sm:ml-3 sm:w-auto sm:text-sm"
                            onClick={onClose}
                        >
                            Entendi
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Exporta o componente FAQModal
export default FAQModal;
