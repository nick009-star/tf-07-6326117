import pyautogui
import time
import pandas as pd
import webbrowser
from pathlib import Path

arquivo_csv = Path(__file__).with_name("notas_alunos.csv")
url_forms = "https://forms.gle/TEqKGhhCR6f9smm77"
dados = pd.read_csv(arquivo_csv, sep=';', skipinitialspace=True,dtype=str, keep_default_na=False) 
dados["RA"] = dados["RA"].str.strip().str.replace(r"\D", "", regex=True).replace("", "0")
for coluna in ["Nota01", "TF01", "Nota02", "TF02"]:
    dados[coluna] = (
        dados[coluna]
        .str.strip()
        .str.upper()
        .replace({"FALTOU": "0", "FALTA": "0", "N/A": "0", "-": "0", "": "0"})
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
dados["Nota01"] = dados["Nota01"].clip(upper=10)
dados["Nota02"] = dados["Nota02"].clip(upper=10)
dados["TF01"] = dados["TF01"].clip(upper=2)
dados["TF02"] = dados["TF02"].clip(upper=2)

print(f"Registros na lista: {len(dados)}")

def mostrar_aluno(aluno):
    nota_final = aluno["Nota01"] * 0.8 + aluno["TF01"]
    nota_final_02 = aluno["Nota02"] * 0.8 + aluno["TF02"]
    nota_final_geral = (nota_final + nota_final_02) / 2

    print(f'{aluno["Nome"].strip()} | RA: {aluno["RA"]}')
    print(f'Nota Final 1: {nota_final}')
    print(f'Nota Final 2: {nota_final_02}')
    print(f"Nota final para o Forms: {nota_final_geral:.2f}")
    print(f"Situação: {'APROVADO' if nota_final_geral >= 7 else 'REPROVADO'}")


modo = input("Digite 1 para pesquisar um aluno ou 2 para enviar todos: ").strip()

if modo == "1":
    termo = input("Digite o RA (somente números) ou parte do nome: ").strip()

    if termo.isdigit():
        encontrados = dados[dados["RA"] == termo]
    else:
        nome_procurado = " ".join(termo.split()).casefold()
        nomes = dados["Nome"].str.strip().str.replace(r"\s+", " ", regex=True).str.casefold()
        encontrados = dados[nomes.str.contains(nome_procurado, regex=False)]

    if encontrados.empty:
        print("Nenhum aluno encontrado.")
    else:
        print("Alunos encontrados:")
        for numero, (_, aluno) in enumerate(encontrados.iterrows(), start=1):
            print(f'{numero} - {aluno["Nome"].strip()} (RA: {aluno["RA"]})')

        escolha = input("Digite o número do aluno que deseja consultar: ").strip()
        if escolha.isdigit() and 1 <= int(escolha) <= len(encontrados):
            aluno = encontrados.iloc[int(escolha) - 1]
            mostrar_aluno(aluno)
        else:
            print("Opção inválida; nenhum aluno foi selecionado.")

elif modo == "2":
    confirmacao = input(
        f"Isso enviará uma resposta para cada um dos {len(dados)} alunos. "
        "Digite ENVIAR TODOS para continuar: "
    ).strip()

    if confirmacao != "ENVIAR TODOS":
        print("Envio cancelado.")
    else:
        pyautogui.FAILSAFE = True
        webbrowser.open(url_forms)
        print("O Forms abriu. Em 20 segundos, clique no campo RA e não mexa no mouse durante o envio.")
        time.sleep(20)
        posicao_ra = pyautogui.position()

        for indice, (_, aluno) in enumerate(dados.iterrows(), start=1):
            nota_final = aluno["Nota01"] * 0.8 + aluno["TF01"]
            nota_final_02 = aluno["Nota02"] * 0.8 + aluno["TF02"]
            nota_final_geral = (nota_final + nota_final_02) / 2

            if indice > 1:
                pyautogui.hotkey("ctrl", "l")
                pyautogui.write(url_forms)
                pyautogui.press("enter")
                time.sleep(7)
                pyautogui.click(posicao_ra)

            valores = [
                str(aluno["RA"]),
                aluno["Nome"].strip(),
                str(aluno["Nota01"]),
                str(aluno["Nota02"]),
                str(aluno["TF01"]),
                str(aluno["TF02"]),
                f"{nota_final_geral:.2f}",
            ]

            for valor in valores:
                pyautogui.write(valor)
                pyautogui.press("tab")

            pyautogui.press("enter")
            print(f"Comando de envio executado para {indice}/{len(dados)}: {aluno['Nome'].strip()}")
            time.sleep(5)
else:
    print("Opção inválida. Execute novamente e escolha 1 ou 2.")