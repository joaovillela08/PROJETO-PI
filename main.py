# Arquivo principal do sistema eleitoral.
# Responsável por executar o menu e controlar as funcionalidades:
# cadastro de candidatos, cadastro de eleitores, votação e apuração dos votos.
#variaveis lista 
import random
import string
from datetime import datetime
import mysql.connector

def conectar():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Carotenos130',
        database='Projeto_integrador'
    )

# ================= LOGS =================
eleitores=[]
mesario=[]
ARQUIVO_LOG = "logs_ocorrencias.txt"


def registrar_log(mensagem):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(ARQUIVO_LOG, "a", encoding="utf-8") as log:

        log.write(f"[{timestamp}] {mensagem}\n")


def exibir_logs():

    print("\n--- ACESSO AOS LOGS ---")

    eleitor = buscar_eleitor(
        input("Título de eleitor: "),
        input("4 primeiros dígitos do CPF: "),
        input("Chave de acesso: ")
    )

    if not eleitor:

        registrar_log(
            "ALERTA: Tentativa de acesso negado aos logs"
        )

        print("Dados inválidos.")
        return

    if not eleitor["mesario"]:

        registrar_log(
            "ALERTA: Tentativa de acesso não autorizado aos logs"
        )

        print("Apenas mesários podem acessar os logs.")
        return

    print("\n--- LOGS DE OCORRÊNCIAS ---")

    try:

        with open(ARQUIVO_LOG, "r", encoding="utf-8") as log:

            conteudo = log.read()

            if conteudo.strip() == "":
                print("Nenhum log registrado.")
            else:
                print(conteudo)

    except FileNotFoundError:

        print("Arquivo de logs não encontrado.")


# ================= DADOS =================


candidatos = {
    "10": {"nome": "Candidato 1", "partido": "ABC", "votos": 0},
    "20": {"nome": "Candidato 2", "partido": "DEF", "votos": 0},
    "30": {"nome": "Candidato 3", "partido": "ABC", "votos": 0}
}

votacao_aberta = False
zeresima_realizada = False


# ================= AUXILIARES =================

def gerar_codigo(tam=8):

    caracteres = string.ascii_uppercase + string.digits

    return ''.join(random.choices(caracteres, k=tam))




# ================= VALIDAÇÕES =================

def validar_cpf(cpf):

    cpf = cpf.replace(".", "").replace("-", "").strip()

    if not cpf.isdigit() or len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    for qtd in [9, 10]:

        soma = sum(
            int(cpf[i]) * ((qtd + 1) - i)
            for i in range(qtd)
        )

        digito = 0 if soma % 11 < 2 else 11 - soma % 11

        if digito != int(cpf[qtd]):
            return False

    return True


def validar_titulo(titulo):

    titulo = titulo.strip()

    if not titulo.isdigit() or len(titulo) != 12:
        return False

    numero = titulo[:8]
    uf = titulo[8:10]

    pesos = [2, 3, 4, 5, 6, 7, 8, 9]

    soma = sum(int(numero[i]) * pesos[i] for i in range(8))

    dv1 = 0 if soma % 11 == 10 else soma % 11

    soma = int(uf[0]) * 7 + int(uf[1]) * 8 + dv1 * 9

    dv2 = 0 if soma % 11 == 10 else soma % 11

    return dv1 == int(titulo[10]) and dv2 == int(titulo[11])


# ================= GERENCIAMENTO =================

def cadastrar_eleitor():

    print("\n--- CADASTRO DE ELEITOR ---")

    nome = input("Nome completo: ")
    cpf = input("CPF: ")
    titulo = input("Título de eleitor: ")

    if not validar_cpf(cpf):
        print("CPF inválido!")
        return

    if not validar_titulo(titulo):
        print("Título inválido!")
        return

    cpf = cpf.replace(".", "").replace("-", "").strip()

    for e in eleitores:

        if e["cpf"] == cpf or e["titulo"] == titulo:
            print("CPF ou título já cadastrado!")
            return

    mesario = input("Atuará como mesário? (S/N): ").upper()

    if mesario not in ["S", "N"]:
        print("Opção inválida!")
        return

    mesario_db = 1 if mesario == "S" else 0

    chave = gerar_codigo()

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
                   INSERT INTO eleitores
                       (nome, cpf, titulo_eleitor, mesario, chave_acesso, status_voto)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   """, (
                       nome,
                       cpf,
                       titulo.strip(),
                       mesario_db,  # ← AQUI ESTÁ A CORREÇÃO
                       chave,
                       False
                   ))

    conexao.commit()

    cursor.close()
    conexao.close()


    print("\nCadastro realizado com sucesso!")
    print("Chave de acesso:", chave)


def listar_eleitores():
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM eleitores")
    eleitores = cursor.fetchall()

    if not eleitores:
        print("Nenhum eleitor cadastrado.")
        return

    for i, e in enumerate(eleitores, 1):
        print(f"""
    Eleitor {i}
    Nome: {e['nome']}
    CPF: {e['cpf']}
    Título: {e['titulo_eleitor']}
    Mesário: {e['mesario']}
    Status: {"Já votou" if e['status_voto'] else "Não votou"}
    """)

    cursor.close()
    conexao.close()


def buscar_por_titulo():

    print("\n--- BUSCAR ELEITOR ---")

    titulo = input("Título de eleitor: ").strip()

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM eleitores
        WHERE titulo_eleitor = %s
    """, (titulo,))

    e = cursor.fetchone()

    cursor.close()
    conexao.close()

    if not e:
        print("Eleitor não encontrado.")
        return

    print(f"""
Nome: {e['nome']}
CPF: {e['cpf']}
Título: {e['titulo_eleitor']}
Mesário: { "S" if e['mesario'] else "N" }
Status: {"Já votou" if e['status_voto'] else "Não votou"}
""")

def remover_eleitor():

    print("\n--- REMOVER ELEITOR ---")

    titulo = input("Título de eleitor: ").strip()

    conexao = conectar()
    cursor = conexao.cursor()

    # Primeiro verifica se existe
    cursor.execute(
        "SELECT id FROM eleitores WHERE titulo_eleitor=%s",
        (titulo,)
    )

    resultado = cursor.fetchone()

    if not resultado:
        print("Eleitor não encontrado.")
        cursor.close()
        conexao.close()
        return

    # Se existir, remove
    cursor.execute(
        "DELETE FROM eleitores WHERE titulo_eleitor=%s",
        (titulo,)
    )

    conexao.commit()

    print("Eleitor removido com sucesso!")

    cursor.close()
    conexao.close()


def menu_gerenciamento():

    while True:

        print("""
--- MENU GERENCIAMENTO ---
1 - Cadastrar Eleitor
2 - Listar Eleitores
3 - Buscar Eleitor
4 - Remover Eleitor
0 - Voltar
""")

        op = input("Escolha: ")

        if op == "1":
            cadastrar_eleitor()

        elif op == "2":
            listar_eleitores()

        elif op == "3":
            buscar_por_titulo()

        elif op == "4":
            remover_eleitor()

        elif op == "0":
            break

        else:
            print("Opção inválida.")


# ================= ABERTURA =================

def abrir_sistema():

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM voto")
    cursor.execute("UPDATE eleitores SET status_voto = 0")
    conexao.commit()
    cursor.close()
    conexao.close()

    global votacao_aberta, zeresima_realizada

    print("\n--- ABERTURA DO SISTEMA ---")

    eleitor = buscar_eleitor(
        input("Título de eleitor: "),
        input("4 primeiros dígitos do CPF: "),
        input("Chave de acesso: ")
    )

    if not eleitor:

        registrar_log(
            "ALERTA: Tentativa de acesso negado"
        )

        print("Erro de validação.")
        return

    if not eleitor["mesario"]:

        registrar_log(
            "ALERTA: Tentativa de acesso negado"
        )

        print("Apenas mesários podem abrir o sistema.")
        return

    for c in candidatos.values():
        c["votos"] = 0

    votacao_aberta = True
    zeresima_realizada = True

    registrar_log(
        "ABERTURA: Votação iniciada com sucesso. Total de votos zerado."
    )

    print("Sistema aberto com sucesso!")

    print("\n--- ZERÉSIMA ---")

    for numero, dados in candidatos.items():

        print(
            f"Número: {numero} | "
            f"{dados['nome']} | "
            f"Votos: {dados['votos']}"
        )


# ================= VOTAÇÃO =================
def buscar_eleitor(titulo, cpf4, chave):

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM eleitores
        WHERE titulo_eleitor = %s
        AND chave_acesso = %s
    """, (titulo.strip(), chave))

    eleitor = cursor.fetchone()

    cursor.close()
    conexao.close()

    if eleitor and eleitor["cpf"][:4] == cpf4:
        return eleitor

    return None

def realizar_voto():

        print("\n--- IDENTIFICAÇÃO DO ELEITOR ---")

        titulo = input("Título de eleitor: ")
        cpf4 = input("4 primeiros dígitos do CPF: ")
        chave = input("Chave de acesso: ")

        eleitor = buscar_eleitor(titulo, cpf4, chave)

        if not eleitor:
            registrar_log("ALERTA: Tentativa de acesso negado")
            print("Dados inválidos.")
            return

        if eleitor["status_voto"] == 1:
            registrar_log("ALERTA: Tentativa de voto duplo")
            print("Este eleitor já votou.")
            return

        print("\n--- CANDIDATOS ---")

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("SELECT * FROM candidatos")
        lista_candidatos = cursor.fetchall()

        if not lista_candidatos:
            print("Nenhum candidato cadastrado.")
            cursor.close()
            conexao.close()
            return

        for c in lista_candidatos:
            print(f"{c['numero']} - {c['nome']} ({c['partido']})")

        numero = input("Digite o número do candidato: ").strip()

        # Buscar id do candidato
        cursor.execute("""
                       SELECT id_candidato
                       FROM candidatos
                       WHERE numero = %s
                       """, (numero,))

        resultado = cursor.fetchone()

        if not resultado:
            print("Candidato inválido.")
            cursor.close()
            conexao.close()
            return

        id_candidato = resultado["id_candidato"]

        print("\n--- CONFIRMAÇÃO ---")

        print("Número:", numero)

        if input("Confirmar voto? (S/N): ").upper() != "S":
            print("Voto cancelado.")
            cursor.close()
            conexao.close()
            return

        # Gerar protocolo
        protocolo = gerar_codigo(10)
        protocolo1=protocolo


        # Inserir voto na tabela voto
        cursor.execute("""
                       INSERT INTO voto (id_eleitor, id_candidato, data_hora)
                       VALUES (%s, %s, NOW())
                       """, (eleitor["id"], id_candidato))

        # Atualizar eleitor
        cursor.execute("""
                       UPDATE eleitores
                       SET status_voto = 1,
                           protocolo   = %s
                       WHERE id = %s
                       """, (protocolo, eleitor["id"]))

        print("\nVoto registrado com sucesso!")
        print("Status atualizado para: Já votou")
        print("Protocolo:", protocolo1)

        conexao.commit()

        cursor.close()
        conexao.close()

        registrar_log("SUCESSO: Voto realizado com sucesso")






# ================= ENCERRAMENTO =================

def encerrar_sistema():

    global votacao_aberta

    print("\n--- ENCERRAMENTO DA VOTAÇÃO ---")

    eleitor = buscar_por_titulo(
        input("Título de eleitor: "),
        input("4 primeiros dígitos do CPF: "),
        input("Chave de acesso: ")
    )

    if not eleitor:

        registrar_log(
            "ALERTA: Tentativa de acesso negado"
        )

        print("Dados inválidos.")
        return

    if eleitor["mesario"] != "S":

        registrar_log(
            "ALERTA: Tentativa de acesso negado"
        )

        print("Apenas mesários podem encerrar o sistema.")
        return

    if input(
        'Deseja realmente encerrar a votação? (S/N): '
    ).upper() != "S":

        print("Encerramento cancelado.")
        return

    if input(
        "Digite novamente a chave de acesso: "
    ) != eleitor["chave"]:

        registrar_log(
            "ALERTA: Tentativa de acesso negado"
        )

        print("Chave incorreta. Encerramento cancelado.")
        return

    votacao_aberta = False

    registrar_log(
        "ENCERRAMENTO: Votação finalizada com sucesso."
    )

    print("\nSistema encerrado com sucesso!")
    print("Resultados consolidados.\n")

    menu_resultados()


# ================= RESULTADOS =================

def boletim_urna():

    print("\n--- BOLETIM DE URNA ---")

    ordenados = sorted(
        candidatos.items(),
        key=lambda x: x[1]["nome"]
    )

    for numero, dados in ordenados:

        print(
            f"{dados['nome']} "
            f"({numero}) - "
            f"{dados['partido']} "
            f"| {dados['votos']} votos"
        )


# ================= AUDITORIA =================

def auditoria():

    print("\n--- AUDITORIA ---")

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    print("Sistema aberto:", votacao_aberta)
    print("Zerésima realizada:", zeresima_realizada)

    cursor.execute("""
        SELECT 
            candidatos.numero,
            candidatos.nome,
            candidatos.partido,
            COUNT(voto.id_voto) AS total_votos
        FROM candidatos
        LEFT JOIN voto 
            ON voto.id_candidato = candidatos.id_candidato
        GROUP BY candidatos.id_candidato
        ORDER BY candidatos.numero
    """)

    resultados = cursor.fetchall()

    if not resultados:
        print("Nenhum voto registrado.")

    for r in resultados:
        print(
            f"{r['numero']} - "
            f"{r['nome']} | "
            f"Partido: {r['partido']} | "
            f"Votos: {r['total_votos']}"
        )

    cursor.close()
    conexao.close()


# ================= URNA =================

def menu_urna():

    if not zeresima_realizada:
        print("Erro: Zerésima não realizada.")
        return

    if not votacao_aberta:
        print("Sistema fechado.")
        return

    while True:

        print("""
--- URNA ---
1 - Votar
2 - Encerrar Sistema
0 - Voltar
""")

        op = input("Escolha: ")

        if op == "1":

            realizar_voto()

        elif op == "2":

            encerrar_sistema()

            if not votacao_aberta:
                break

        elif op == "0":

            break

        else:

            print("Opção inválida.")


# ================= MENU VOTAÇÃO =================

def menu_votacao():

    while True:

        print("""
--- MENU VOTAÇÃO ---
1 - Abrir Sistema
2 - Auditoria
3 - Acessar Urna
4 - Exibir Logs
0 - Voltar
""")

        op = input("Escolha: ")

        if op == "1":
            abrir_sistema()

        elif op == "2":
            auditoria()

        elif op == "3":
            menu_urna()

        elif op == "4":
            exibir_logs()

        elif op == "0":
            break

        else:
            print("Opção inválida.")


# ================= MENU PRINCIPAL =================

def menu_principal():

    while True:

        print("""
===== SISTEMA ELEITORAL =====
1 - Gerenciamento
2 - Votação
0 - Sair
""")

        op = input("Escolha: ")

        if op == "1":
            menu_gerenciamento()

        elif op == "2":
            menu_votacao()

        elif op == "0":
            print("Encerrando sistema...")
            break

        else:
            print("Opção inválida.")


# ================= EXECUÇÃO =================

menu_principal()
#até então foram gastas aproximadamente 10:00h de cada integrante no grupo apenas para o codigo (Gabriel Castro, Hyan Viotor e João vilela.)
