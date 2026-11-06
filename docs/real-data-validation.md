# Validação com os dados originais

O autor forneceu `ENB2012_data.xlsx` e o relatório acadêmico original. Os anexos foram usados como dados e referência histórica, sem modificar ou publicar os documentos pessoais. A planilha foi convertida para CSV fora do checkout para usar a interface local existente; suporte nativo a XLSX não foi adicionado.

SHA-256 da planilha: `0089fcffc1415e41e2ff63730cca5280efe54fc43d722dfde1b0aaa808e35dc4`.

## Verificações executadas

- 768 linhas, X1–X8, Y1 e Y2; nenhum valor ausente.
- Mediana global de Y1: 18,95; classes 0 e 1: 384 exemplos cada.
- Holdout original: 537 exemplos de treino e 231 de teste.
- CLI com CSV real: sucesso, com JSON/CSV e sete gráficos.
- Cinco células de código do notebook refatorado: executadas com os dados reais. O caminho local foi aplicado apenas à cópia em memória, sem incorporar caminhos de anexos ao notebook versionado.
- Código original do commit ca2a97f: executado sem a célula de instalação, substituindo somente a aquisição da UCI pelos dados da planilha. As predições dos três modelos foram comparadas por igualdade exata às do fluxo refatorado e coincidiram integralmente.

| Modelo | Acertos / teste | Acurácia | F1 macro |
|---|---:|---:|---:|
| Árvore de decisão | 222 / 231 | 96,10% | 0,960682 |
| KNN (K=5) | 225 / 231 | 97,40% | 0,973916 |
| Regressão logística | 226 / 231 | 97,84% | 0,978251 |

São resultados deste holdout, não uma estimativa universal de desempenho. Os tempos não são comparados ao PDF: dependem de hardware, versões e do escopo da medição.

## Diferenças em relação ao relatório acadêmico

- A tabela da página 5 apresenta 96%, 98% e 98%. A execução atual coincide com as saídas do notebook original, mas não reproduz exatamente essa tabela. Não é possível determinar a causa sem o registro da execução usada no PDF.
- As conclusões das páginas 5 e 7 favorecem o KNN. Neste holdout, a regressão logística tem maior acurácia e F1 macro; não há empate exato. Menor tempo de ajuste do KNN não comprova menor custo total, que também inclui inferência.
- X5 tem 384 exemplos de altura 3,5 e 384 de altura 7,0. Ter duas categorias não significa desbalanceamento; a afirmação da página 3 não se sustenta pela frequência observada.
- As alegações de aptidão comercial/auditoria da página 8 excedem esta evidência: não há validação externa, teste em produção ou certificação normativa.
- Ausência de valores ausentes confirma completude nesses campos, não independência das amostras ou integridade científica completa. Balanceamento global também não elimina todos os vieses do treino.

O PDF original foi preservado como registro acadêmico. As conclusões técnicas atuais ficam nesta documentação, sem atribuir resultados novos ao documento histórico.

## Limites restantes

O download direto da UCI continua bloqueado no ambiente. A validação com arquivo local comprova o workflow com os dados fornecidos, não a disponibilidade da API externa. Os anexos e artefatos gerados não foram incluídos no Git; para repetir a execução é necessário obter a planilha do autor ou uma cópia oficial equivalente, convertê-la para CSV com os cabeçalhos preservados e executar o comando local documentado no README.
