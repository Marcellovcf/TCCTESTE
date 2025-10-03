THIS SHOULD BE A LINTER ERRORimport numpy as np
import pandas as pd
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class VisualizationGenerator:
    def __init__(self) -> None:
        self.colors = {'Mineradora': '#1f77b4', 'Distribuidora': '#ff7f0e'}

    def create_boxplots(self, df: pd.DataFrame) -> go.Figure:
        params = [
            'viscosidade_40c',
            'teor_agua',
            'particulas_4um',
            'particulas_6um',
            'particulas_14um',
        ]
        available = [p for p in params if p in df.columns]
        if not available:
            return go.Figure()

        fig = make_subplots(rows=1, cols=len(available), subplot_titles=available, horizontal_spacing=0.08)
        for i, p in enumerate(available, start=1):
            for origin in ['Mineradora', 'Distribuidora']:
                y = df[df['origem'] == origin][p].dropna()
                fig.add_box(y=y, name=origin, marker_color=self.colors[origin], showlegend=(i == 1), row=1, col=i)
        fig.update_layout(title="Comparação por Parâmetro", boxmode='group', height=500)
        return fig

    def create_normality_plots(self, df: pd.DataFrame) -> go.Figure:
        params = [
            'viscosidade_40c',
            'teor_agua',
            'particulas_4um',
            'particulas_6um',
            'particulas_14um',
        ]
        available = [p for p in params if p in df.columns]
        if not available:
            return go.Figure()

        n = len(available)
        cols = min(3, n)
        rows = (n + cols - 1) // cols
        fig = make_subplots(rows=rows, cols=cols, subplot_titles=available, vertical_spacing=0.12, horizontal_spacing=0.08)

        for idx, p in enumerate(available):
            r = idx // cols + 1
            c = idx % cols + 1
            for origin in ['Mineradora', 'Distribuidora']:
                y = np.sort(df[df['origem'] == origin][p].dropna().values)
                if len(y) < 3:
                    continue
                q_theo = stats.norm.ppf((np.arange(1, len(y) + 1)) / (len(y) + 1))
                fig.add_scatter(x=q_theo, y=y, mode='markers', name=f"{origin}-{p}", marker=dict(color=self.colors[origin]), showlegend=(idx == 0), row=r, col=c)
            # Reference line using mineradora stats when available
            y_ref = df[df['origem'] == 'Mineradora'][p].dropna().values
            if len(y_ref) >= 2:
                mean = float(np.mean(y_ref))
                std = float(np.std(y_ref))
                x_line = np.array([stats.norm.ppf(0.01), stats.norm.ppf(0.99)])
                y_line = mean + std * x_line
                fig.add_scatter(x=x_line, y=y_line, mode='lines', line=dict(color='red', dash='dash'), name='Linha Normal', showlegend=(idx == 0), row=r, col=c)

        fig.update_layout(title="Gráficos de Probabilidade Normal (QQ)", height=380 * rows)
        return fig

    def create_pareto_chart(self, results: dict) -> go.Figure:
        rows = []
        for p, r in results.items():
            pval = r.get('p_value')
            if pval is not None and not (isinstance(pval, float) and np.isnan(pval)) and pval < 0.05:
                rows.append({'Parameter': p, 'Effect': abs(r.get('effect_size') or 0.0)})
        if not rows:
            fig = go.Figure()
            fig.add_annotation(text="Nenhuma divergência significativa", x=0.5, y=0.5, xref='paper', yref='paper', showarrow=False)
            return fig

        df = pd.DataFrame(rows).sort_values('Effect', ascending=False)
        df['Percent'] = df['Effect'] / df['Effect'].sum() * 100.0
        df['Cum'] = df['Percent'].cumsum()

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_bar(x=df['Parameter'], y=df['Effect'], name='Tamanho do Efeito', marker_color='steelblue', secondary_y=False)
        fig.add_scatter(x=df['Parameter'], y=df['Cum'], mode='lines+markers', name='% Acumulativa', line=dict(color='red'), secondary_y=True)
        fig.update_yaxes(title_text='Tamanho do Efeito', secondary_y=False)
        fig.update_yaxes(title_text='% Acumulativa', range=[0, 100], secondary_y=True)
        fig.update_layout(title='Pareto de Divergências')
        return fig

