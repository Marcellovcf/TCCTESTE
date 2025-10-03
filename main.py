import streamlit as st
import pandas as pd
from pdf_extractor import PDFExtractor
from statistical_analyzer import StatisticalAnalyzer
from visualizations import VisualizationGenerator
from classifier import ParameterClassifier
from ishikawa_analyzer import IshikawaAnalyzer


def show_example_format() -> None:
    st.header("📋 Formato Esperado dos Laudos")
    st.markdown(
        """
        Os PDFs devem conter os seguintes parâmetros:

        - **Viscosidade a 40°C**: em cSt (centistokes)
        - **Teor de água**: em ppm (partes por milhão)
        - **Partículas >4 µm**: em part/mL
        - **Partículas >6 µm**: em part/mL  
        - **Partículas ≥14 µm**: em part/mL

        ### Limites Normativos:
        - Viscosidade: 2,0 – 4,1 cSt
        - Teor de água: ≤ 200 ppm
        - Partículas ≥14 µm: ≤ 20 part/mL

        ### Critérios de Divergência:
        - Viscosidade: ≥ 0,4 cSt de diferença
        - Teor de água: ≥ 50 ppm de diferença
        - Partículas ≥14 µm: ≥ 5 part/mL de diferença
        """
    )


def create_results_table(results: dict) -> pd.DataFrame:
    rows = []
    for param, r in results.items():
        rows.append(
            {
                "Parâmetro": param,
                "Média Mineradora": f"{r['mean_mineradora']:.2f}" if pd.notna(r['mean_mineradora']) else "-",
                "Média Distribuidora": f"{r['mean_distribuidora']:.2f}" if pd.notna(r['mean_distribuidora']) else "-",
                "Mediana Mineradora": f"{r['median_mineradora']:.2f}" if pd.notna(r['median_mineradora']) else "-",
                "Mediana Distribuidora": f"{r['median_distribuidora']:.2f}" if pd.notna(r['median_distribuidora']) else "-",
                "Desv. Padrão Mineradora": f"{r['std_mineradora']:.2f}" if pd.notna(r['std_mineradora']) else "-",
                "Desv. Padrão Distribuidora": f"{r['std_distribuidora']:.2f}" if pd.notna(r['std_distribuidora']) else "-",
                "Teste Aplicado": r['test_used'],
                "p-valor": f"{r['p_value']:.4f}" if pd.notna(r['p_value']) else "-",
                "Conclusão": "Rejeita H₀" if pd.notna(r['p_value']) and r['p_value'] < 0.05 else "Não Rejeita H₀",
            }
        )
    return pd.DataFrame(rows)


def display_classifications(classifications: dict) -> None:
    col1, col2, col3 = st.columns(3)
    normal_count = sum(1 for c in classifications.values() if c['classification'] == 'Normal')
    divergent_count = sum(1 for c in classifications.values() if c['classification'] == 'Divergente')
    out_count = sum(1 for c in classifications.values() if c['classification'] == 'Fora do Padrão')

    col1.metric("✅ Normal", normal_count)
    col2.metric("⚠️ Divergente", divergent_count)
    col3.metric("❌ Fora do Padrão", out_count)

    for param, c in classifications.items():
        emoji = {"Normal": "✅", "Divergente": "⚠️", "Fora do Padrão": "❌"}[c['classification']]
        st.write(f"{emoji} **{param}**: {c['classification']}")
        if c['details']:
            st.caption(c['details'])


def display_causes(causes: dict) -> None:
    icons = {
        "Método": "🔬",
        "Máquina": "⚙️",
        "Mão de obra": "👥",
        "Material": "📦",
        "Meio ambiente": "🌡️",
        "Medida": "📏",
    }
    for cat, items in causes.items():
        if not items:
            continue
        st.subheader(f"{icons.get(cat, '•')} {cat}")
        for it in items:
            st.write(f"- {it}")


def main() -> None:
    st.set_page_config(page_title="Análise de Laudos de Diesel", page_icon="🛢️", layout="wide")
    st.title("🛢️ Análise Estatística de Laudos de Diesel")
    st.markdown("### Comparativo entre Mineradora e Distribuidora")

    st.sidebar.header("📁 Upload de Arquivos")
    mineradora_files = st.sidebar.file_uploader(
        "Laudos da Mineradora (PDF)", type=["pdf"], accept_multiple_files=True, key="mineradora_files"
    )
    distribuidora_files = st.sidebar.file_uploader(
        "Laudos da Distribuidora (PDF)", type=["pdf"], accept_multiple_files=True, key="distribuidora_files"
    )

    if not mineradora_files or not distribuidora_files:
        st.info("👆 Envie os laudos para iniciar a análise.")
        show_example_format()
        return

    extractor = PDFExtractor()
    with st.spinner("Extraindo dados dos PDFs..."):
        mineradora_rows = []
        for f in mineradora_files:
            data = extractor.extract_parameters(f)
            if data:
                data['origem'] = 'Mineradora'
                mineradora_rows.append(data)

        distribuidora_rows = []
        for f in distribuidora_files:
            data = extractor.extract_parameters(f)
            if data:
                data['origem'] = 'Distribuidora'
                distribuidora_rows.append(data)

    if not mineradora_rows or not distribuidora_rows:
        st.error("Não foi possível extrair dados suficientes dos PDFs enviados.")
        return

    df = pd.DataFrame(mineradora_rows + distribuidora_rows)

    analyzer = StatisticalAnalyzer()
    results = analyzer.perform_analysis(df)

    st.header("📊 Resultados da Análise Estatística")
    st.dataframe(create_results_table(results), use_container_width=True)

    viz = VisualizationGenerator()
    st.header("📈 Visualizações")
    st.subheader("Boxplots comparativos")
    st.plotly_chart(viz.create_boxplots(df), use_container_width=True)

    st.subheader("Gráficos de probabilidade normal (QQ)")
    st.plotly_chart(viz.create_normality_plots(df), use_container_width=True)

    st.subheader("Pareto de divergências")
    st.plotly_chart(viz.create_pareto_chart(results), use_container_width=True)

    st.header("🎯 Diagnóstico de Divergências")
    classifier = ParameterClassifier()
    classifications = classifier.classify_parameters(df)
    display_classifications(classifications)

    st.header("🔍 Possíveis Causas (Ishikawa)")
    ishikawa = IshikawaAnalyzer()
    causes = ishikawa.suggest_causes(classifications)
    display_causes(causes)


if __name__ == "__main__":
    main()

