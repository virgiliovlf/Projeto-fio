import os
import json
import time
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
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY está vazia nos Secrets.")

    client = genai.Client(api_key=api_key)

    # Descobre automaticamente os modelos disponíveis para a sua chave
    modelos_disponiveis = []
    try:
        for m in client.models.list():
            nome = m.name.replace("models/", "")
            if "gemini" in nome and "embedding" not in nome and "imagen" not in nome:
                modelos_disponiveis.append(nome)
    except Exception as e:
        print(f"Aviso ao listar modelos: {e}")

    # Garante que gemini-3.8-flash seja o primeiro da fila
    modelos = ["gemini-3.8-flash"] + [m for m in modelos_disponiveis if m != "gemini-3.8-flash"]
    print(f"Modelos encontrados na conta: {modelos}")

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

    response = None
    modelo_usado = ""

    # Tenta até 5 rodadas com pausa de 15s entre cada falha 503
    for rodada in range(5):
        for modelo in modelos:
            try:
                response = client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1
                    )
                )
                modelo_usado = modelo
                break
            except Exception as e:
                print(f"[Rodada {rodada+1}] {modelo} indisponível: {e}")
        if response:
            break
        print("Aguardando 15 segundos para alívio do servidor...")
        time.sleep(15)

    if not response:
        raise RuntimeError("Servidores do Google sobrecarregados após 5 rodadas. Tente rodar novamente em alguns minutos.")

    resultado_ia = json.loads(response.text)
    payload = {
        "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "modelo": f"{modelo_usado} (Auditoria Determinística)",
        "analise": resultado_ia
    }

    with open(OUTPUT_IA_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Sucesso! Ficheiro parecer_ia.json gravado via {modelo_usado}.")

if __name__ == "__main__":
    gerar_diagnostico_ia()
