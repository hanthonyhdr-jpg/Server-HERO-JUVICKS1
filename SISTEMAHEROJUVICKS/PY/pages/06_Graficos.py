import streamlit as st
import os
import sys

# Adiciona a raiz do projeto ao sys.path para garantir que 'utils' e 'database' sejam encontrados
if getattr(sys, 'frozen', False):
    sys.path.append(sys._MEIPASS)
else:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from database import buscar_dados
from datetime import datetime, timedelta

# --- UTILS: Carregamento Seguro de JSON ---
def safe_loads(json_str, fallback=[]):
    if not json_str or json_str == 'null':
        return fallback
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Tenta uma recuperação básica se for um erro de truncamento comum
        try:
            # Se termina abruptamente, tenta fechar os colchetes/chaves
            if json_str.startswith('[') and not json_str.endswith(']'):
                return json.loads(json_str + '"]') # Tenta fechar uma string e o array
        except:
            pass
        return fallback

from TEMAS.moderno import apply_modern_style
from utils.auth_manager import verificar_autenticacao, obter_dados_empresa, verificar_permissao_modulo, verificar_nivel_acesso

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
emp_nome, logo_src = obter_dados_empresa()
st.set_page_config(page_title="Dashboard | Performance", layout="wide", page_icon="📈")
apply_modern_style(logo_url=logo_src, nome_empresa=emp_nome)

# LOGIN PROTECTION
verificar_autenticacao()
verificar_nivel_acesso(["ADMIN", "GERENTE", "VENDEDOR"])
verificar_permissao_modulo("Dashboard")

# --- 2. BUSCA DE DADOS (COM JOIN PARA FILTROS GEOGRÁFICOS) ---
query = """
    SELECT o.total, o.status, o.data, o.itens_json, o.vendedor, o.custo_producao,
           c.nome as cliente, c.cidade, c.bairro, c.estado
    FROM orcamentos o
    JOIN clientes c ON o.cliente_id = c.id
"""
df = buscar_dados(query)

if not df.empty:
    # Tratamento de dados
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df = df.dropna(subset=['data'])
    df['total'] = pd.to_numeric(df['total'], errors='coerce').fillna(0)
    df['custo_producao'] = pd.to_numeric(df['custo_producao'], errors='coerce').fillna(0)
    df['status'] = df['status'].astype(str).str.strip().str.capitalize()
    
    def calc_lucro(row):
        # Se já existe custo real lançado no financeiro, usa ele
        if row['custo_producao'] > 0:
            return row['total'] - row['custo_producao']
            
        # Caso contrário, tenta uma estimativa baseada na engenharia de produtos
        try:
            itens = safe_loads(row['itens_json'])
            custo_total_orc = 0
            for i in itens:
                qtd = float(i.get('qtd', 1))
                dim = i.get('dimensoes', '-')
                fator = 1.0
                if 'x' in dim:
                    try:
                        partes = dim.split('x')
                        fator = float(partes[0]) * float(partes[1])
                    except: fator = 1.0
                
                c_proc = float(i.get('custo_processamento', 0))
                c_depr = float(i.get('depreciacao', 0))
                
                c_insumos = 0
                comp_json = i.get('composicao_json', '[]')
                if comp_json:
                    try:
                        comp_lista = json.loads(comp_json)
                        c_insumos = sum(float(item.get('Custo (R$)', 0)) for item in comp_lista)
                    except: c_insumos = 0
                
                custo_total_orc += (c_proc + c_depr + c_insumos) * qtd * fator
            return row['total'] - custo_total_orc
        except: return row['total']
    
    df['lucro'] = df.apply(calc_lucro, axis=1)

    # --- 3. FILTROS NA SIDEBAR ---
    st.sidebar.header("🎯 Filtros Avançados")
    
    # Filtro de Calendário (Range)
    hoje = datetime.now()
    inicio_ano = hoje - timedelta(days=365)
    
    st.sidebar.subheader("📅 Período")
    data_range = st.sidebar.date_input(
        "Selecione o Intervalo",
        value=(inicio_ano, hoje),
        help="Selecione data inicial e final no calendário"
    )
    
    if isinstance(data_range, tuple) and len(data_range) == 2:
        start_date, end_date = data_range
        df_filtered = df[(df['data'].dt.date >= start_date) & (df['data'].dt.date <= end_date)].copy()
    else:
        df_filtered = df.copy()

    st.sidebar.divider()
    st.sidebar.subheader("📍 Região")
    
    # Filtro de Cidade
    cidades = ["Todas"] + sorted(df_filtered['cidade'].dropna().unique().tolist())
    sel_cidade = st.sidebar.selectbox("Filtrar por Cidade", cidades)
    if sel_cidade != "Todas":
        df_filtered = df_filtered[df_filtered['cidade'] == sel_cidade]
        
    # Filtro de Bairro (Dinâmico conforme a cidade)
    bairros = ["Todos"] + sorted(df_filtered['bairro'].dropna().unique().tolist())
    sel_bairro = st.sidebar.selectbox("Filtrar por Bairro", bairros)
    if sel_bairro != "Todos":
        df_filtered = df_filtered[df_filtered['bairro'] == sel_bairro]

    st.sidebar.divider()
    vendedores = ["Todos"] + sorted(df_filtered['vendedor'].unique().tolist())
    sel_vend = st.sidebar.selectbox("Filtrar Vendedor", vendedores)
    if sel_vend != "Todos":
        df_filtered = df_filtered[df_filtered['vendedor'] == sel_vend]

    # --- 4. TÍTULO E MÉTRICAS ---
    st.title("🚀 Dashboard de Performance")
    
    # Métricas Principais
    df_aprov = df_filtered[df_filtered['status'] == 'Aprovado']
    total_fat = df_aprov['total'].sum()
    total_lucro = df_aprov['lucro'].sum()
    ticket_medio = df_aprov['total'].mean() if not df_aprov.empty else 0
    tx_conversao = (len(df_aprov) / len(df_filtered) * 100) if not df_filtered.empty else 0
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Faturamento Bruto", f"R$ {total_fat:,.2f}")
    m2.metric("Lucro Líquido Est.", f"R$ {total_lucro:,.2f}")
    m3.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
    m4.metric("Taxa de Conversão", f"{tx_conversao:.1f}%")

    st.divider()

    # --- 5. GRÁFICOS ---
    with st.expander("📈 Evolução e Análise Geográfica", expanded=True):
        c_g1, c_g2 = st.columns(2)
        
        with c_g1:
            st.write("#### Evolução por Data")
            df_evo = df_filtered.groupby(df_filtered['data'].dt.date).agg({'total': 'sum', 'lucro': 'sum'}).reset_index()
            fig_evolucao = go.Figure()
            fig_evolucao.add_trace(go.Scatter(x=df_evo['data'], y=df_evo['total'], name='Fat.', line=dict(color='#00d4ff', width=3)))
            fig_evolucao.add_trace(go.Bar(x=df_evo['data'], y=df_evo['lucro'], name='Lucro', marker_color='#2ecc71', opacity=0.6))
            fig_evolucao.update_layout(template="plotly_dark", height=350, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_evolucao, use_container_width=True)

        with c_g2:
            st.write("#### Faturamento por Cidade")
            fat_cid = df_aprov.groupby('cidade')['total'].sum().reset_index()
            fig_cid = px.pie(fat_cid, values='total', names='cidade', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_cid.update_layout(template="plotly_dark", height=350, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_cid, use_container_width=True)

    with st.expander("⚖️ Funil e Maiores Clientes", expanded=True):
        c_g3, c_g4 = st.columns(2)
        
        with c_g3:
            st.write("#### Funil de Vendas (Status)")
            status_count = df_filtered['status'].value_counts().reset_index()
            fig_funil = px.funnel(status_count, x='count', y='status', color='status')
            fig_funil.update_layout(template="plotly_dark", height=350, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_funil, use_container_width=True)

        with c_g4:
            st.write("#### Top 10 Clientes")
            top_cli = df_aprov.groupby('cliente')['total'].sum().nlargest(10).reset_index()
            fig_cli = px.bar(top_cli, x='total', y='cliente', orientation='h', color='total')
            fig_cli.update_layout(template="plotly_dark", height=350, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_cli, use_container_width=True)

    with st.expander("📦 Análise por Produto", expanded=True):
        # Lógica para extrair ranking de produtos do JSON
        ranking_prod = {}
        for _, row in df_filtered.iterrows():
            itens = safe_loads(row['itens_json'])
            for item in itens:
                nome = item.get('produto') or item.get('item') or item.get('nome') or "Não Identificado"
                qtd = float(item.get('qtd', 0))
                subtotal = float(item.get('subtotal', 0))
                if nome not in ranking_prod:
                    ranking_prod[nome] = {"qtd": 0, "valor": 0}
                ranking_prod[nome]["qtd"] += qtd
                ranking_prod[nome]["valor"] += subtotal
        
        if ranking_prod:
            df_prod = pd.DataFrame.from_dict(ranking_prod, orient='index').reset_index()
            df_prod.columns = ['Produto', 'Qtd Vendida', 'Valor Total']
            
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                st.write("#### Produtos mais Vendidos (Qtd)")
                fig_pq = px.bar(df_prod.nlargest(10, 'Qtd Vendida'), x='Qtd Vendida', y='Produto', orientation='h', color='Qtd Vendida', color_continuous_scale='Viridis')
                fig_pq.update_layout(template="plotly_dark", height=350, showlegend=False)
                st.plotly_chart(fig_pq, use_container_width=True)
            
            with c_p2:
                st.write("#### Faturamento por Produto (R$)")
                fig_pv = px.bar(df_prod.nlargest(10, 'Valor Total'), x='Valor Total', y='Produto', orientation='h', color='Valor Total', color_continuous_scale='Magma')
                fig_pv.update_layout(template="plotly_dark", height=350, showlegend=False)
                st.plotly_chart(fig_pv, use_container_width=True)
        else:
            st.info("Não foi possível processar os dados dos produtos.")

    # --- 6. TABELA ---
    with st.expander("📄 Dados Filtrados"):
        st.dataframe(df_filtered.drop(columns=['itens_json']), use_container_width=True, hide_index=True)

else:
    st.info("💡 Sem dados no período selecionado.")

