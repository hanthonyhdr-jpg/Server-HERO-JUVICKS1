import streamlit as st

from database import buscar_dados


ORCAMENTOS_CACHE_KEY = "orcamentos_cache_version"
FINANCEIRO_CACHE_KEY = "financeiro_cache_version"
CLIENTES_CACHE_KEY = "clientes_cache_version"


def get_orcamentos_cache_version():
    return int(st.session_state.get(ORCAMENTOS_CACHE_KEY, 0))


def bump_orcamentos_cache_version():
    st.session_state[ORCAMENTOS_CACHE_KEY] = get_orcamentos_cache_version() + 1


def get_financeiro_cache_version():
    return int(st.session_state.get(FINANCEIRO_CACHE_KEY, 0))


def bump_financeiro_cache_version():
    st.session_state[FINANCEIRO_CACHE_KEY] = get_financeiro_cache_version() + 1


def get_clientes_cache_version():
    return int(st.session_state.get(CLIENTES_CACHE_KEY, 0))


def bump_clientes_cache_version():
    st.session_state[CLIENTES_CACHE_KEY] = get_clientes_cache_version() + 1


CONFIG_CACHE_KEY = "config_cache_version"


def get_config_cache_version():
    return int(st.session_state.get(CONFIG_CACHE_KEY, 0))


def bump_config_cache_version():
    st.session_state[CONFIG_CACHE_KEY] = get_config_cache_version() + 1


@st.cache_data(show_spinner=False)
def cached_buscar_dados(sql, params=(), version=0):
    return buscar_dados(sql, params)
