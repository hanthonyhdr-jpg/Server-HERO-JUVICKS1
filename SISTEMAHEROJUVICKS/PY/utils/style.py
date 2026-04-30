def aplicar_estilo():
    st.markdown("""
        <style>
        /* Estiliza os botões de ação */
        .stButton>button {
            border-radius: 20px;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        /* Melhora o visual dos containers */
        [data-testid="stExpander"], div[data-testid="column"] {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 10px;
        }
        </style>
    """, unsafe_allow_html=True)