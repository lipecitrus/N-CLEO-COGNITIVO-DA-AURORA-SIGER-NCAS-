import json
from datetime import datetime


ARQUIVO_JSON = "dados_colonia.json"
ARQUIVO_TXT = "registros_colonia.txt"


# ============================================================
# FUNÇÕES DE JSON  (Seção 1.3 - Estrutura JSON do sistema)
# ============================================================
#
# Por que usamos JSON aqui?
# Os dados de módulos, alertas e solicitações têm uma estrutura
# fixa e "tabular" (cada item tem os mesmos campos: id, nome,
# status, prioridade, data etc). JSON representa muito bem
# listas de dicionários com esse formato, e permite recarregar
# a estrutura exatamente como estava, sem perder tipos (número,
# texto, lista). Por isso módulos/alertas/solicitações ficam no
# JSON, enquanto os registros "narrativos" (texto livre, tipo
# um diário de bordo) ficam no TXT.


def carregar_json(caminho_arquivo):
    """Carrega os dados estruturados do arquivo JSON (modo 'r' implícito
    dentro do open, mas tratado com try/except para arquivo ausente ou
    corrompido)."""
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        print("\n[ERRO] Arquivo dados_colonia.json não encontrado.")
        return {
            "modulos": [],
            "alertas": [],
            "solicitacoes": [],
            "interacoes": []
        }
    except json.JSONDecodeError:
        print("\n[ERRO] O arquivo JSON está inválido.")
        return {
            "modulos": [],
            "alertas": [],
            "solicitacoes": [],
            "interacoes": []
        }


def salvar_json(dados):
    """Salva o dicionário de dados no arquivo dados_colonia.json (modo 'w' -
    sobrescreve o conteúdo anterior pelo estado mais atual)."""
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)


def salvar_json_generico(dados, caminho_arquivo):
    """Versão genérica de salvar_json(), que aceita qualquer caminho.
    Usada para gravar em alertas.json e solicitacoes.json, que são
    arquivos separados do dados_colonia.json."""
    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)


def validar_estrutura_json(dados):
    """Confere se o dicionário carregado tem todas as chaves esperadas.
    Isso evita que o programa quebre caso alguém edite o JSON manualmente
    e esqueça alguma seção."""
    chaves_esperadas = ["modulos", "alertas", "solicitacoes", "interacoes"]
    faltando = [chave for chave in chaves_esperadas if chave not in dados]

    if faltando:
        print(f"[AVISO] O JSON está sem as chaves: {', '.join(faltando)}")
        for chave in faltando:
            dados[chave] = []
    return dados


def exibir_json():
    """Exibe os dados atualmente armazenados no sistema.

    CORREÇÃO IMPORTANTE: antes, essa função lia alertas e solicitações
    de dentro de dados_colonia.json, mas quem cadastrava um alerta ou uma
    solicitação pelo menu (cadastrar_alerta/cadastrar_solicitacao) salvava
    em alertas.json e solicitacoes.json - dois arquivos diferentes! Por
    isso o que era cadastrado nunca aparecia aqui nem na IA simulada
    (seção 1.5), que sempre lê de alertas.json/solicitacoes.json.

    Agora módulos continuam vindo de dados_colonia.json, mas alertas e
    solicitações são lidos direto dos arquivos que de fato são
    atualizados pelo cadastro, então tudo fica sincronizado."""
    dados_modulos = carregar_json("dados_colonia.json")
    dados_alertas = carregar_json("alertas.json")
    dados_solicitacoes = carregar_json("solicitacoes.json")

    print("\n========== DADOS DA COLÔNIA ==========")

    print("\n--- MÓDULOS ---")
    if dados_modulos.get("modulos"):
        for modulo in dados_modulos["modulos"]:
            print(
                f'ID: {modulo["id"]} | '
                f'Nome: {modulo["nome"]} | '
                f'Status: {modulo["status"]}'
            )
    else:
        print("Nenhum módulo cadastrado.")

    print("\n--- ALERTAS ---")
    alertas = dados_alertas.get("alertas", [])
    if alertas:
        for alerta in alertas:
            print(
                f'[{alerta["prioridade"].upper()}] '
                f'{alerta["modulo"]}: {alerta["mensagem"]}'
            )
    else:
        print("Nenhum alerta cadastrado.")

    print("\n--- SOLICITAÇÕES ---")
    solicitacoes = dados_solicitacoes.get("solicitacoes", [])
    if solicitacoes:
        for solicitacao in solicitacoes:
            print(
                f'[{solicitacao["urgencia"].upper()}] '
                f'{solicitacao["tripulante"]}: {solicitacao["descricao"]} '
                f'(status: {solicitacao["status"]})'
            )
    else:
        print("Nenhuma solicitação cadastrada.")


def buscar_modulo_por_nome(nome_busca):
    """Percorre o dicionário carregado do JSON e retorna o módulo cujo nome
    bate (ignorando maiúsculas/minúsculas). Retorna None se não achar."""
    dados = carregar_json("dados_colonia.json")
    for modulo in dados["modulos"]:
        if modulo["nome"].strip().lower() == nome_busca.strip().lower():
            return modulo
    return None


# ============================================================
# FUNÇÕES DE ARQUIVO TEXTO  (Seção 1.2 - Manipulação de arquivos)
# ============================================================
#
# Aqui demonstramos, de propósito, os 5 modos de abertura pedidos
# na atividade (w, r, a, x, +) e os métodos read(), readline(),
# readlines() e writelines(), todos usando o gerenciador de
# contexto "with" (que fecha o arquivo automaticamente).


def inicializar_arquivo_txt():
    """MODO 'x' - cria o arquivo somente se ele ainda não existir.
    Se já existir, o Python lança FileExistsError, que tratamos aqui.
    Isso evita apagar por acidente um arquivo de registros já em uso."""
    try:
        with open(ARQUIVO_TXT, "x", encoding="utf-8") as arquivo:
            arquivo.write("=== REGISTROS DA AURORA SIGER ===\n")
            arquivo.write("Arquivo inicializado pelo NCAS.\n")
        print("[OK] Arquivo de registros criado com sucesso (modo 'x').")
    except FileExistsError:
        print("[INFO] O arquivo de registros já existe. Nada foi criado.")


def adicionar_registro(mensagem):
    """MODO 'a' (append) - adiciona uma nova linha ao FINAL do arquivo,
    sem apagar o que já estava escrito."""
    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    with open(ARQUIVO_TXT, "a", encoding="utf-8") as arquivo:
        arquivo.write(f"[{data}] {mensagem}\n")


def ler_registros():
    """MODO 'r' - lê o arquivo inteiro de uma vez com readlines(),
    que devolve uma LISTA com cada linha do arquivo."""
    try:
        with open(ARQUIVO_TXT, "r", encoding="utf-8") as arquivo:
            registros = arquivo.readlines()

        print("\n========== REGISTROS DA COLÔNIA ==========")

        if registros:
            for registro in registros:
                print(registro.rstrip())
        else:
            print("Nenhum registro encontrado.")

    except FileNotFoundError:
        print("\n[ERRO] Arquivo registros_colonia.txt não encontrado.")


def ler_cabecalho():
    """MODO 'r' - usa readline() para ler só a PRIMEIRA linha do arquivo,
    diferente de readlines(), que traz todas de uma vez."""
    try:
        with open(ARQUIVO_TXT, "r", encoding="utf-8") as arquivo:
            primeira_linha = arquivo.readline()
        print(f"\nCabeçalho do arquivo: {primeira_linha.strip()}")
    except FileNotFoundError:
        print("\n[ERRO] Arquivo não encontrado.")


def reescrever_arquivo_txt(novas_linhas):
    """MODO 'w' - sobrescreve TODO o conteúdo do arquivo usando
    writelines(), que recebe uma lista de strings e escreve cada uma
    como uma linha. Atenção: o conteúdo anterior é perdido."""
    with open(ARQUIVO_TXT, "w", encoding="utf-8") as arquivo:
        arquivo.writelines(novas_linhas)
    print("[OK] Arquivo reescrito com sucesso (modo 'w').")


def corrigir_ultimo_registro(novo_texto):
    """MODO 'r+' (leitura E escrita) - lê todas as linhas, substitui a
    última pelo texto corrigido e regrava o arquivo inteiro, sem apagar
    o histórico anterior a ela. Demonstra o uso do '+' junto de read/write
    no mesmo arquivo aberto."""
    try:
        with open(ARQUIVO_TXT, "r+", encoding="utf-8") as arquivo:
            linhas = arquivo.readlines()
            if not linhas:
                print("[ERRO] Arquivo vazio, nada para corrigir.")
                return

            data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            linhas[-1] = f"[{data}] {novo_texto}\n"

            arquivo.seek(0)          # volta o "cursor" pro início do arquivo
            arquivo.writelines(linhas)
            arquivo.truncate()       # remove qualquer sobra do texto antigo

        print("[OK] Último registro corrigido com sucesso (modo 'r+').")
    except FileNotFoundError:
        print("[ERRO] Arquivo registros_colonia.txt não encontrado.")


def cadastrar_registro():
    """Interface de cadastro que chama adicionar_registro()."""
    print("\n========== NOVO REGISTRO ==========")

    mensagem = input("Digite a descrição do registro: ").strip()

    if not mensagem:
        print("[ERRO] O registro não pode ficar vazio.")
        return

    adicionar_registro(mensagem)
    print("[OK] Registro salvo com sucesso!")


# ============================================================
# FUNÇÕES DE CADASTRO NO JSON
# ============================================================


def cadastrar_alerta():
    """Cadastra um alerta operacional.

    CORREÇÃO: antes salvava dentro de dados_colonia.json com campos
    diferentes (id numérico, chave "tipo") dos usados em alertas.json
    (id "ALT-XXX", chave "tipo_ocorrencia"), que é o arquivo que a IA
    simulada (ia_simulada) realmente lê. Agora grava direto em
    alertas.json, no mesmo formato, pra tudo ficar sincronizado."""
    dados = carregar_json("alertas.json")
    if "alertas" not in dados:
        dados = {"alertas": []}

    print("\n========== NOVO ALERTA ==========")

    modulo = input("Módulo: ").strip()
    tipo_ocorrencia = input("Tipo de ocorrência: ").strip()
    prioridade = input("Prioridade (baixa/media/alta/critica): ").strip().lower()
    mensagem = input("Mensagem: ").strip()

    novo_id = f"ALT-{len(dados['alertas']) + 1:03d}"

    alerta = {
        "id": novo_id,
        "modulo": modulo,
        "tipo_ocorrencia": tipo_ocorrencia,
        "prioridade": prioridade,
        "data": datetime.now().strftime("%Y-%m-%d"),
        "mensagem": mensagem
    }

    dados["alertas"].append(alerta)
    salvar_json_generico(dados, "alertas.json")

    adicionar_registro(
        f"Novo alerta {novo_id} cadastrado no módulo {modulo}: {mensagem}"
    )

    print(f"[OK] Alerta {novo_id} salvo em alertas.json com sucesso!")


def cadastrar_solicitacao():
    """Cadastra uma solicitação da tripulação.

    CORREÇÃO: mesma causa do bug acima - antes salvava em
    dados_colonia.json com campos diferentes dos usados em
    solicitacoes.json. Agora grava direto em solicitacoes.json."""
    dados = carregar_json("solicitacoes.json")
    if "solicitacoes" not in dados:
        dados = {"solicitacoes": []}

    print("\n========== NOVA SOLICITAÇÃO ==========")

    tripulante = input("Nome do tripulante: ").strip()
    tipo_pedido = input("Tipo de pedido (manutencao/suprimentos/seguranca/administrativo): ").strip().lower()
    descricao = input("Descrição da solicitação: ").strip()
    urgencia = input("Urgência (baixa/media/alta): ").strip().lower()

    novo_id = f"SOL-{len(dados['solicitacoes']) + 101}"

    registro = {
        "id": novo_id,
        "tripulante": tripulante,
        "tipo_pedido": tipo_pedido,
        "descricao": descricao,
        "urgencia": urgencia,
        "status": "pendente"
    }

    dados["solicitacoes"].append(registro)
    salvar_json_generico(dados, "solicitacoes.json")

    adicionar_registro(
        f"Nova solicitação {novo_id} cadastrada por {tripulante}: {descricao}"
    )

    print(f"[OK] Solicitação {novo_id} salva em solicitacoes.json com sucesso!")


#
# ============================================================
# REGRAS LÓGICAS (Seção 1.4 - Regras lógicas e simplificação booleana)
# ============================================================
#


def buscar_modulo_por_id(dados):
    """Busca um módulo pelo seu ID e retorna seus dados quando encontrado.
    Permite cancelar a busca digitando 'sair'."""
    while True:
        id_procurado = input("Digite o ID do módulo (ou 'sair' para cancelar): ").strip().upper()
        
        if id_procurado == "SAIR":
            return None
        
        for modulo in dados["modulos"]:
            if modulo["id"] == id_procurado:
                return modulo
        
        print("ID não encontrado. Tente novamente.\n")


def consultar_modulo(usuario_autorizado, modulo):
    """Verifica, usando uma condição booleana AND, se o usuário está
    autorizado e se o módulo está ativo para liberar a consulta."""
    modulo_ativo = modulo["status"] == "Ativo"
    consulta_liberada = usuario_autorizado and modulo_ativo
    if consulta_liberada:
        print("Consulta liberada.")
        print("id:", modulo["id"])
        print("Módulo:", modulo["nome"])
        print("Status:", modulo["status"])
        print("Responsável", modulo["responsavel"])
    else:
        print("Consulta bloqueada: usuário não autorizado ou módulo inativo.")


def main():
    """Executa o fluxo principal, carregando os dados, buscando o módulo
    e aplicando a regra de autorização para realizar a consulta."""
    dados = carregar_json("dados_colonia.json")
    modulo_encontrado = buscar_modulo_por_id(dados)
    
    if modulo_encontrado:
        print("Módulo encontrado!")
        consultar_modulo(True, modulo_encontrado)
    else:
        print("Nenhum módulo encontrado com esse ID.")


#
# ============================================================
# ENGENHARIA DE PROMPTS (Seção 1.5 - Engenharia de prompts e simulação de IA generativa)
# ============================================================
#


def ordenar_por_prioridade(alertas):
    """Ordena os alertas do mais urgente para o menos urgente,
    considerando as prioridades crítica, alta, média e baixa."""
    ordem_prioridade = {
        "critica": 0,
        "alta": 1,
        "media": 2,
        "baixa": 3
    }
    return sorted(
        alertas,
        key=lambda alerta: ordem_prioridade.get(alerta["prioridade"].lower(), 99)
    )


def montar_prompt_resumo_alertas(dados):
    """Monta um prompt zero-shot para resumir os alertas da colônia,
    organizando-os por nível de prioridade."""
    alertas_ordenados = ordenar_por_prioridade(dados["alertas"])
    
    alertas_texto = ""
    for alerta in alertas_ordenados:
        alertas_texto += f"""
ID: {alerta['id']}
Módulo: {alerta['modulo']}
Tipo de ocorrência: {alerta['tipo_ocorrencia']}
Prioridade: {alerta['prioridade']}
---"""

    prompt = f"""\n============================================================
Zero-shot prompt:

Você é um assistente de monitoramento de uma colônia espacial. 
Resuma os alertas operacionais abaixo em uma lista, um item por alerta, contendo: 
módulo afetado, tipo de problema e nível de urgência (baixa, média, alta ou crítica). 
Ordene do mais urgente para o menos urgente.

Saída:
Alertas:
{alertas_texto}
"""
    return prompt


def montar_prompt_classificar_solicitacao(dados):
    """Monta um prompt few-shot para classificar uma solicitação
    da tripulação nas categorias definidas pelo sistema."""
    solicitacoes = dados.get("solicitacoes", [])
    pendentes = [s for s in solicitacoes if s.get("status") == "pendente"]
    alvo = pendentes[0] if pendentes else (solicitacoes[0] if solicitacoes else {
        "descricao": "Solicita verificacao do modulo de purificacao de agua."
    })

    prompt = f"""\n============================================================
Few-shot prompt:

Classifique a solicitação da tripulação abaixo em uma das categorias: 
"manutencao", "recurso", "emergencia" ou "administrativo".

Exemplo 1:
Solicitação: "Preciso de mais filtros de ar para o módulo de purificação, os atuais estão saturados."
Categoria: recurso

Exemplo 2:
Solicitação: "O painel de controle do Módulo 3 está soltando faíscas."
Categoria: emergencia

Exemplo 3:
Solicitação: "Solicito revisão programada dos motores da nave antes da próxima órbita."
Categoria: manutencao

Exemplo 4:
Solicitação: "Preciso que assinem o relatório de horas da equipe deste mês."
Categoria: administrativo

Agora classifique esta solicitação:
Solicitação: "{alvo['descricao']}"
Categoria:

Saída:
Categoria: manutencao
"""
    return prompt


def montar_prompt_saida_estruturada(solicitacao_nova):
    """Monta um prompt que orienta a IA a analisar uma solicitação
    e retornar a resposta em formato JSON estruturado."""
    prompt = f"""\n============================================================
Saída estruturada:

Você é um assistente de análise operacional de uma colônia espacial.

Analise a solicitação da tripulação abaixo e retorne a classificação em formato JSON.

Regras de saída:
- Responda SOMENTE com um objeto JSON válido.
- Não inclua texto explicativo antes ou depois.
- Não use blocos de markdown (```).
- Siga exatamente esta estrutura:

{{
  "categoria": "manutencao | suprimentos | seguranca | administrativo",
  "urgencia_estimada": "baixa | media | alta | critica",
  "modulo_relacionado": "string ou null se não identificado",
  "requer_acao_imediata": true ou false
}}

Solicitação: "{solicitacao_nova}"

Saída: 
{{
  "categoria": "suprimentos",
  "urgencia_estimada": "baixa",
  "modulo_relacionado": "Alojamento",
  "requer_acao_imediata": false
}}
"""
    return prompt


def ia_simulada():
    """Executa a simulação das estratégias de IA, carregando os dados
    e exibindo os prompts zero-shot, few-shot e de saída estruturada."""
    dados_zero_shot = carregar_json("alertas.json")
    dados_few_shot = carregar_json("solicitacoes.json")
    dados_saida_estruturada = "Solicita reposicao de racoes no setor de alojamento."
    prompt_zero_shot = montar_prompt_resumo_alertas(dados_zero_shot)
    prompt_few_shot = montar_prompt_classificar_solicitacao(dados_few_shot)
    saida_estruturada = montar_prompt_saida_estruturada(dados_saida_estruturada)
    print(prompt_zero_shot)
    print(prompt_few_shot)
    print(saida_estruturada)


# ============================================================
# MENU PRINCIPAL
# ============================================================


def menu():
    while True:
        print("\n")
        print("╔════════════════════════════════════════════╗")
        print("║       AURORA SIGER - NCAS                  ║")
        print("║       Núcleo Cognitivo                     ║")
        print("╠════════════════════════════════════════════╣")
        print("║ 1. Cadastrar registro TXT (modo a)         ║")
        print("║ 2. Consultar registros TXT (modo r)        ║")
        print("║ 3. Cadastrar alerta (JSON)                 ║")
        print("║ 4. Cadastrar solicitação (JSON)            ║")
        print("║ 5. Consultar dados JSON                    ║")
        print("║ 6. Recarregar dados JSON                   ║")
        print("║ 7. Inicializar arquivo TXT (modo x)        ║")
        print("║ 8. Ler cabeçalho do TXT (readline)         ║")
        print("║ 9. Corrigir último registro (modo r+)      ║")
        print("║ 10. IA simulada                            ║")
        print("║ 11. Consultar módulo                       ║")
        print("║ 0. Sair                                    ║")
        print("╚════════════════════════════════════════════╝")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_registro()

        elif opcao == "2":
            ler_registros()

        elif opcao == "3":
            cadastrar_alerta()

        elif opcao == "4":
            cadastrar_solicitacao()

        elif opcao == "5":
            exibir_json()

        elif opcao == "6":
            dados_modulos = carregar_json("dados_colonia.json")
            dados_modulos = validar_estrutura_json(dados_modulos)
            dados_alertas = carregar_json("alertas.json")
            dados_solicitacoes = carregar_json("solicitacoes.json")
            print("\n[OK] JSON carregado com sucesso.")
            print(
                f"Módulos: {len(dados_modulos['modulos'])} | "
                f"Alertas: {len(dados_alertas.get('alertas', []))} | "
                f"Solicitações: {len(dados_solicitacoes.get('solicitacoes', []))} | "
                f"Interações: {len(dados_modulos['interacoes'])}"
            )

        elif opcao == "7":
            inicializar_arquivo_txt()

        elif opcao == "8":
            ler_cabecalho()

        elif opcao == "9":
            novo_texto = input("Digite o texto corrigido: ").strip()
            if novo_texto:
                corrigir_ultimo_registro(novo_texto)
            else:
                print("[ERRO] O texto não pode ficar vazio.")

        elif opcao == "10":
            ia_simulada()

        elif opcao == "11":
            main()
            
        elif opcao == "0":
            print("\nNCAS encerrado. Até a próxima!")
            break

        else:
            print("\n[ERRO] Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()
