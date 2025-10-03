# Analisador de Laudos Laboratoriais de Diesel

Sistema web (Streamlit) para análise estatística comparativa de laudos laboratoriais de diesel entre mineradora e distribuidora.

## Funcionalidades

- Extração automática de dados de PDFs (viscosidade 40°C, teor de água, partículas >4µm, >6µm, ≥14µm)
- Testes estatísticos: Shapiro-Wilk, Levene, t-test, Mann-Whitney; IC 95%
- Tabela comparativa com médias, medianas, desvios, p-valor e conclusão
- Gráficos: boxplots, probabilidade normal (QQ), Pareto de divergências
- Classificação: Normal, Fora do Padrão, Divergente
- Sugestões de causas (Ishikawa)

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Execução

```bash
streamlit run main.py
```

Abra o navegador em `http://localhost:8501`.

## Uso

1. Faça upload dos PDFs da mineradora e da distribuidora na barra lateral
2. O sistema extrai automaticamente os parâmetros e monta as tabelas
3. Visualize os testes, gráficos e diagnósticos de divergência com causas prováveis

## Limites e Critérios

- Viscosidade: 2,0–4,1 cSt; divergência ≥0,4 cSt
- Teor de água: ≤200 ppm; divergência ≥50 ppm
- Partículas ≥14 µm: ≤20 part/mL; divergência ≥5 part/mL

## Publicar no GitHub

```bash
git init
git add .
git commit -m "feat: diesel lab analyzer initial version"
git branch -M main
git remote add origin <sua_url_do_repositorio>
git push -u origin main
```

# TCCTESTE