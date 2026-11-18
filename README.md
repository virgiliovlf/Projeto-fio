# Painel Integrado de Indicadores de Desempenho Institucional (Fiocruz)

Produto Técnico-Tecnológico desenvolvido no âmbito do Mestrado em Administração (Universidade Potiguar — UnP), voltado à análise de integração, transparência ativa e reprodutibilidade dos indicadores de desempenho da Fiocruz (Ciclo 2025 — Portaria nº 571/2026).

## Arquivos do Repositório
- `index.html`: Painel interativo completo com síntese diagnóstica via IA.
- `data/parecer_ia.json`: Base JSON com a auditoria de reprodutibilidade gerada pelo script Python.
- `scripts/coletor.py`: Script integrado à API do Gemini (`google-genai`) para auditoria determinística sem simulação de dados.
- `.github/workflows/atualizar_dados.yml`: Automação via GitHub Actions.
