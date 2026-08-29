import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard de Manutenção",
    page_icon="🔧",
    layout="wide"
)

dados = pd.read_csv("dados/manutencao.csv")

st.title("🔧 Dashboard de Manutenção")
st.markdown("### Indicadores de desempenho da manutenção")

st.sidebar.header("🔎 Filtros")

equipamentos = ["Todos"] + sorted(dados["equipamento"].unique().tolist())
tipos_falha = ["Todos"] + sorted(dados["tipo_falha"].unique().tolist())
prioridades = ["Todos"] + sorted(dados["prioridade"].unique().tolist())

filtro_equipamento = st.sidebar.selectbox("Equipamento", equipamentos)
filtro_tipo = st.sidebar.selectbox("Tipo de falha", tipos_falha)
filtro_prioridade = st.sidebar.selectbox("Prioridade", prioridades)

dados_filtrados = dados.copy()

if filtro_equipamento != "Todos":
    dados_filtrados = dados_filtrados[
        dados_filtrados["equipamento"] == filtro_equipamento
    ]

if filtro_tipo != "Todos":
    dados_filtrados = dados_filtrados[
        dados_filtrados["tipo_falha"] == filtro_tipo
    ]

if filtro_prioridade != "Todos":
    dados_filtrados = dados_filtrados[
        dados_filtrados["prioridade"] == filtro_prioridade
    ]

quantidade_falhas = len(dados_filtrados)
tempo_total = dados_filtrados["tempo_reparo_horas"].sum()
custo_total = dados_filtrados["custo_reparo"].sum()
falhas_alta = len(
    dados_filtrados[dados_filtrados["prioridade"] == "Alta"]
)

mttr = (
    dados_filtrados["tempo_reparo_horas"].sum()
    / len(dados_filtrados)
    if len(dados_filtrados) > 0
    else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("🔴 Quantidade de falhas", quantidade_falhas)
col2.metric("⏱️ Horas de reparo", f"{tempo_total} h")
col3.metric("💰 Custo total", f"R$ {custo_total:,.2f}")
col4.metric("⏱️ MTTR", f"{mttr:.2f} h")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("⏱️ Tempo de reparo por equipamento")

    tempo_equipamento = (
        dados_filtrados.groupby("equipamento")["tempo_reparo_horas"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(tempo_equipamento)

with col2:
    st.subheader("🔧 Falhas por tipo")

    falhas_tipo = dados_filtrados["tipo_falha"].value_counts()

    st.bar_chart(falhas_tipo)

st.divider()

st.subheader("💰 Custo de manutenção por equipamento")

custo_equipamento = (
    dados_filtrados.groupby("equipamento")["custo_reparo"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(custo_equipamento)

st.divider()

st.subheader("📋 Registros de manutenção")

st.dataframe(dados_filtrados, width="stretch")
