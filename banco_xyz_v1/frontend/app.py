from __future__ import annotations

import uuid
import pandas as pd
import streamlit as st

from services.api import (
    approve_report,
    deliver_report,
    download_pdf,
    generate_report,
    get_clients,
)

# ==========================================================
# CONFIGURACAO
# ==========================================================
st.set_page_config(
    page_title="Banco XYZ | Relatorios de Investimentos com IA",
    page_icon="🏦",
    layout="wide",
)

# ==========================================================
# SESSAO
# ==========================================================
def init_session_state() -> None:
    st.session_state.setdefault("result", None)
    st.session_state.setdefault("pdf_path", None)
    st.session_state.setdefault("thread_id", f"thread-{uuid.uuid4().hex[:8]}")
    st.session_state.setdefault("approver_name", "Analista Humano")
    st.session_state.setdefault("selected_client_id", None)
    st.session_state.setdefault("dark_mode", False)


init_session_state()

# ==========================================================
# TEMA NTT DATA
# ==========================================================
LIGHT_THEME = {
    "bg": "#F5F8FC",
    "card": "#FFFFFF",
    "card_soft": "#EEF4FB",
    "text": "#0A2540",
    "muted": "#5B6B7A",
    "primary": "#003B8E",
    "secondary": "#005EB8",
    "accent": "#00A3E0",
    "border": "#D9E2EC",
    "success": "#17A34A",
    "warning": "#F59E0B",
    "danger": "#DC2626",
    "sidebar_bg": "linear-gradient(180deg, #003B8E 0%, #005EB8 100%)",
    "sidebar_text": "#FFFFFF",
    "hero_text": "#FFFFFF",
    "badge_bg": "rgba(255, 255, 255, 0.16)",
    "badge_text": "#FFFFFF",
    "input_bg": "#FFFFFF",
    "profile_item_bg": "#FFFFFF",
    "profile_value": "#0A2540",
    "timeline_done_bg": "rgba(23, 163, 74, 0.08)",
    "timeline_done_border": "#17A34A",
}

DARK_THEME = {
    "bg": "#081120",
    "card": "#0F1B2D",
    "card_soft": "#13243A",
    "text": "#EAF2FB",
    "muted": "#AFC2D6",
    "primary": "#4DA3FF",
    "secondary": "#00A3E0",
    "accent": "#7DD3FC",
    "border": "#223A57",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#F87171",
    "sidebar_bg": "linear-gradient(180deg, #001B44 0%, #003B8E 100%)",
    "sidebar_text": "#FFFFFF",
    "hero_text": "#FFFFFF",
    "badge_bg": "rgba(255, 255, 255, 0.14)",
    "badge_text": "#FFFFFF",
    "input_bg": "#0F1B2D",
    "profile_item_bg": "#13243A",
    "profile_value": "#EAF2FB",
    "timeline_done_bg": "rgba(34, 197, 94, 0.10)",
    "timeline_done_border": "#22C55E",
}

theme = DARK_THEME if st.session_state["dark_mode"] else LIGHT_THEME


def inject_theme() -> None:
    st.markdown(
        f"""
        <style>
            .stApp {{
                background: {theme["bg"]};
                color: {theme["text"]};
            }}

            .block-container {{
                padding-top: 1.2rem;
                padding-bottom: 2rem;
                max-width: 1400px;
            }}

            [data-testid="stSidebar"] {{
                background: {theme["sidebar_bg"]};
                border-right: 1px solid {theme["border"]};
            }}

            [data-testid="stSidebar"] * {{
                color: {theme["sidebar_text"]} !important;
            }}

            .hero {{
                background: linear-gradient(90deg, {theme["primary"]}, {theme["accent"]});
                padding: 28px 30px;
                border-radius: 24px;
                margin-bottom: 20px;
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
            }}

            .hero-title {{
                color: {theme["hero_text"]};
                font-size: 2rem;
                font-weight: 800;
                margin-bottom: 8px;
            }}

            .hero-subtitle {{
                color: rgba(255,255,255,0.94);
                font-size: 1rem;
                margin-bottom: 16px;
            }}

            .section-title {{
                font-size: 1.08rem;
                font-weight: 800;
                color: {theme["primary"]};
                margin-bottom: 10px;
            }}

            .card {{
                background: {theme["card"]};
                border: 1px solid {theme["border"]};
                border-radius: 20px;
                padding: 20px;
                margin-bottom: 16px;
                box-shadow: 0 8px 24px rgba(16, 24, 40, 0.08);
            }}

            .kpi {{
                background: {theme["card"]};
                border: 1px solid {theme["border"]};
                border-radius: 18px;
                padding: 18px;
                text-align: center;
                box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
            }}

            .kpi-label {{
                color: {theme["muted"]};
                font-size: 0.92rem;
                margin-bottom: 6px;
            }}

            .kpi-value {{
                color: {theme["primary"]};
                font-size: 1.5rem;
                font-weight: 800;
            }}

            .profile-item {{
                background: {theme["profile_item_bg"]};
                border-left: 5px solid {theme["accent"]};
                border-radius: 14px;
                padding: 12px 14px;
                margin-bottom: 10px;
                box-shadow: 0 6px 16px rgba(0, 0, 0, 0.04);
            }}

            .profile-label {{
                font-size: 0.76rem;
                font-weight: 700;
                color: {theme["muted"]};
                text-transform: uppercase;
                letter-spacing: 0.04em;
                margin-bottom: 4px;
            }}

            .profile-value {{
                font-size: 0.98rem;
                color: {theme["profile_value"]};
                font-weight: 600;
            }}

            .pill {{
                display: inline-block;
                padding: 7px 11px;
                border-radius: 999px;
                background: rgba(0, 163, 224, 0.10);
                color: {theme["primary"]};
                font-size: 0.82rem;
                font-weight: 700;
                margin-right: 6px;
                margin-bottom: 6px;
                border: 1px solid transparent;
            }}

            .timeline {{
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin: 12px 0 20px 0;
            }}

            .timeline-step {{
                background: {theme["card_soft"]};
                color: {theme["muted"]};
                border: 1px solid {theme["border"]};
                border-radius: 16px;
                padding: 12px 14px;
                font-size: 0.9rem;
                font-weight: 700;
                min-width: 140px;
                box-shadow: 0 6px 16px rgba(0, 0, 0, 0.04);
            }}

            .timeline-step.active {{
                background: {theme["primary"]};
                color: white;
                border-color: {theme["primary"]};
            }}

            .timeline-step.done {{
                background: {theme["timeline_done_bg"]};
                color: {theme["text"]};
                border-color: {theme["timeline_done_border"]};
            }}

            .small-badge {{
                display: inline-block;
                padding: 6px 12px;
                border-radius: 999px;
                background: {theme["badge_bg"]};
                color: {theme["badge_text"]};
                border: 1px solid rgba(255,255,255,0.18);
                font-size: 0.8rem;
                font-weight: 700;
                margin-right: 6px;
                margin-top: 8px;
            }}

            div[data-testid="stMetric"] {{
                background: {theme["card"]};
                border: 1px solid {theme["border"]};
                border-radius: 18px;
                padding: 10px;
            }}

            div[data-testid="stDownloadButton"] button,
            div[data-testid="stButton"] button {{
                border-radius: 14px !important;
                font-weight: 700 !important;
                border: 1px solid {theme["border"]} !important;
                background: {theme["primary"]} !important;
                color: white !important;
            }}

            div[data-testid="stDownloadButton"] button:hover,
            div[data-testid="stButton"] button:hover {{
                background: {theme["secondary"]} !important;
                color: white !important;
                border-color: {theme["secondary"]} !important;
            }}

            div[data-testid="stTextInput"] input,
            div[data-testid="stTextArea"] textarea {{
                background: {theme["input_bg"]} !important;
                color: {theme["text"]} !important;
                border: 1px solid {theme["border"]} !important;
            }}

            div[data-baseweb="select"] > div {{
                background: {theme["input_bg"]} !important;
                color: {theme["text"]} !important;
                border-color: {theme["border"]} !important;
            }}

            div[data-testid="stDataFrame"] {{
                border-radius: 18px;
                overflow: hidden;
                border: 1px solid {theme["border"]};
            }}

            .muted {{
                color: {theme["muted"]};
            }}

            hr {{
                border: none;
                border-top: 1px solid {theme["border"]};
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_theme()

# ==========================================================
# HELPERS UI
# ==========================================================
def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## Painel")
        dark = st.toggle("Modo noturno", value=st.session_state["dark_mode"])
        if dark != st.session_state["dark_mode"]:
            st.session_state["dark_mode"] = dark
            st.rerun()

        st.markdown("---")
        st.markdown("## Banco XYZ")
        st.markdown("### Painel operacional")
        st.markdown("---")
        st.caption("Fluxo assistido para geracao, aprovacao e emissao de relatorios.")
        st.markdown("**Etapas**")
        st.markdown("1. Selecionar cliente")
        st.markdown("2. Gerar rascunho")
        st.markdown("3. Validar conteudo")
        st.markdown("4. Aprovar emissao")
        st.markdown("5. Baixar PDF")
        st.markdown("6. Enviar por e-mail ou WhatsApp")
        st.markdown("### NTT DATA theme")
        st.markdown("---")
        st.caption("Identidade visual NTT DATA")
        st.markdown(
            f'<div class="small-badge">Primaria {theme["primary"]}</div>',
            unsafe_allow_html=True,
        )


def render_hero() -> None:
    title = "Banco XYZ | Relatorios de Investimentos com IA"
    subtitle = "Geracao assistida • Aprovacao humana • PDF • Entrega por e-mail e WhatsApp"

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
            <span class="small-badge">NTT DATA Design</span>
            <span class="small-badge">LangGraph</span>
            <span class="small-badge">RAG</span>
            <span class="small-badge">Human in the Loop</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def open_card(title: str, subtitle: str | None = None) -> None:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)


def close_card() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def normalize_result_for_ui(result: dict | None) -> dict:
    result = result or {}
    return {
        "status": result.get("status", "-"),
        "thread_id": result.get("thread_id", "-"),
        "run_id": result.get("run_id", "-"),
        "report_preview": result.get("report_preview") or result.get("report_text", ""),
        "report_summary": result.get("report_summary")
        or result.get("report_preview")
        or result.get("report_text", ""),
        "report_detailed": result.get("report_detailed") or result.get("report_text", ""),
        "artifacts": result.get("artifacts", {}),
        "audit_log": result.get("audit_log", []),
        "error_message": result.get("error_message") or result.get("error"),
        "pdf_path": result.get("pdf_path"),
    }


def format_status_label(status: str) -> str:
    mapping = {
        "draft_generated": "Rascunho gerado",
        "awaiting_human_approval": "Aguardando aprovacao",
        "approved": "Aprovado",
        "rejected": "Rejeitado",
        "delivered": "Entregue",
        "-": "-",
    }
    return mapping.get(status, status.replace("_", " ").title())


def render_kpis(total_clients: int, raw_result: dict | None) -> None:
    result = normalize_result_for_ui(raw_result)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="kpi">
                <div class="kpi-label">Clientes</div>
                <div class="kpi-value">{total_clients}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="kpi">
                <div class="kpi-label">Status</div>
                <div class="kpi-value" style="font-size:1rem;">{format_status_label(result["status"])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        has_pdf = "Sim" if result.get("pdf_path") or st.session_state.get("pdf_path") else "Nao"
        st.markdown(
            f"""
            <div class="kpi">
                <div class="kpi-label">PDF disponivel</div>
                <div class="kpi-value">{has_pdf}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_profile_card(chosen: dict) -> None:
    profile_fields = [
        ("Nome", chosen.get("nome", "-")),
        ("Perfil", chosen.get("perfil_suitability", "-")),
        ("Objetivo", chosen.get("objetivo_investimento", "-")),
        ("Horizonte", chosen.get("horizonte_tempo", "-")),
        ("Patrimonio total", chosen.get("patrimonio_total", "-")),
        ("Valor aplicado", chosen.get("valor_aplicado", "-")),
        ("Evento recente", chosen.get("evento_ocorrido", "-")),
    ]

    for label, value in profile_fields:
        st.markdown(
            f"""
            <div class="profile-item">
                <div class="profile-label">{label}</div>
                <div class="profile-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    produtos = chosen.get("produtos_ativos", []) or []
    if produtos:
        st.markdown("**Produtos ativos**")
        pills = "".join(f"<span class='pill'>{produto}</span>" for produto in produtos)
        st.markdown(pills, unsafe_allow_html=True)


def _build_line_df(portfolio_history: list[dict], ibov_history: list[dict]) -> pd.DataFrame:
    portfolio_df = pd.DataFrame(portfolio_history)
    ibov_df = pd.DataFrame(ibov_history)

    if not portfolio_df.empty:
        portfolio_df = portfolio_df.rename(columns={"portfolio": "Carteira"})
        if "date" in portfolio_df.columns:
            portfolio_df["date"] = pd.to_datetime(portfolio_df["date"], errors="coerce")
            portfolio_df = portfolio_df.set_index("date")

    if not ibov_df.empty:
        ibov_df = ibov_df.rename(columns={"close": "Ibovespa"})
        if "date" in ibov_df.columns:
            ibov_df["date"] = pd.to_datetime(ibov_df["date"], unit="s", errors="coerce")
            ibov_df = ibov_df.set_index("date")

    if portfolio_df.empty and ibov_df.empty:
        return pd.DataFrame()

    if portfolio_df.empty:
        return ibov_df[["Ibovespa"]]

    if ibov_df.empty:
        return portfolio_df[["Carteira"]]

    return portfolio_df.join(ibov_df[["Ibovespa"]], how="outer").sort_index()


def _build_allocation_df(allocation: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(allocation)
    if df.empty:
        return df
    expected = [c for c in ["classe", "peso"] if c in df.columns]
    return df[expected]


def render_report_tabs(result: dict, chosen: dict) -> None:
    report_summary = result.get("report_summary") or result.get("report_preview", "")
    report_detailed = result.get("report_detailed") or result.get("report_preview", "")
    artifacts = result.get("artifacts", {}) or {}

    benchmarks = artifacts.get("benchmarks", {}) or {}
    current_rates = benchmarks.get("current_rates", {}) or {}
    ibov_history = benchmarks.get("ibov_history", []) or []
    portfolio_history = benchmarks.get("portfolio_history", []) or []
    chart_recommendation = artifacts.get("chart_recommendation", {}) or {}
    allocation = artifacts.get("recommended_allocation", []) or []

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Resumo", "Detalhado", "Benchmarks e Graficos", "Artefatos"]
    )

    with tab1:
        st.subheader("Versao resumida")
        st.write(report_summary)

        c1, c2, c3 = st.columns(3)
        c1.metric("Selic", current_rates.get("selic") or "-")
        c2.metric("CDI", current_rates.get("cdi") or "-")
        c3.metric("IPCA", current_rates.get("ipca") or "-")

    with tab2:
        st.subheader("Versao detalhada")
        st.write(report_detailed)

    with tab3:
        st.subheader("Comparacao e demonstracao visual")
        st.caption(
            f"Perfil: {chosen.get('perfil_suitability', '-')}"
            f" | Foco: {chart_recommendation.get('focus', '-')}"
        )

        profile = str(chosen.get("perfil_suitability", "")).lower()
        line_df = _build_line_df(portfolio_history, ibov_history)
        alloc_df = _build_allocation_df(allocation)

        if "conserv" in profile:
            st.markdown("#### Evolucao estavel / preservacao")
            if not line_df.empty:
                numeric_cols = [c for c in line_df.columns if c in ["Carteira", "Ibovespa"]]
                if numeric_cols:
                    st.area_chart(line_df[numeric_cols])

            if not alloc_df.empty and {"classe", "peso"}.issubset(alloc_df.columns):
                st.markdown("#### Distribuicao da carteira")
                st.bar_chart(alloc_df.set_index("classe"))

        elif "moder" in profile:
            st.markdown("#### Carteira x benchmarks")
            if not line_df.empty:
                st.line_chart(line_df)

            if not alloc_df.empty and {"classe", "peso"}.issubset(alloc_df.columns):
                st.markdown("#### Alocacao por classe")
                st.bar_chart(alloc_df.set_index("classe"))

        else:
            st.markdown("#### Performance e maior oscilacao")
            if not line_df.empty:
                st.line_chart(line_df)

            if not alloc_df.empty and {"classe", "peso"}.issubset(alloc_df.columns):
                st.markdown("#### Exposicao por classe")
                st.bar_chart(alloc_df.set_index("classe"))

            if not line_df.empty and "Carteira" in line_df.columns and "Ibovespa" in line_df.columns:
                risk_return = pd.DataFrame(
                    {
                        "Metrica": ["Carteira", "Ibovespa"],
                        "Retorno proxy": [
                            line_df["Carteira"].dropna().pct_change().mean(),
                            line_df["Ibovespa"].dropna().pct_change().mean(),
                        ],
                        "Risco proxy": [
                            line_df["Carteira"].dropna().pct_change().std(),
                            line_df["Ibovespa"].dropna().pct_change().std(),
                        ],
                    }
                ).set_index("Metrica")
                st.markdown("#### Proxy de risco x retorno")
                st.bar_chart(risk_return)

    with tab4:
        st.subheader("Artefatos tecnicos")
        st.json(artifacts)


def render_timeline(status: str) -> None:
    steps = [
        ("draft_generated", "Rascunho"),
        ("awaiting_human_approval", "Aprovacao"),
        ("approved", "PDF"),
        ("delivered", "Entrega"),
    ]
    order = {
        "-": 0,
        "draft_generated": 1,
        "awaiting_human_approval": 2,
        "approved": 3,
        "delivered": 4,
        "rejected": 2,
    }
    current = order.get(status, 0)

    html = ["<div class='timeline'>"]
    for code, label in steps:
        threshold = order.get(code, 0)
        if current > threshold:
            css_class = "done"
        elif current == threshold and current > 0:
            css_class = "active"
        else:
            css_class = ""
        html.append(f"<div class='timeline-step {css_class}'>{label}</div>")
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def save_report_result(result: dict) -> None:
    st.session_state["result"] = result
    st.session_state["pdf_path"] = result.get("pdf_path")


def get_preferred_channel(client: dict) -> str:
    raw = str(client.get("canal_preferencia", "")).lower()
    if "whats" in raw:
        return "whatsapp"
    return "email"


# ==========================================================
# UI
# ==========================================================
render_sidebar()
render_hero()

# ==========================================================
# BACKEND
# ==========================================================
try:
    clients = get_clients()
except Exception as exc:
    st.error(f"Nao foi possivel conectar ao backend: {exc}")
    st.stop()

if not clients:
    st.warning("Nenhum cliente disponivel no momento.")
    st.stop()

client_df = pd.DataFrame(clients)
raw_result = st.session_state.get("result")
render_kpis(len(clients), raw_result)

options = {
    (
        f"{client['id_pessoa']} | "
        f"{client['nome']} | "
        f"{client.get('perfil_suitability', '-')} | "
        f"{client.get('objetivo_investimento', '-')}"
    ): client
    for client in clients
}

default_option_index = 0
if st.session_state["selected_client_id"] is not None:
    client_ids = [client["id_pessoa"] for client in clients]
    if st.session_state["selected_client_id"] in client_ids:
        default_option_index = client_ids.index(st.session_state["selected_client_id"])

left, right = st.columns([1.05, 1.45], gap="large")

with left:
    open_card(
        "Configuracao do relatorio",
        "Selecione o cliente, revise os dados e execute o fluxo.",
    )

    selected_label = st.selectbox(
        "Selecione o cliente",
        list(options.keys()),
        index=default_option_index,
    )
    chosen = options[selected_label]
    st.session_state["selected_client_id"] = chosen["id_pessoa"]

    thread_id = st.text_input("Thread ID", value=st.session_state["thread_id"])
    st.session_state["thread_id"] = thread_id

    approver_name = st.text_input("Aprovador", value=st.session_state["approver_name"])
    st.session_state["approver_name"] = approver_name

    st.markdown("---")
    st.markdown("<div class='section-title'>Perfil do cliente</div>", unsafe_allow_html=True)
    render_profile_card(chosen)

    if st.button("Gerar rascunho", use_container_width=True):
        with st.spinner("Executando geracao do relatorio..."):
            try:
                result = generate_report(chosen["id_pessoa"], thread_id)
                save_report_result(result)
                st.success("Rascunho gerado com sucesso.")
                st.rerun()
            except Exception as exc:
                st.error(f"Erro ao gerar rascunho: {exc}")

    close_card()

with right:
    open_card("Base de clientes", "Visao resumida dos dados disponiveis.")
    cols_to_show = [
        "id_pessoa",
        "nome",
        "perfil_suitability",
        "objetivo_investimento",
        "horizonte_tempo",
        "valor_aplicado",
        "patrimonio_total",
        "canal_preferencia",
    ]
    existing_cols = [c for c in cols_to_show if c in client_df.columns]
    st.dataframe(client_df[existing_cols], use_container_width=True, hide_index=True)
    close_card()

# ==========================================================
# RESULTADO DO FLUXO
# ==========================================================
raw_result = st.session_state.get("result")

if raw_result:
    result = normalize_result_for_ui(raw_result)

    render_timeline(result["status"])

    st.markdown("## Resultado do fluxo")
    m1, m2, m3 = st.columns(3)
    m1.metric("Status", format_status_label(result["status"]))
    m2.metric("Thread", result["thread_id"])
    m3.metric("Run", result["run_id"])

    preview_col, side_col = st.columns([1.5, 1], gap="large")

    with preview_col:
        open_card("Relatorio e analise")
        render_report_tabs(result, chosen)
        close_card()

    with side_col:
        open_card("Rastreabilidade")
        with st.expander("Artefatos do RAG e alocacao"):
            st.json(result["artifacts"])

        with st.expander("Trilha de auditoria"):
            st.json(result["audit_log"])

        if result.get("error_message"):
            st.error(result["error_message"])

        close_card()

    if result["status"] == "awaiting_human_approval":
        open_card("Aprovacao humana")

        notes = st.text_area(
            "Observacoes do aprovador",
            value="Aprovado para emissao do PDF.",
            height=120,
        )

        col_approve, col_reject = st.columns(2)

        with col_approve:
            if st.button("Aprovar e emitir PDF", use_container_width=True):
                with st.spinner("Emitindo PDF..."):
                    try:
                        new_result = approve_report(
                            thread_id=result["thread_id"],
                            approved=True,
                            approval_notes=notes,
                            approver_name=approver_name,
                        )
                        save_report_result(new_result)
                        st.success("Relatorio aprovado com sucesso.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Erro ao aprovar relatorio: {exc}")

        with col_reject:
            if st.button("Rejeitar relatorio", use_container_width=True):
                try:
                    new_result = approve_report(
                        thread_id=result["thread_id"],
                        approved=False,
                        approval_notes=notes,
                        approver_name=approver_name,
                    )
                    save_report_result(new_result)
                    st.warning("Relatorio rejeitado.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Erro ao rejeitar relatorio: {exc}")

        close_card()

# ==========================================================
# DOWNLOAD E ENTREGA
# ==========================================================
pdf_path = (
    (st.session_state.get("result") or {}).get("pdf_path")
    or st.session_state.get("pdf_path")
)

if pdf_path:
    st.markdown("## PDF e entrega")

    c1, c2 = st.columns([1, 1], gap="large")

    with c1:
        open_card("Download do PDF")
        try:
            pdf_bytes = download_pdf(pdf_path)
            st.success("PDF gerado com sucesso.")
            st.download_button(
                label="Baixar PDF final",
                data=pdf_bytes,
                file_name=pdf_path.split("/")[-1],
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"PDF gerado, mas nao foi possivel baixa-lo automaticamente: {exc}")
            st.code(pdf_path)
        close_card()

    with c2:
        open_card("Enviar ao cliente")

        preferred_channel = get_preferred_channel(chosen)

        channel = st.radio(
            "Canal de envio",
            options=["email", "whatsapp"],
            index=0 if preferred_channel == "email" else 1,
            horizontal=True,
        )

        requested_by = st.text_input(
            "Solicitado por",
            value=approver_name,
        )

        if channel == "email":
            st.caption("Entrega por e-mail via backend.")
        else:
            st.caption("Entrega por WhatsApp via backend.")

        if st.button(f"Enviar por {channel}", use_container_width=True):
            with st.spinner(f"Enviando por {channel}..."):
                try:
                    delivery_result = deliver_report(
                        thread_id=(st.session_state.get("result") or {}).get("thread_id"),
                        channel=channel,
                        requested_by=requested_by,
                    )
                    st.success(f"Entrega solicitada com sucesso via {channel}.")
                    st.json(delivery_result)
                except Exception as exc:
                    st.error(f"Erro ao enviar por {channel}: {exc}")

        close_card()
