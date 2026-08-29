import pandas as pd

# Carregar os dados
dados = pd.read_csv("dados/manutencao.csv")

# Mostrar a base
print("\n===== BASE DE MANUTENÇÃO =====")
print(dados)

# Indicadores
quantidade_falhas = len(dados)
tempo_total = dados["tempo_reparo_horas"].sum()
custo_total = dados["custo_reparo"].sum()
custo_medio = dados["custo_reparo"].mean()

# Equipamento com maior tempo total de reparo
tempo_por_equipamento = dados.groupby("equipamento")["tempo_reparo_horas"].sum()
equipamento_maior_tempo = tempo_por_equipamento.idxmax()

# Equipamento com maior custo de manutenção
custo_por_equipamento = dados.groupby("equipamento")["custo_reparo"].sum()
equipamento_maior_custo = custo_por_equipamento.idxmax()

# Tipo de falha mais frequente
falhas_por_tipo = dados["tipo_falha"].value_counts()
tipo_falha_mais_frequente = falhas_por_tipo.idxmax()

# Quantidade de falhas de alta prioridade
falhas_alta_prioridade = (dados["prioridade"] == "Alta").sum()

# Mostrar resultados
print("\n===== INDICADORES DE MANUTENÇÃO =====")
print(f"Quantidade de falhas: {quantidade_falhas}")
print(f"Tempo total de reparo: {tempo_total} horas")
print(f"Custo total de manutenção: R$ {custo_total:,.2f}")
print(f"Custo médio por reparo: R$ {custo_medio:,.2f}")

print(f"\nEquipamento com maior tempo de reparo: {equipamento_maior_tempo}")
print(f"Tempo por equipamento:")
print(tempo_por_equipamento)

print(f"\nEquipamento com maior custo de manutenção: {equipamento_maior_custo}")
print(f"Custo por equipamento:")
print(custo_por_equipamento)

print(f"\nTipo de falha mais frequente: {tipo_falha_mais_frequente}")
print(falhas_por_tipo)

print(f"\nFalhas de alta prioridade: {falhas_alta_prioridade}")
