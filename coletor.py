import os
import json
from datetime import datetime
from google import genai
from google.genai import types

OUTPUT_IA_JSON = "parecer_ia.json"

INDICADORES_RESUMO = [
    {"id": "pesquisa", "nome": "Produtividade em pesquisa", "atingimento": "149,19%", "repro": "Parcial", "gargalo": "Denominador funcional não exportável com os mesmos filtros"},
    {"id": "plataformas", "nome": "Atendimento às plataformas tecnológicas", "atingimento": "117,10%", "repro": "Não reproduzível", "gargalo": "Sem painel público com numerador e denominador"},
    {"id": "colecoes", "nome": "Atendimento de serviços das coleções biológicas", "atingimento": "130,14%", "repro": "Não reproduzível", "gargalo": "Serviços demandados e atendidos ausentes em base aberta"},
    {"id": "bio", "nome": "Atendimento às demandas de biofármacos", "atingimento": "104,44%", "repro": "Parcial", "gargalo": "Programação anual não integrada ao painel de fornecimento"},
    {"id": "arv", "nome": "Atendimento à demanda por antirretrovirais", "atingimento": "100,00%", "repro": "Parcial", "gargalo": "Pautas/requisições não integradas no mesmo ambiente"},
    {"id": "med", "nome": "Atendimento à demanda por medicamentos do MS", "atingimento": "102,11%", "repro": "Parcial", "gargalo": "Quantidades requisitadas ausentes do painel público"},
    {"id": "edu", "nome": "Matrículas por modalidade", "atingimento": "Por modalidade", "repro": "Parcial", "gargalo": "Previsão pactuada não integrada aos registros acadêmicos"}
]

def gerar_diagnostico_ia():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Aviso: GEMINI_API_KEY não configurada. Mantendo arquivo padrão.")
        return

    client = genai.Client(api_key=api_key)

    prompt = f"""
    Você é um auditor técnico de governança e transparência pública analisando os indicadores da Fiocruz (Ciclo 2025 - Portaria nº 571/2026).
    REGRAS ESTRITAS:
    1. NÃO invente, NÃO estime e NÃO simule nenhum número. Use apenas os dados fornecidos abaixo.
    2. Produza uma resposta em JSON contendo:
       - "sintese_executiva": um parágrafo de 3 a 4 frases analisando o contraste entre o alto atingimento médio (117,2%) e as restrições de reprodutibilidade pública (5 parciais e 2 não reproduzíveis).
       - "recomendacoes_por_id": um objeto onde cada chave é o "id" do indicador e o valor é uma recomendação técnica objetiva (máximo 2 frases) para a Cogeplan/Observatório abrir o elo faltante.

    Dados:
    {json.dumps(INDICADORES_RESUMO, ensure_ascii=False)}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
    )

    resultado_ia = json.loads(response.text)
    payload = {
        "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "modelo": "Gemini 2.5 Flash (Auditoria Determinística)",
        "analise": resultado_ia
    }

    with open(OUTPUT_IA_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print("Parecer de IA gerado com sucesso em data/parecer_ia.json")

if __name__ == "__main__":
    gerar_diagnostico_ia()
