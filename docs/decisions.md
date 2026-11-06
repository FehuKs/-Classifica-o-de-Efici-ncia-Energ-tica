# Decisões de engenharia

## Preservar o experimento antes de evoluir a metodologia

O projeto original consistia em oito células de notebook, com instalação implícita, download obrigatório, estado compartilhado e relatórios acoplados ao treinamento. A refatoração mantém os hiperparâmetros, a ordem dos atributos, a divisão e a definição das classes. O notebook continua sendo a apresentação do estudo; seus gráficos agora são produzidos pelos módulos reutilizáveis.

## Limites do significado de eficiência

Classe 0 significa Y1 menor ou igual à mediana; classe 1 significa Y1 acima dela. “Alta/Baixa Eficiência” são os nomes históricos dessa comparação relativa, não critérios normativos. A mediana global mantém o benchmark retrospectivo. Alterar esse limiar ou o split mudaria a pergunta experimental e exige avaliação separada.

## Aquisição e validação

CSV local permite reuso de uma cópia do dataset quando o serviço externo estiver indisponível. O carregador não baixa fontes alternativas nem fabrica dados. A validação exige X1–X8 e Y1 numéricos e finitos, alinhamento das linhas e uma classificação viável. Não pretende validar todas as restrições físicas possíveis de edifícios.

## Avaliação e apresentação

Os pipelines encapsulam o scaler e o classificador, com ajuste exclusivo no treino. O relatório usa os resultados calculados; o notebook escolhe os melhores F1 macro dinamicamente e preserva empates. A CLI publica todas as métricas sem impor um vencedor universal. Tempos com perf_counter incluem pré-processamento do pipeline, diferentemente do antigo tempo exclusivo de fit do classificador.

## Validação e evidência

A suíte independente de rede usa dados sintéticos explicitamente identificados. A equivalência das predições é comparada à sequência original de split/scaler/fit. Há testes do contrato UCI simulado e geração real de gráficos e JSON/CSV. Isso não equivale a reproduzir as métricas do dataset UCI.

No onboarding, a fonte UCI retornou 403 pelo proxy; imports, instalação e kernel funcionaram. A execução real continua sendo uma verificação separada dependente de rede. Não foram publicados novos números de acurácia do dataset real.

## Escopo

Não foram adicionados LLMs, serviços pagos, API HTTP, Docker ou ferramentas de orquestração. Uma CLI e unittest atendem à automação e validação atuais sem aumentar a infraestrutura necessária. O workflow de CI foi escrito para GitHub Actions; sua execução remota precisa ser observada depois de publicar a branch.

Verificações locais desta implementação: oito testes passaram; as cinco células de código do notebook executaram com CSV sintético de teste. Instalação pelo lock, instalação editável, pip check e git diff --check passaram. A chamada real à UCI falhou com erro de acesso; métricas históricas não foram reproduzidas.

## Validação posterior com os dados originais

Após o envio de ENB2012_data.xlsx pelo autor, CLI e notebook foram executados com sucesso usando sua conversão para CSV. As predições dos três modelos foram comparadas diretamente às do código original e são idênticas. Isso supera a limitação anterior de validação apenas sintética; o acesso remoto à UCI permanece não validado. Veja [resultados e divergências do relatório acadêmico](real-data-validation.md).
