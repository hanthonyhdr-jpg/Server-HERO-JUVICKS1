import sqlite3
import os
import pandas as pd
from database import DB_DIR, DB_PATH

def exportar_bd_aprovados(ids_filtrados=None):
    """Gera um banco de dados contendo apenas orçamentos aprovados.
    Se ids_filtrados (lista) for fornecida, exporta apenas esses IDs.
    """
    
    export_path = os.path.join(DB_DIR, "orcamentos_aprovados.db")
    
    # Se o arquivo já existir, remove para recriar
    if os.path.exists(export_path):
        os.remove(export_path)

    # Conectar ao banco original para ler os dados
    conn_orig = sqlite3.connect(DB_PATH)
    
    # Lendo apenas orçamentos aprovados que POSSUEM cliente vinculado (JOIN)
    # Isso evita exportar orçamentos "órfãos" que não aparecem na tela do sistema
    if ids_filtrados is not None and len(ids_filtrados) > 0:
        ids_formatados = "','".join([str(i) for i in ids_filtrados])
        query_orc = f"""
            SELECT o.* FROM orcamentos o 
            INNER JOIN clientes c ON o.cliente_id = c.id 
            WHERE o.status = 'Aprovado' AND o.id IN ('{ids_formatados}')
        """
    else:
        query_orc = """
            SELECT o.* FROM orcamentos o 
            INNER JOIN clientes c ON o.cliente_id = c.id 
            WHERE o.status = 'Aprovado'
        """
        
    df_orcamentos = pd.read_sql_query(query_orc, conn_orig)
    
    if df_orcamentos.empty:
        conn_orig.close()
        return None  # Não há nada para exportar
    
    # Obter os IDs de clientes que possuem esses orçamentos aprovados
    ids_clientes = df_orcamentos['cliente_id'].unique().tolist()
    
    # Montar a query para clientes
    ids_formatados_cli = "','".join([str(i) for i in ids_clientes])
    query_clientes = f"SELECT * FROM clientes WHERE id IN ('{ids_formatados_cli}')"
    df_clientes = pd.read_sql_query(query_clientes, conn_orig)
    
    conn_orig.close()

    # Criando e conectando ao novo banco de dados
    conn_new = sqlite3.connect(export_path)
    
    # Exportar DataFrames para o novo SQLite
    df_orcamentos.to_sql("orcamentos", conn_new, index=False, if_exists="replace")
    df_clientes.to_sql("clientes", conn_new, index=False, if_exists="replace")
    
    conn_new.close()
    
    return export_path
