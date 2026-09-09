from datetime import date

import pandas as pd
import streamlit as st

MANUTENCAO_CSV = "dados/manutencao.csv"
EQUIPAMENTOS_CSV = "dados/equipamentos.csv"

COLUNAS_MANUTENCAO = [
    "equipamento",
    "data_falha",
    "tempo_reparo_horas",
    "tipo_falha",
    "prioridade",
    "custo_reparo",
]
COLUNAS_EQUIPAMENTOS = ["equipamento", "tipo"]

st.set_page_config(
    page_title="Dashboard de Manutenção",
    page_icon="🔧",
    layout="wide"
)


def carregar_manutencao():
    try:
        return pd.read_csv(MANUTENCAO_CSV)
    except FileNotFoundError:
        return pd.DataFrame(columns=COLUNAS_MANUTENCAO)


def carregar_equipamentos():
    try:
        return pd.read_csv(EQUIPAMENTOS_CSV)
    except FileNotFoundError:
        return pd.DataFrame(columns=COLUNAS_EQUIPAMENTOS)


def salvar_manutencao(df):
    df.to_csv(MANUTENCAO_CSV, index=False)


def salvar_equipamentos(df):
    df.to_csv(EQUIPAMENTOS_CSV, index=False)


dados = carregar_manutencao()
equipamentos_cadastrados = carregar_equipamentos()

lista_equipamentos = sorted(
    set(dados["equipamento"].dropna()) | set(equipamentos_cadastrados["equipamento"].dropna())
)

st.title("🔧 Dashboard de Manutenção")
st.markdown("### Indicadores de desempenho da manutenção")

tab_dashboard, tab_cadastro = st.tabs(["📊 Dashboard", "➕ Cadastrar dados"])

with tab_cadastro:
    col_equipamento, col_manutencao = st.columns(2)

    with col_equipamento:
        st.subheader("🏭 Nova máquina/equipamento")
        with st.form("form_equipamento", clear_on_submit=True):
            nome_equipamento = st.text_input("Nome do equipamento")
            tipo_equipamento = st.selectbox(
                "Tipo", ["Bomba", "Compressor", "Motor", "Gerador", "Outro"]
            )
            enviar_equipamento = st.form_submit_button("Adicionar equipamento")

        if enviar_equipamento:
            nome_equipamento = nome_equipamento.strip()
            if not nome_equipamento:
                st.error("Informe o nome do equipamento.")
            elif nome_equipamento in lista_equipamentos:
                st.warning("Este equipamento já está cadastrado.")
            else:
                novo_equipamento = pd.DataFrame(
                    [{"equipamento": nome_equipamento, "tipo": tipo_equipamento}]
                )
                equipamentos_cadastrados = pd.concat(
                    [equipamentos_cadastrados, novo_equipamento], ignore_index=True
                )
                salvar_equipamentos(equipamentos_cadastrados)
                st.success(f"Equipamento '{nome_equipamento}' adicionado!")
                st.rerun()

    with col_manutencao:
        st.subheader("🛠️ Nova manutenção")
        if not lista_equipamentos:
            st.info("Cadastre um equipamento antes de registrar uma manutenção.")
        else:
            with st.form("form_manutencao", clear_on_submit=True):
                equipamento_sel = st.selectbox("Equipamento", lista_equipamentos)
                data_falha = st.date_input("Data da falha", value=date.today())
                tempo_reparo_horas = st.number_input(
                    "Tempo de reparo (horas)", min_value=0.0, step=0.5, format="%.1f"
                )
                tipo_falha = st.selectbox(
                    "Tipo de falha", ["Elétrica", "Mecânica", "Hidráulica", "Outro"]
                )
                prioridade = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])
                custo_reparo = st.number_input(
                    "Custo do reparo (R$)", min_value=0.0, step=50.0, format="%.2f"
                )
                enviar_manutencao = st.form_submit_button("Registrar manutenção")

            if enviar_manutencao:
                nova_manutencao = pd.DataFrame(
                    [{
                        "equipamento": equipamento_sel,
                        "data_falha": data_falha.isoformat(),
                        "tempo_reparo_horas": tempo_reparo_horas,
                        "tipo_falha": tipo_falha,
                        "prioridade": prioridade,
                        "custo_reparo": custo_reparo,
                    }]
                )
                dados = pd.concat([dados, nova_manutencao], ignore_index=True)
                salvar_manutencao(dados)
                st.success("Manutenção registrada com sucesso!")
                st.rerun()

with tab_dashboard:
    st.sidebar.header("🔎 Filtros")

    equipamentos = ["Todos"] + lista_equipamentos
    tipos_falha = ["Todos"] + sorted(dados["tipo_falha"].dropna().unique().tolist())
    prioridades = ["Todos"] + sorted(dados["prioridade"].dropna().unique().tolist())

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

    if dados_filtrados.empty:
        st.info("Nenhum registro de manutenção para os filtros selecionados.")
    else:
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
