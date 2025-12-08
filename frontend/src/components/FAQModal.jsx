/**
 * FAQModal.jsx
 *
 * Componente Modal para exibir Perguntas Frequentes (FAQ) e informações sobre o projeto.
 * 
 * MELHORIAS (PORTAL):
 * - Utiliza `createPortal` para renderizar o modal diretamente no `document.body`.
 *   Isso previne problemas de 'stacking context' (z-index) e overflow de containers pais.
 * - Gerencia o scroll da página (lock) quando aberto.
 */

import { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';

/**
 * Componente FAQModal
 * 
 * @param {boolean} isOpen - Controla a visibilidade do modal
 * @param {function} onClose - Função chamada ao solicitar o fechamento
 */
const FAQModal = ({ isOpen, onClose }) => {

    // --- Efeito de Bloqueio de Scroll ---
    // Impede que a página de fundo role enquanto o modal está aberto.
    useEffect(() => {
        if (isOpen) {
            // Desabilita o scroll do body
            document.body.style.overflow = 'hidden';
        } else {
            // Restaura o scroll
            document.body.style.overflow = 'unset';
        }

        // Cleanup function: garante que o scroll volta ao normal se o componente desmontar
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [isOpen]);

    // Se não estiver aberto, não renderiza nada
    if (!isOpen) return null;

    // --- Renderização via Portal ---
    // Renderiza o JSX fora da hierarquia do componente pai, direto no body.
    return createPortal(
        <div className="fixed inset-0 z-[9999] overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
            <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">

                {/* Overlay de fundo escuro com opacidade REDUZIDA para efeito de Popup */}
                {/* bg-black/40 permite ver o conteúdo atrás. backdrop-blur-sm suaviza, mas não bloqueia a visão totalmente */}
                <div
                    className="fixed inset-0 bg-black/40 transition-opacity backdrop-blur-[2px]"
                    aria-hidden="true"
                    onClick={onClose}
                ></div>

                {/* Espaçador para centralização vertical */}
                <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

                {/* Conteúdo do Modal */}
                {/* z-index relativo ao overlay pai */}
                <div className="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full relative animate-in fade-in zoom-in-95 duration-200">

                    <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                        <div className="sm:flex sm:items-start">
                            <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">

                                {/* Cabeçalho */}
                                <div className="flex justify-between items-center mb-6">
                                    <h3 className="text-xl leading-6 font-bold text-gray-900" id="modal-title">
                                        Perguntas Frequentes
                                    </h3>
                                    <button
                                        onClick={onClose}
                                        className="p-1 rounded-full hover:bg-gray-100 text-gray-400 hover:text-gray-500 transition-colors"
                                    >
                                        <X className="h-6 w-6" />
                                    </button>
                                </div>

                                {/* Conteúdo */}
                                <div className="mt-2 space-y-4">
                                    <div className="bg-orange-50/50 p-4 rounded-xl border border-orange-100">
                                        <p className="font-bold text-orange-900 text-sm mb-1">Os dados são oficiais?</p>
                                        <p className="text-sm text-slate-600 leading-relaxed">
                                            Sim. Todos os dados apresentados são extraídos utilizando APIs públicas oficiais, processando informações reais de partidas e perfis de jogadores.
                                        </p>
                                    </div>

                                    <div className="bg-blue-50/50 p-4 rounded-xl border border-blue-100">
                                        <p className="font-bold text-blue-900 text-sm mb-1">Frequência de Atualização</p>
                                        <p className="text-sm text-slate-600 leading-relaxed">
                                            Nossos pipelines de dados rodam automaticamente todas as <strong>Segundas-feiras</strong>, garantindo insights frescos para a semana.
                                        </p>
                                    </div>

                                    {/* Nova Seção: Sobre o Projeto */}
                                    <div className="bg-emerald-50/50 p-4 rounded-xl border border-emerald-100">
                                        <p className="font-bold text-emerald-900 text-sm mb-1">Sobre o Projeto</p>
                                        <p className="text-sm text-slate-600 leading-relaxed">
                                            Este sistema foi desenvolvido integralmente por um único desenvolvedor como parte de um <strong>Trabalho de Conclusão de Curso (TCC)</strong>.
                                            <br className="mb-2" />
                                            O objetivo é demonstrar competências em Engenharia de Dados e Desenvolvimento Fullstack, criando uma ferramenta útil para a comunidade.
                                        </p>
                                    </div>

                                    <div className="text-center pt-6 pb-2">
                                        <p className="text-xs text-slate-400 uppercase tracking-widest font-semibold">Overwatch Meta Analyzer v1.0 • Projeto Acadêmico</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Footer com Botão */}
                    <div className="bg-gray-50 px-4 py-4 sm:px-6 sm:flex sm:flex-row-reverse border-t border-gray-100">
                        <button
                            type="button"
                            className="w-full inline-flex justify-center rounded-xl border border-transparent shadow-sm px-6 py-2.5 bg-slate-900 text-base font-medium text-white hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 sm:ml-3 sm:w-auto sm:text-sm transition-all"
                            onClick={onClose}
                        >
                            Entendi
                        </button>
                    </div>
                </div>
            </div>
        </div>,
        document.body // Alvo do Portal
    );
};

export default FAQModal;
