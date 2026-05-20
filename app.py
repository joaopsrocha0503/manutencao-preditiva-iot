import os
import json
import pandas as pd
import streamlit as st

def main():
    st.set_page_config(
        page_title="Dashboard Preditivo - FEUP",
        page_icon="https://www.fe.up.pt/favicon.ico",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --- Estilos CSS profissionais ---
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }

            /* KPI Card Container */
            .kpi-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 16px;
                margin-bottom: 24px;
            }
            .kpi-card {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 20px 24px;
                border-left: 4px solid #2b6cb0;
            }
            .kpi-card.warning {
                border-left-color: #d69e2e;
            }
            .kpi-card.danger {
                border-left-color: #c53030;
            }
            .kpi-label {
                font-size: 0.8rem;
                font-weight: 600;
                color: #718096;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 6px;
            }
            .kpi-value {
                font-size: 2rem;
                font-weight: 700;
                color: #1a202c;
                line-height: 1.2;
            }
            .kpi-detail {
                font-size: 0.8rem;
                color: #4a5568;
                margin-top: 6px;
            }

            /* Section headers */
            .section-header {
                font-size: 1.1rem;
                font-weight: 600;
                color: #1a365d;
                border-bottom: 2px solid #e2e8f0;
                padding-bottom: 8px;
                margin-top: 32px;
                margin-bottom: 16px;
            }

            /* Dashboard title */
            .dashboard-title {
                font-size: 1.6rem;
                font-weight: 700;
                color: #1a365d;
                margin-bottom: 2px;
            }
            .dashboard-subtitle {
                font-size: 0.95rem;
                color: #4a5568;
                margin-bottom: 24px;
            }

            /* Sidebar */
            section[data-testid="stSidebar"] {
                background-color: #1a365d;
            }
            section[data-testid="stSidebar"] * {
                color: #e2e8f0 !important;
            }
            .sidebar-section {
                background: rgba(255,255,255,0.08);
                border-radius: 6px;
                padding: 14px 16px;
                margin-bottom: 12px;
            }
            .sidebar-label {
                font-size: 0.72rem;
                font-weight: 600;
                color: #a0aec0 !important;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            .sidebar-value {
                font-size: 0.9rem;
                font-weight: 500;
                color: #ffffff !important;
            }
            .status-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 0.78rem;
                font-weight: 600;
            }
            .status-ok {
                background: rgba(72,187,120,0.2);
                color: #48bb78 !important;
            }
            .status-alert {
                background: rgba(245,101,101,0.2);
                color: #fc8181 !important;
            }

            /* Industrial styling for Streamlit native metrics */
            div[data-testid="stMetric"] {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-left: 4px solid #3b82f6;
                padding: 15px 20px;
                border-radius: 6px;
                box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
            }
            div[data-testid="stMetricValue"] > div {
                color: #f8fafc;
                font-size: 2.2rem;
                font-weight: 700;
                font-family: monospace;
            }
            div[data-testid="stMetricLabel"] > div > div > p {
                color: #94a3b8;
                font-size: 0.85rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            div[data-testid="stMetricDelta"] > div > div > p {
                color: #cbd5e1 !important;
                font-size: 0.85rem;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- Caminhos ---
    base_dir = os.path.dirname(os.path.abspath(__file__))
    metrics_path = os.path.join(base_dir, 'output', 'analise', 'metricas_gestao.json')
    detections_path = os.path.join(base_dir, 'output', 'analise', 'detecoes.json')
    rul_path = os.path.join(base_dir, 'output', 'analise', 'previsao_rul.json')
    raw_data_path = os.path.join(base_dir, 'data', 'sensores_simulados.csv')

    # --- Verificação de ficheiros ---
    if not os.path.exists(metrics_path) or not os.path.exists(detections_path):
        st.error("Ficheiros de análise não encontrados. Execute o pipeline antes de abrir o dashboard.")
        st.code("python run_pipeline.py", language="bash")
        return

    # --- Carregar dados ---
    with open(metrics_path, 'r', encoding='utf-8') as f:
        metrics_data = json.load(f)
    with open(detections_path, 'r', encoding='utf-8') as f:
        detections_data = json.load(f)
        
    rul_data = None
    if os.path.exists(rul_path):
        with open(rul_path, 'r', encoding='utf-8') as f:
            rul_data = json.load(f)

    equipamentos_disponiveis = list(metrics_data.keys())
    
    # --- Sidebar ---
    with st.sidebar:
        st.markdown('<p style="font-size:1.2rem; font-weight:700; color:#ffffff !important; margin-bottom:20px;">FEUP — Manutenção Preditiva</p>', unsafe_allow_html=True)
        
        selected_machine = st.selectbox(
            "Equipamento a Monitorizar",
            equipamentos_disponiveis
        )
        
        kpi = metrics_data[selected_machine]['kpis_gestao']
        failures_list = metrics_data[selected_machine]['detalhes_eventos_falha']
        
        rul_machine_data = None
        if rul_data and selected_machine in rul_data:
            rul_machine_data = rul_data[selected_machine]

        st.markdown(f"""
            <div class="sidebar-section">
                <div class="sidebar-label">Equipamento Selecionado</div>
                <div class="sidebar-value">{selected_machine}</div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Localização</div>
                <div class="sidebar-value">Chão de Fábrica - Setor Principal</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 16px 0;'>", unsafe_allow_html=True)

        availability = kpi['disponibilidade_percentagem']
        if availability >= 90:
            badge = '<span class="status-badge status-ok">Operacional</span>'
        else:
            badge = '<span class="status-badge status-alert">Manutenção Requerida</span>'

        st.markdown(f"""
            <div class="sidebar-section">
                <div class="sidebar-label">Estado Atual</div>
                <div style="margin-top:6px;">{badge}</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="sidebar-section">
                <div class="sidebar-label">Período de Análise</div>
                <div class="sidebar-value">{kpi['periodo_analise_horas']}h de operação</div>
            </div>
        """, unsafe_allow_html=True)

    # --- Título ---
    st.title("Dashboard de Monitorização Preditiva - FEUP")
    st.subheader("Análise Inteligente e Indicadores de Gestão da Manutenção (Indústria 4.0)")
    st.markdown("---")

    # --- KPIs ---
    st.markdown("### Principais Indicadores Industriais (KPIs)")

    mtbf_val = f"{kpi['mtbf_horas']}h" if kpi['mtbf_horas'] else "N/A"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Disponibilidade", value=f"{kpi['disponibilidade_percentagem']}%", delta="Uptime / Tempo Total", delta_color="off")

    with col2:
        st.metric(label="Downtime Total", value=f"{kpi['downtime_total_minutos']} min", delta=f"Equivale a {kpi['downtime_total_horas']}h de paragem", delta_color="off")

    with col3:
        st.metric(label="MTTR", value=f"{kpi['mttr_minutos']} min", delta="Tempo médio de reparação", delta_color="off")

    with col4:
        prejuizo = kpi['downtime_total_horas'] * 500
        st.metric(label="Prejuízo de Inatividade", value=f"{prejuizo:.2f} €", delta="Custo estimado (500€/h)", delta_color="off")

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    col5, col6 = st.columns(2)
    
    with col5:
        st.metric(label="MTBF", value=mtbf_val, delta="Tempo médio entre falhas", delta_color="off")

    with col6:
        if rul_machine_data:
            rul_h = rul_machine_data['rul_horas']
            st.metric(label="RUL Estimado", value=f"{rul_h}h", delta="Vida Útil Restante", delta_color="off")
            
            # Barra de progresso visual
            pct = min(100, int((rul_h / 10.0) * 100))
            if pct <= 0:
                pct = 0
            
            st.progress(pct, text=f"Saúde Térmica: {pct}%")
            
            # Semáforo Dinâmico de Risco
            if pct > 50:
                st.success("🟢 Operação Segura")
            elif 20 <= pct <= 50:
                st.warning("🟡 Atenção: Intervenção Próxima")
            else:
                st.error("🔴 Falha Iminente")
        else:
            st.metric(label="RUL Estimado", value="N/A", delta="Máquina Saudável", delta_color="off")
            st.progress(100, text="Saúde Térmica: 100%")
            st.success("🟢 Operação Segura")

    # --- Integração de Ordens de Serviço (CMMS) ---
    st.markdown("---")
    st.markdown(f"### Gestão de Ordens de Serviço Ativas ({selected_machine})")
    
    safe_machine_name = selected_machine.replace(' ', '_').replace('/', '-')
    ordem_path = os.path.join(base_dir, 'output', 'analise', f'ordem_servico_urgente_{selected_machine}.txt')
    
    if os.path.exists(ordem_path):
        with open(ordem_path, 'r', encoding='utf-8') as f:
            ordem_conteudo = f.read()
        st.error(f"**ALERTA DE SISTEMA (CMMS): TICKET ABERTO**\n\n```text\n{ordem_conteudo}\n```")
    else:
        st.success("✅ Nenhuma Ordem de Serviço pendente para este equipamento.")

    # --- Gráficos ---
    st.markdown("---")
    st.markdown(f"### Telemetria e Alertas - {selected_machine}")

    tab1, tab2 = st.tabs(["Gráfico Analítico (Alta Definição)", "Gráfico Interativo"])

    with tab1:
        graph_path = os.path.join(base_dir, 'output', 'visualizacao', f'grafico_sensores_{safe_machine_name}.png')
        if os.path.exists(graph_path):
            st.image(graph_path, caption=f"Gráfico gerado pelo pipeline para {selected_machine}.", width="stretch")
        else:
            st.warning("Imagem do gráfico não encontrada.")

    with tab2:
        if os.path.exists(raw_data_path):
            df_raw = pd.read_csv(raw_data_path, encoding='utf-8-sig')
            df_raw['timestamp'] = pd.to_datetime(df_raw['timestamp'])
            
            df_machine = df_raw[df_raw['equipamento'] == selected_machine]

            variables = st.multiselect("Sensores a visualizar", ["temperatura", "vibracao"], default=["temperatura", "vibracao"])
            if variables:
                df_chart = df_machine.set_index('timestamp')[variables]
                st.line_chart(df_chart, height=350)
        else:
            st.warning("Dataset sensores_simulados.csv não encontrado.")

    # --- Tabela de eventos ---
    st.markdown("---")
    st.markdown("### Registo Detalhado de Falhas Preditivas (Eventos Contíguos)")

    if len(failures_list) > 0:
        df_failures = pd.DataFrame(failures_list)
        df_failures.columns = [
            "ID",
            "Início",
            "Fim",
            "Duração (min)",
            "Causa / Estado"
        ]

        st.dataframe(
            df_failures,
            width="stretch",
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn(width="small"),
                "Início": st.column_config.TextColumn(width="medium"),
                "Fim": st.column_config.TextColumn(width="medium"),
                "Duração (min)": st.column_config.NumberColumn(width="small"),
                "Causa / Estado": st.column_config.TextColumn(width="large")
            }
        )

        st.caption(
            f"O modelo Isolation Forest agrupou {len(detections_data)} leituras anómalas "
            f"em {len(failures_list)} eventos de falha distintos."
        )
        
        # Botão de Exportação (Data Delivery)
        csv_export = df_failures.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="Descarregar Histórico de Manutenção (CSV)",
            data=csv_export,
            file_name='historico_manutencao.csv',
            mime='text/csv',
        )
    else:
        st.info("Nenhum evento de falha registado nas últimas 24 horas.")

if __name__ == '__main__':
    main()
