import numpy as np
import pandas as pd


class ParameterClassifier:
    def __init__(self) -> None:
        self.normative_limits = {
            'viscosidade_40c': {'min': 2.0, 'max': 4.1, 'unit': 'cSt'},
            'teor_agua': {'min': 0.0, 'max': 200.0, 'unit': 'ppm'},
            'particulas_14um': {'min': 0.0, 'max': 20.0, 'unit': 'part/mL'},
        }
        self.divergence_criteria = {
            'viscosidade_40c': 0.4,
            'teor_agua': 50.0,
            'particulas_14um': 5.0,
        }

    def classify_parameters(self, df: pd.DataFrame) -> dict:
        out: dict[str, dict] = {}
        for col in df.columns:
            if col == 'origem':
                continue
            c = self._classify_one(df, col)
            if c:
                out[col] = c
        return out

    def _classify_one(self, df: pd.DataFrame, param: str) -> dict | None:
        a = df[df['origem'] == 'Mineradora'][param].dropna()
        b = df[df['origem'] == 'Distribuidora'][param].dropna()
        if len(a) == 0 or len(b) == 0:
            return None
        ma = float(np.mean(a))
        mb = float(np.mean(b))
        within_a = self._within(param, ma)
        within_b = self._within(param, mb)
        divergent = self._divergent(param, ma, mb)

        if not within_a or not within_b:
            details = []
            if not within_a:
                details.append(f"Mineradora fora do limite: {ma:.2f}")
            if not within_b:
                details.append(f"Distribuidora fora do limite: {mb:.2f}")
            lim = self.normative_limits.get(param)
            if lim:
                details.append(f"Limite: {lim['min']}-{lim['max']} {lim['unit']}")
            cls = 'Fora do Padrão'
        elif divergent:
            thr = self.divergence_criteria.get(param, 0.0)
            cls = 'Divergente'
            details = [f"Diferença de {abs(ma-mb):.2f} (limite {thr})"]
        else:
            cls = 'Normal'
            details = ["Dentro dos limites e sem divergência significativa"]

        return {
            'classification': cls,
            'details': "; ".join(details),
            'mean_mineradora': ma,
            'mean_distribuidora': mb,
            'within_limits_mineradora': within_a,
            'within_limits_distribuidora': within_b,
            'is_divergent': divergent,
        }

    def _within(self, param: str, v: float) -> bool:
        lim = self.normative_limits.get(param)
        if not lim:
            return True
        return lim['min'] <= v <= lim['max']

    def _divergent(self, param: str, a: float, b: float) -> bool:
        thr = self.divergence_criteria.get(param)
        if thr is None:
            return False
        return abs(a - b) >= thr

