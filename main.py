# Arquivo principal do sistema eleitoral.
# Responsável por executar o menu e controlar as funcionalidades:
# cadastro de candidatos, cadastro de eleitores, votação e apuração dos votos.
#variaveis lista 
candidatos = {}
eleitores = set()
votos = {}

# -------- VALIDAÇÃO DE CPF --------
def validar_cpf(cpf):
    cpf = cpf.replace(".", "").replace("-", "").strip()

    if not cpf.isdigit():
        return False

    contador = 0
    for _ in cpf:
        contador += 1

    if contador != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    for i in range(9, 11):
        soma = 0
        for j in range(i):
            soma += int(cpf[j]) * ((i + 1) - j)

        digito = (soma * 10) % 11
        if digito == 10:
            digito = 0

        if digito != int(cpf[i]):
            return False

    return True

def menu_principal():
    print("\n--- Sistema Eleitoral ---")
    print("1 - Cadastros")
    print("2 - Votar")
    print("3 - Ver resultado")
    print("0 - Sair")

def menu_cadastros():
    opcao = ""
    while opcao != "0":
        print("\n--- Menu de Cadastros ---")
        print("1 - Cadastrar candidato")
        print("2 - Cadastrar eleitor")
        print("0 - Voltar")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_candidato()
        elif opcao == "2":
            cadastrar_eleitor()
        elif opcao == "0":
            print("Voltando...")
        else:
            print("Opção inválida!")

def cadastrar_candidato():
    print("\n--- Cadastro de Candidato ---")
    nome = input("Nome do candidato: ")
    if nome in candidatos:
        print("Candidato já cadastrado!")
    else:
        candidatos[nome] = 0
        print("Candidato cadastrado com sucesso!")

def cadastrar_eleitor():
    print("\n--- Cadastro de Eleitor ---")
    cpf = input("CPF do eleitor: ")

    if not validar_cpf(cpf):
        print("CPF inválido!")
        return

    cpf = cpf.replace(".", "").replace("-", "").strip()

    if cpf in eleitores:
        print("Eleitor já cadastrado!")
    else:
        eleitores.add(cpf)
        print("Eleitor cadastrado com sucesso!")
