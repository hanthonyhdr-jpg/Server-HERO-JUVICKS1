import streamlit as st
import streamlit.components.v1 as components

def injetar_atalhos():
    # Mapeamento: Tecla -> Nome do Arquivo (sem o número e extensão)
    # O Streamlit converte "01_👥_Gestão_de_Clientes.py" na URL "Gestão_de_Clientes"
    
    js_code = """
    <script>
    const doc = window.parent.document;
    
    // Adiciona o ouvinte de eventos apenas uma vez
    if (!doc.keyListenerAttached) {
        doc.addEventListener('keydown', function(e) {
            
            // Mapeamento das teclas para as URLs das páginas
            const map = {
                'F2': 'Gestão_de_Clientes',
                'F3': 'Catálogo_Produtos',
                'F4': 'Novo_Orçamento',
                'F5': 'Histórico_Vendas',     // Cuidado: F5 costuma ser Atualizar página
                'F6': 'Emitir_Contratos',
                'F7': 'Dashboard_Gerencial',
                'F8': 'Ficha_de_Produção',
                'F9': 'Configurações',
                'F10': 'Backup_e_Dados',
                'F11': 'Gestão_de_Usuários'  // Cuidado: F11 costuma ser Tela Cheia
            };

            if (map[e.key]) {
                e.preventDefault(); // Impede a ação padrão do navegador (ex: F5 atualizar)
                
                // Pega a URL base atual (http://localhost:8501/)
                const baseUrl = window.parent.location.origin;
                
                // Redireciona para a nova página
                window.parent.location.href = baseUrl + '/' + map[e.key];
            }
        });
        doc.keyListenerAttached = true;
    }
    </script>
    """
    # Injeta o Javascript invisível na página
    components.html(js_code, height=0, width=0)