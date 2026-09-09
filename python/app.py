from datetime import date

import pandas as pd
import plotly.graph_objects as go
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

# Paleta: hue sequencial por métrica (tempo x custo) + cores de status fixas para prioridade.
COR_TEMPO = "#2a78d6"
COR_CUSTO = "#eb6834"
COR_ALTA = "#d03b3b"
COR_MEDIA = "#fab219"
COR_BAIXA = "#0ca30c"
COR_GRADE = "#e1e0d9"
COR_TEXTO = "#52514e"
FONTE = "system-ui, -apple-system, 'Segoe UI', sans-serif"

st.set_page_config(
    page_title="Dashboard de Manutenção",
    page_icon="🔧",
    layout="wide"
)

st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        background-color: rgba(120, 120, 120, 0.06);
        border-radius: 10px;
        padding: 1rem 1rem 0.75rem 1rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
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


def calcular_mtbf_dias(df):
    """Tempo médio entre falhas (dias), a partir do intervalo entre falhas de cada equipamento."""
    intervalos = []
    for _, grupo in df.groupby("equipamento"):
        datas = pd.to_datetime(grupo["data_falha"]).sort_values()
        if len(datas) > 1:
            intervalos.extend(datas.diff().dropna().dt.days.tolist())
    return sum(intervalos) / len(intervalos) if intervalos else 0.0


def layout_base(fig, altura):
    fig.update_layout(
        height=altura,
        margin=dict(l=10, r=30, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONTE, color=COR_TEXTO, size=13),
        showlegend=False,
    )
    fig.update_xaxes(gridcolor=COR_GRADE, zeroline=False)
    fig.update_yaxes(gridcolor=COR_GRADE, zeroline=False)
    return fig


def grafico_barras_h(serie, cor, formato_valor):
    """Barras horizontais finas, uma única cor, com rótulo no fim de cada barra."""
    fig = go.Figure(
        go.Bar(
            x=serie.values,
            y=serie.index,
            orientation="h",
            marker_color=cor,
            text=[formato_valor(v) for v in serie.values],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{text}<extra></extra>",
        )
    )
    fig.update_yaxes(autorange="reversed")
    maior_valor = serie.max() if len(serie) > 0 else 0
    fig.update_xaxes(showticklabels=False, range=[0, maior_valor * 1.2 if maior_valor > 0 else 1])
    return layout_base(fig, altura=70 + 48 * len(serie))


def grafico_falhas_por_prioridade(dados_filtrados):
    """Barras horizontais com as cores de status fixas (Alta=crítico, Média=alerta, Baixa=ok)."""
    ordem = ["Alta", "Média", "Baixa"]
    cores = {"Alta": COR_ALTA, "Média": COR_MEDIA, "Baixa": COR_BAIXA}
    icones = {"Alta": "🔴", "Média": "🟡", "Baixa": "🟢"}

    contagem = dados_filtrados["prioridade"].value_counts().reindex(ordem).fillna(0)

    fig = go.Figure(
        go.Bar(
            x=contagem.values,
            y=[f"{icones[p]} {p}" for p in contagem.index],
            orientation="h",
            marker_color=[cores[p] for p in contagem.index],
            text=[int(v) for v in contagem.values],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{text} falha(s)<extra></extra>",
        )
    )
    fig.update_yaxes(autorange="reversed")
    maior_valor = contagem.max() if len(contagem) > 0 else 0
    fig.update_xaxes(showticklabels=False, range=[0, maior_valor * 1.2 if maior_valor > 0 else 1])
    return layout_base(fig, altura=230)


def grafico_evolucao_mensal(dados_filtrados):
    """Linha com a quantidade de falhas por mês, para mostrar a tendência ao longo do tempo."""
    serie = dados_filtrados.copy()
    serie["mes"] = pd.to_datetime(serie["data_falha"]).dt.to_period("M").astype(str)
    falhas_mes = serie.groupby("mes").size().sort_index()

    fig = go.Figure(
        go.Scatter(
            x=falhas_mes.index,
            y=falhas_mes.values,
            mode="lines+markers",
            line=dict(color=COR_TEMPO, width=2),
            marker=dict(size=8, color=COR_TEMPO),
            hovertemplate="%{x}: %{y} falha(s)<extra></extra>",
        )
    )
    fig.update_yaxes(rangemode="tozero")
    fig.update_xaxes(type="category")
    return layout_base(fig, altura=280)


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

    if dados_filtrados.empty:
        st.info("Nenhum registro de manutenção para os filtros selecionados.")
    else:
        quantidade_falhas = len(dados_filtrados)
        tempo_total = dados_filtrados["tempo_reparo_horas"].sum()
        custo_total = dados_filtrados["custo_reparo"].sum()
        falhas_alta = len(dados_filtrados[dados_filtrados["prioridade"] == "Alta"])

        mttr = tempo_total / quantidade_falhas
        mtbf_dias = calcular_mtbf_dias(dados_filtrados)
        mtbf_horas = mtbf_dias * 24
        disponibilidade = (
            mtbf_horas / (mtbf_horas + mttr) * 100 if (mtbf_horas + mttr) > 0 else 0
        )
        custo_medio = custo_total / quantidade_falhas
        pct_alta = falhas_alta / quantidade_falhas * 100

        linha1 = st.columns(4)
        linha1[0].metric("🔴 Quantidade de falhas", quantidade_falhas)
        linha1[1].metric("⏱️ MTTR (tempo médio de reparo)", f"{mttr:.2f} h")
        linha1[2].metric("📅 MTBF (tempo médio entre falhas)", f"{mtbf_dias:.1f} dias")
        linha1[3].metric("✅ Disponibilidade", f"{disponibilidade:.1f} %")

        linha2 = st.columns(3)
        linha2[0].metric("💰 Custo total", f"R$ {custo_total:,.2f}")
        linha2[1].metric("💵 Custo médio por manutenção", f"R$ {custo_medio:,.2f}")
        linha2[2].metric("⚠️ Falhas de alta prioridade", f"{pct_alta:.1f} %")

        st.divider()

        st.subheader("📈 Evolução de falhas por mês")
        st.plotly_chart(grafico_evolucao_mensal(dados_filtrados), width="stretch")

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🚦 Falhas por prioridade")
            st.plotly_chart(grafico_falhas_por_prioridade(dados_filtrados), width="stretch")

        with col2:
            st.subheader("🔧 Falhas por tipo")
            falhas_tipo = dados_filtrados["tipo_falha"].value_counts().sort_values()
            st.plotly_chart(
                grafico_barras_h(falhas_tipo, COR_TEMPO, lambda v: f"{int(v)}"),
                width="stretch",
            )

        st.divider()

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("⏱️ Tempo de reparo por equipamento")
            tempo_equipamento = (
                dados_filtrados.groupby("equipamento")["tempo_reparo_horas"]
                .sum()
                .sort_values()
            )
            st.plotly_chart(
                grafico_barras_h(tempo_equipamento, COR_TEMPO, lambda v: f"{v:.1f} h"),
                width="stretch",
            )

        with col4:
            st.subheader("💰 Custo de manutenção por equipamento")
            custo_equipamento = (
                dados_filtrados.groupby("equipamento")["custo_reparo"]
                .sum()
                .sort_values()
            )
            st.plotly_chart(
                grafico_barras_h(custo_equipamento, COR_CUSTO, lambda v: f"R$ {v:,.0f}"),
                width="stretch",
            )

        st.divider()

        st.subheader("📋 Registros de manutenção")
        st.dataframe(dados_filtrados, width="stretch")
