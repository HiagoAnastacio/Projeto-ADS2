/**
 * ChartLogger.js
 *
 * Utilitário de Logging para Debug de Gráficos.
 * Padroniza as mensagens de log no console para facilitar o rastreamento
 * do fluxo de dados nos componentes de visualização (Recebimento -> Processamento -> Renderização).
 */

const ChartLogger = {
    /**
     * logReceive
     * 
     * Registra o momento em que o componente recebe dados via props.
     * Útil para verificar se os dados estão chegando do componente pai.
     * 
     * @param {string} componentName - Nome do componente (ex: WinRateChart)
     * @param {any} data - Dados recebidos via props
     */
    logReceive: (componentName, data) => {
        // Inicia um grupo colapsado no console para não poluir
        console.groupCollapsed(`[${componentName}] 1. RECEIVE - Dados Recebidos`);
        // Mostra os dados brutos
        console.log("Raw Data:", data);
        // Mostra o tipo dos dados para verificação rápida
        console.log("Tipo:", Array.isArray(data) ? `Array[${data.length}]` : typeof data);

        // Avisos visuais se os dados forem suspeitos
        if (!data) console.warn("ALERTA: Dados são nulos ou undefined.");
        else if (Array.isArray(data) && data.length === 0) console.warn("ALERTA: Array de dados está vazio.");

        // Fecha o grupo
        console.groupEnd();
    },

    /**
     * logProcess
     * 
     * Registra o resultado do processamento interno dos dados (formatação, pivotagem).
     * 
     * @param {string} componentName 
     * @param {Array} processedData - Dados finais prontos para o Recharts
     * @param {Array} errors - Lista de erros de parsing encontrados (opcional)
     */
    logProcess: (componentName, processedData, errors = []) => {
        // Verifica se há dados e erros
        const hasData = processedData && processedData.length > 0;
        const hasErrors = errors.length > 0;

        // Define estilo visual baseado no sucesso/erro
        const style = hasErrors ? "color: red; font-weight: bold;" : "color: green;";
        const label = hasErrors ? "COM ERROS" : "SUCESSO";

        // Inicia grupo
        console.groupCollapsed(`%c[${componentName}] 2. PROCESS - Processamento (${label})`, style);
        console.log("Dados Processados:", processedData);

        // Se houver erros, mostra tabela de erros
        if (hasErrors) {
            console.error(`Falha ao processar ${errors.length} itens.`);
            console.table(errors);
        } else {
            console.log("Todos os itens foram processados corretamente.");
        }
        console.groupEnd();
    },

    /**
     * logRender
     * 
     * Registra a decisão final de renderização do componente.
     * Informa se vai desenhar o gráfico, mostrar loading, vazio ou erro.
     * 
     * @param {string} componentName 
     * @param {string} status - Status da renderização ('RENDER_CHART', 'RENDER_EMPTY', 'RENDER_ERROR')
     * @param {string} reason - Explicação do motivo (ex: "Dados vazios")
     */
    logRender: (componentName, status, reason) => {
        // Define cores para diferentes status
        let color = "blue";
        if (status === 'RENDER_EMPTY') color = "orange";
        if (status === 'RENDER_ERROR') color = "red";

        // Loga a mensagem colorida
        console.log(`%c[${componentName}] 3. RENDER - Status: ${status}`, `color: ${color}; font-weight: bold;`);
        // Loga o motivo, se houver
        if (reason) console.log(`Motivo: ${reason}`);
    }
};

// Exporta o objeto logger
export default ChartLogger;
