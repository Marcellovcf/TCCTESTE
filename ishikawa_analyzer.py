class IshikawaAnalyzer:
    def __init__(self) -> None:
        self.cause_database = {
            'Método': [
                "Diferença no ponto de coleta (antes/depois de filtros)",
                "Protocolos de coleta distintos",
                "Tempo de repouso e homogeneização distintos",
            ],
            'Máquina': [
                "Calibração de equipamentos em períodos diferentes",
                "Modelos/marcas de equipamentos distintos",
                "Condições ambientais do laboratório",
            ],
            'Mão de obra': [
                "Operador dedicado vs. equipe rotativa",
                "Nível de treinamento e experiência",
            ],
            'Material': [
                "Tipo de embalagem e vedação",
                "Condições e tempo de transporte",
                "Contaminação durante manuseio",
            ],
            'Meio ambiente': [
                "Variações de temperatura/umidade",
                "Exposição à luz e vibrações",
            ],
            'Medida': [
                "Arredondamento e resolução dos equipamentos",
                "Critérios de outliers e incerteza",
            ],
        }

        self.parameter_specific = {
            'viscosidade_40c': {
                'Método': ["Temperatura de pré-aquecimento e estabilização"],
                'Máquina': ["Calibração do viscosímetro", "Estabilidade do banho"],
                'Material': ["Contaminação com água", "Oxidação"],
            },
            'teor_agua': {
                'Método': ["Exposição ao ar e contaminação de coleta"],
                'Máquina': ["Calibração Karl Fischer", "Purga do sistema"],
                'Material': ["Vedação/embalagem", "Higroscopicidade"],
            },
            'particulas_4um': {
                'Máquina': ["Calibração contador de partículas", "Limpeza do sistema"],
                'Material': ["Contaminação externa", "Filtração"],
                'Meio ambiente': ["Partículas em suspensão no laboratório"],
            },
            'particulas_6um': {
                'Máquina': ["Resolução e calibração"],
                'Material': ["Degradação de aditivos", "Contaminação cruzada"],
                'Medida': ["Critérios de contagem diferentes"],
            },
            'particulas_14um': {
                'Máquina': ["Sensibilidade do detector", "Alinhamento óptico"],
                'Material': ["Agregados/precipitação"],
                'Método': ["Agitação inadequada"],
            },
        }

    def suggest_causes(self, classifications: dict) -> dict:
        suggested = {k: [] for k in self.cause_database.keys()}

        probs = [p for p, c in classifications.items() if c['classification'] in ("Divergente", "Fora do Padrão")]
        if not probs:
            return {
                'Método': ["Padronizar protocolos de coleta"],
                'Máquina': ["Sincronizar calibrações"],
                'Mão de obra': ["Treinamento conjunto"],
                'Material': ["Padronizar embalagens"],
                'Meio ambiente': ["Monitorar temperatura/umidade"],
                'Medida': ["Padronizar arredondamentos"],
            }

        for p in probs:
            if p in self.parameter_specific:
                for cat, lst in self.parameter_specific[p].items():
                    suggested[cat].extend(lst)

        # Adicionar causas gerais prováveis
        for cat, lst in self.cause_database.items():
            if len(suggested[cat]) < 3:
                needed = 3 - len(suggested[cat])
                suggested[cat].extend(lst[:needed])

        # Deduplicar e limitar
        for cat in suggested:
            seen = set()
            dedup = []
            for item in suggested[cat]:
                if item not in seen:
                    seen.add(item)
                    dedup.append(item)
            suggested[cat] = dedup[:5]
        return suggested

