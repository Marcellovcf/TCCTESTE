import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import shapiro, levene, ttest_ind, mannwhitneyu


class StatisticalAnalyzer:
    def __init__(self, alpha: float = 0.05) -> None:
        self.alpha = alpha

    def perform_analysis(self, df: pd.DataFrame) -> dict:
        results: dict[str, dict] = {}
        params = [
            'viscosidade_40c',
            'teor_agua',
            'particulas_4um',
            'particulas_6um',
            'particulas_14um',
        ]
        for p in params:
            if p in df.columns:
                results[p] = self._analyze_param(df, p)
        return results

    def _analyze_param(self, df: pd.DataFrame, param: str) -> dict:
        m = df[df['origem'] == 'Mineradora'][param].dropna()
        d = df[df['origem'] == 'Distribuidora'][param].dropna()

        if len(m) < 2 or len(d) < 2:
            return self._insufficient()

        stats_m = self._desc(m)
        stats_d = self._desc(d)

        norm_m = self._normality(m)
        norm_d = self._normality(d)

        test = self._choose_test(m, d, norm_m, norm_d)

        ci_m = self._ci(m)
        ci_d = self._ci(d)

        return {
            'mean_mineradora': stats_m['mean'],
            'mean_distribuidora': stats_d['mean'],
            'median_mineradora': stats_m['median'],
            'median_distribuidora': stats_d['median'],
            'std_mineradora': stats_m['std'],
            'std_distribuidora': stats_d['std'],
            'normality_mineradora': norm_m,
            'normality_distribuidora': norm_d,
            'test_used': test['test_name'],
            'p_value': test['p_value'],
            'statistic': test['statistic'],
            'ci_mineradora': ci_m,
            'ci_distribuidora': ci_d,
            'effect_size': self._cohen_d(m, d),
        }

    def _desc(self, x: pd.Series) -> dict:
        return {
            'mean': float(np.mean(x)),
            'median': float(np.median(x)),
            'std': float(np.std(x, ddof=1)),
            'count': int(len(x)),
        }

    def _normality(self, x: pd.Series) -> dict:
        if len(x) < 3:
            return {'is_normal': False, 'p_value': None, 'statistic': None}
        stat, p = shapiro(x)
        return {'is_normal': bool(p > self.alpha), 'p_value': float(p), 'statistic': float(stat)}

    def _choose_test(self, a: pd.Series, b: pd.Series, na: dict, nb: dict) -> dict:
        if na['is_normal'] and nb['is_normal']:
            lev_stat, lev_p = levene(a, b)
            equal_var = bool(lev_p > self.alpha)
            t_stat, t_p = ttest_ind(a, b, equal_var=equal_var)
            return {
                'test_name': f"Teste t ({'variâncias iguais' if equal_var else 'variâncias diferentes'})",
                'p_value': float(t_p),
                'statistic': float(t_stat),
            }
        u_stat, u_p = mannwhitneyu(a, b, alternative='two-sided')
        return {'test_name': 'Mann-Whitney U', 'p_value': float(u_p), 'statistic': float(u_stat)}

    def _ci(self, x: pd.Series, confidence: float = 0.95) -> tuple[float, float]:
        if len(x) < 2:
            return (float('nan'), float('nan'))
        mean = float(np.mean(x))
        sem = float(stats.sem(x))
        h = sem * float(stats.t.ppf((1 + confidence) / 2.0, len(x) - 1))
        return (mean - h, mean + h)

    def _cohen_d(self, a: pd.Series, b: pd.Series) -> float:
        n1, n2 = len(a), len(b)
        s1, s2 = np.var(a, ddof=1), np.var(b, ddof=1)
        pooled = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
        if pooled == 0:
            return float('nan')
        return (float(np.mean(a)) - float(np.mean(b))) / float(pooled)

    def _insufficient(self) -> dict:
        return {
            'mean_mineradora': np.nan,
            'mean_distribuidora': np.nan,
            'median_mineradora': np.nan,
            'median_distribuidora': np.nan,
            'std_mineradora': np.nan,
            'std_distribuidora': np.nan,
            'normality_mineradora': {'is_normal': False, 'p_value': None},
            'normality_distribuidora': {'is_normal': False, 'p_value': None},
            'test_used': 'Dados insuficientes',
            'p_value': np.nan,
            'statistic': np.nan,
            'ci_mineradora': (np.nan, np.nan),
            'ci_distribuidora': (np.nan, np.nan),
            'effect_size': np.nan,
        }

