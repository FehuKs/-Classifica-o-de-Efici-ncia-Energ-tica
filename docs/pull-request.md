# Tornar reproduzível o experimento de eficiência energética

O estudo dependia de estado compartilhado no notebook, instalação implícita e disponibilidade da UCI. Esta mudança permite executar o mesmo protocolo pelo notebook ou CLI, com aquisição/validação de dados, pipelines de treinamento e relatórios separados.

## Mudanças

- Mantém mediana global de Y1, split 70/30 com semente 42 e os três modelos com seus parâmetros originais.
- Adiciona leitura de CSV local, validação de esquema e erros de acesso acionáveis.
- Encapsula scaler e classificador para KNN e regressão logística, ajustados apenas no treino.
- Exporta JSON com versões/protocolo, CSV e sete visualizações; remove saídas históricas do notebook para evitar confusão com uma nova execução.
- Substitui conclusões fixas por comparação calculada, documentando limitações do estudo.
- Adiciona pacote instalável, versões de dependências, oito testes, CI e instruções completas no README.

## Validação executada

- `python -m unittest discover -s tests -v`: 8 testes passaram, incluindo CLI como subprocesso, equivalência das predições ao protocolo original e relatórios repetíveis.
- Notebook completo: 5 células de código executadas com CSV sintético de teste, usando nbclient; o arquivo versionado mantém DATA_CSV=None e não contém resultados fabricados.
- Instalação com requirements.lock e instalação editável sem dependências/isolamento de build: passaram.
- `python -m pip check` e `git diff --check`: passaram.
- Validação adicional com ENB2012_data.xlsx fornecida pelo autor: CLI e notebook passaram; as predições dos três modelos são idênticas às do código original sobre os mesmos dados. Acurácias: 96,10%, 97,40% e 97,84%. Download remoto da UCI permanece bloqueado.

## Limites

A equivalência foi verificada com dados sintéticos e a planilha original enviada pelo autor, convertida para CSV. O download atual da fonte UCI não pôde ser validado. A mediana global mantém a definição retrospectiva da tarefa; não representa avaliação prospectiva ou certificação energética. Tempos dos pipelines incluem ajuste do scaler. A execução remota do GitHub Actions ainda não foi observada.

Sem LLM, serviços pagos, API de inferência ou mudanças metodológicas adicionais.
