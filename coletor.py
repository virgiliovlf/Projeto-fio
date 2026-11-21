import os
import json
import time
from datetime import datetime, timezone, timedelta
from google import genai
from google.genai import types

OUTPUT_IA_JSON = "parecer_ia.json"

INDICADORES_RESUMO = [
    {
        "id": "pesquisa",
        "nome": "Produtividade em pesquisa (média rolante quadriênio)",
        "atingimento": "149,19%",
        "repro": "Parcial",
        "completude": "63%",
        "gargalo": "Denominador funcional (servidores elegíveis) não exportável com os mesmos filtros",
        "elos_faltantes": "Numerador e filtros parciais; Denominador e Memória ausentes"
    },
    {
        "id": "plataformas",
        "nome": "Atendimento de serviços às plataformas tecnológicas",
        "atingimento": "117,10%",
        "repro": "Não reproduzível",
        "completude": "50%",
        "gargalo": "Ausência de painel público com numerador (atendidos) e denominador (demandados)",
        "elos_faltantes": "Numerador, Denominador, Filtros e Memória de cálculo ausentes"
    },
    {
        "id": "colecoes",
        "nome": "Atendimento de serviços prestados pelas Coleções Biológicas",
        "atingimento": "130,14%",
        "repro": "Não reproduzível",
        "completude": "50%",
        "gargalo": "Serviços demandados e atendidos ausentes em base pública estruturada",
        "elos_faltantes": "Numerador, Denominador, Filtros e Memória de cálculo ausentes"
    },
    {
        "id": "bio",
        "nome": "Percentual de atendimento às demandas de biofármacos",
        "atingimento": "104,40%",
        "repro": "Parcial",
        "completude": "63%",
        "gargalo": "Programação anual pactuada (denominador) não integrada ao painel de fornecimento",
        "elos_faltantes": "Numerador e filtros parciais; Denominador e Memória ausentes"
    },
    {
        "id": "arv",
        "nome": "Atendimento à demanda por Antirretrovirais do Programa Aids/MS",
        "atingimento": "100,00%",
        "repro": "Parcial",
        "completude": "63%",
        "gargalo": "Pautas e quantidades requisitadas não reunidas no mesmo ambiente dos volumes entregues",
        "elos_faltantes": "Numerador e filtros parciais; Denominador e Memória ausentes"
    },
    {
        "id": "med",
        "nome": "Atendimento à demanda por medicamentos do Ministério da Saúde",
        "atingimento": "101,98%",
        "repro": "Parcial",
        "completude": "63%",
        "gargalo": "Quantidades requisitadas por pautas do MS ausentes do painel público",
        "elos_faltantes": "Numerador e filtros parciais; Denominador e Memória ausentes"
    },
    {
        "id": "edu",
        "nome": "Alunos matriculados (Stricto, Lato e Técnico)",
        "atingimento": "124,96%",
        "repro": "Parcial",
        "completude": "50%",
        "gargalo": "Previsão pactuada por modalidade (Stricto 75%, Lato 80%, Técnico 60%) dispersa",
        "elos_faltantes": "Meta, Resultado, Numerador e Filtros parciais; Denominador e Memória ausentes"
    },
    {
        "id": "arca",
        "nome": "Índice de disponibilização no Repositório ARCA",
        "atingimento": "109,00%",
        "repro": "Parcial",
        "completude": "69%",
        "gargalo": "Falta desagregação automatizada por unidade técnico-científica nos relatórios",
        "elos_faltantes": "Numerador e Memória parciais; Denominador histórico desagregado ausente"
    },
    {
        "id": "prog",
        "nome": "Horas de programação veiculadas",
        "atingimento": "100,00%",
        "repro": "Disponível",
        "completude": "100%",
        "gargalo": "Nenhum gargalo crítico de rastreabilidade (mede tempo de grade, mas não alcance público)",
        "elos_faltantes": "Todos os 8 elos disponíveis"
    },
    {
        "id": "museu",
        "nome": "Índice de visitação ao Museu da Vida",
        "atingimento": "178,43%",
        "repro": "Parcial",
        "completude": "63%",
        "gargalo": "Estimativas indiretas no público itinerante/móvel e ausência de recorte sociodemográfico",
        "elos_faltantes": "Numerador e filtros parciais; Denominador (expectativa) e Memória ausentes"
    },
    {
        "id": "pacientes",
        "nome": "Proporção de pacientes em protocolo de pesquisa",
        "atingimento": "110,55%",
        "repro": "Parcial",
        "completude": "63%",
        "gargalo": "Sistemas de prontuário eletrônico descentralizados entre os institutos assistenciais",
        "elos_faltantes": "Numerador e filtros parciais; Denominador e Memória ausentes"
    },
    {
        "id": "blh",
        "nome": "Proporção de Bancos de Leite Humano (BLH) no Brasil credenciados",
        "atingimento": "126,83%",
        "repro": "Parcial",
        "completude": "63%",
        "gargalo": "Monitoramento da rede nacional dependente de auditorias estaduais descentralizadas",
        "elos_faltantes": "Numerador e filtros parciais; Denominador (BLHs monitorados) e Memória ausentes"
    },
    {
        "id": "diag",
        "nome": "Diagnósticos laboratoriais de referência atendidos no prazo",
        "atingimento": "108,26%",
        "repro": "Parcial",
        "completude": "63%",
        "gargalo": "Sem abertura pública dos recortes por agravo e laboratório de referência (LIS)",
        "elos_faltantes": "Numerador e filtros parciais; Denominador e Memória ausentes"
    },
    {
        "id": "ouvidoria",
        "nome": "Manifestações de ouvidoria atendidas no prazo pactuado",
        "atingimento": "106,00%",
        "repro": "Parcial",
        "completude": "81%",
        "gargalo": "Ausência de memória pública sobre tramitação interna nas unidades demandadas",
        "elos_faltantes": "Denominador, Filtros e Memória disponíveis apenas de forma parcial"
    },
    {
        "id": "economia",
        "nome": "Economia obtida em aquisições por Pregão Eletrônico SISPP",
        "atingimento": "242,40%",
        "repro": "Parcial",
        "completude": "63%",
        "gargalo": "Sem memória aberta dos itens cancelados/desertos no denominador e oscilações de estimativa",
        "elos_faltantes": "Numerador e filtros parciais; Denominador e Memória ausentes"
    }
]

REFERENCIAL_DISSERTACAO = """
VOCÊ É UM ANALISTA DE APOIO À PESQUISA DE MESTRADO PROFISSIONAL EM ADMINISTRAÇÃO (UnP).
Julgue os 15 indicadores da Fiocruz (Ciclo 2025 - Portaria nº 571/2026) ESTRITAMENTE à luz do referencial teórico,
das evidências empíricas e das etapas metodológicas do projeto de dissertação:

1. SELETIVIDADE E ALINHAMENTO ESTRATÉGICO (Parmenter, 2015; Badawy et al., 2016; Van de Ven et al., 2023; Johnsen, Solholm e Tufte, 2024):
   Nem toda medida disponível é um KPI estratégico; sistemas fragmentados geram redundância e uso meramente informativo (Neely et al., 1997; Bourne et al., 2000, 2003).
2. COMPLETUDE METODOLÓGICA E AUDITABILIDADE (RIPSA, 2008; Bahia, 2021; Fiocruz, 2025; Tallens Junior et al., 2025; CGU):
   Um KPI exige finalidade, fórmula, unidade, fonte, periodicidade, polaridade, responsável, linha de base, meta, série histórica e memória de cálculo (numerador, denominador e filtros).
3. EFICÁCIA FORMAL VS. EFETIVIDADE, QUALIDADE E EQUIDADE NO SUS (TCU, 2011; Mury, 2019; Gonzaga et al., 2019; Lapuente e Van de Walle, 2020):
   Cumprir metas numéricas (eficácia) não garante economicidade, eficiência, qualidade, equidade ou efetividade social no SUS. Vincular também gestão de riscos e accountability (Alves e Martins, 2026; Castro, Barbosa Neto e Cunha, 2022) e aprendizagem organizacional (Castelo, Castelo e Gomes, 2023).
4. EVIDÊNCIAS EMPÍRICAS DO CASO FIOCRUZ (Ohayon e Rosenberg, 2014; Belle et al., 2022; Vidè, Cepiku e Mastrodascio, 2025; Rivenbark e Vignieri, 2025):
   Ohayon e Rosenberg (2014) identificaram lacunas nos indicadores de CT&I da Fiocruz entre produtos internos (artigos, insumos) e impactos nas políticas do SUS. A apresentação visual e a clareza condicionam o uso gerencial.
5. CLASSIFICAÇÃO DA ETAPA 4 E PROPOSIÇÃO INCREMENTAL:
   Cada recomendação deve iniciar obrigatoriamente com uma das tags exatas:
   - [Etapa 4: Atende plenamente]
   - [Etapa 4: Atende parcialmente]
   - [Etapa 4: Não atende à auditabilidade]
   Seguida de diagnóstico fundamentado nos autores acima e na lacuna dos 8 elos, propondo 1 ajuste técnico de rastreabilidade para a Cogeplan/Observatório + 1 indicador incremental voltado à efetividade ou qualidade no SUS.
"""


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
    {REFERENCIAL_DISSERTACAO}

    REGRAS ESTRITAS:
    1. NÃO invente, NÃO estime e NÃO simule nenhum número. Use apenas os dados fornecidos abaixo.
    2. Produza uma resposta em JSON válido contendo exatamente:
       - "sintese_executiva": um parágrafo único (3 a 4 frases) analisando o contraste entre o alto atingimento médio dos 15 indicadores (127,48%) e as restrições de reprodutibilidade pública (1 disponível, 12 parciais e 2 não reproduzíveis; completude documental média de 61%), fundamentado na tensão entre eficácia formal e efetividade/transparência segundo os autores do referencial.
       - "recomendacoes_por_id": um objeto contendo todos os 15 IDs ("pesquisa", "plataformas", "colecoes", "bio", "arv", "med", "edu", "arca", "prog", "museu", "pacientes", "blh", "diag", "ouvidoria", "economia"), onde cada valor inicia com a tag da Etapa 4 e apresenta o parecer técnico-acadêmico (máximo 3 frases).

    Dados dos 15 indicadores (Ciclo 2025 - Portaria nº 571/2026):
    {json.dumps(INDICADORES_RESUMO, ensure_ascii=False, indent=2)}
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
                        temperature=0.15
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
    if "sintese_executiva" not in resultado_ia or "recomendacoes_por_id" not in resultado_ia:
        raise ValueError("JSON retornado pela IA não contém os campos obrigatórios.")

    fuso_br = timezone(timedelta(hours=-3))
    payload = {
        "gerado_em": datetime.now(fuso_br).strftime("%d/%m/%Y %H:%M"),
        "modelo": f"{modelo_usado} · Régua Teórico-Empírica (PTT/UnP)",
        "analise": resultado_ia
    }

    with open(OUTPUT_IA_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Sucesso! Ficheiro parecer_ia.json gravado via {modelo_usado}.")


if __name__ == "__main__":
    gerar_diagnostico_ia()
