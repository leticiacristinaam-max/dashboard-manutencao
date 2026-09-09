# dashboard-manutencao

Projeto de análise de dados aplicada à gestão da manutenção utilizando Python e Power BI.

## O que o dashboard faz

Um dashboard interativo em [Streamlit](https://streamlit.io/) para acompanhar indicadores de manutenção de equipamentos:

- **Indicadores**: quantidade de falhas, horas de reparo, custo total e MTTR (tempo médio de reparo).
- **Filtros**: por equipamento, tipo de falha e prioridade.
- **Gráficos**: tempo de reparo por equipamento, falhas por tipo e custo de manutenção por equipamento — atualizados automaticamente conforme os filtros e os dados cadastrados.
- **Cadastro de dados**: formulários para adicionar novas máquinas/equipamentos e para registrar novas manutenções (com data, tempo de reparo, tipo de falha, prioridade e custo), sem precisar editar planilhas manualmente.

## Como rodar

1. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

2. Rode o dashboard:

   ```bash
   streamlit run python/app.py
   ```

3. Acesse o endereço mostrado no terminal (por padrão, `http://localhost:8501`).

Também há um script `python/dashboard.py` que imprime os mesmos indicadores diretamente no terminal, sem interface gráfica.

## Estrutura de dados

- `dados/manutencao.csv`: histórico de manutenções, com as colunas `equipamento`, `data_falha`, `tempo_reparo_horas`, `tipo_falha`, `prioridade` e `custo_reparo`.
- `dados/equipamentos.csv`: máquinas/equipamentos cadastrados pela aba "Cadastrar dados" do dashboard, com as colunas `equipamento` e `tipo`.

Ambos os arquivos são atualizados automaticamente pelo próprio dashboard ao usar os formulários de cadastro — não é necessário editá-los à mão.

## Estrutura do projeto

```
python/
  app.py         # dashboard interativo (Streamlit)
  dashboard.py   # análise via terminal
dados/
  manutencao.csv
  equipamentos.csv
graficos/        # imagens de gráficos gerados a partir da análise
requirements.txt
```
