import pandas as pd

dados = pd.read_csv("dados/manutencao.csv")

print(dados)

print("Quantidade de registros:", len(dados))
print("Tempo total de reparo:", dados["tempo_reparo_horas"].sum(), "horas")

maior_reparo = dados.loc[dados["tempo_reparo_horas"].idxmax()]

print("Equipamento com maior tempo de reparo:")
print(maior_reparo)