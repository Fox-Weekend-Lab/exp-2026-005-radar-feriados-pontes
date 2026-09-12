# Radar de Feriados e Pontes

> Este projeto foi gerado automaticamente por IA e revisado por um agente automatizado, nao por uma pessoa. Leia o codigo antes de usar.

## Descrição

CLI em Python para consultar feriados públicos de um país, manter os feriados nacionais e indicar sugestões de emenda quando um feriado ocorre em uma terça-feira ou quinta-feira.

A consulta é feita por uma URL base configurada na variável de ambiente `NAGER_API_BASE_URL`. O programa acrescenta a ela o caminho `/api/v3/NextPublicHolidays/{country_code}`.

## Objetivo

Oferecer uma forma simples de listar feriados nacionais futuros para um código de país ISO 3166-1 alfa-2 e destacar dias úteis que podem ser usados como emenda:

- Feriado na terça-feira: sugestão de folga na segunda-feira anterior.
- Feriado na quinta-feira: sugestão de folga na sexta-feira seguinte.

## Como funciona

1. A CLI recebe um código de país como argumento posicional.
2. O código é removido de espaços, convertido para maiúsculas e validado como duas letras ASCII.
3. O cliente lê `NAGER_API_BASE_URL` e faz uma requisição HTTP com tempo limite de 10 segundos.
4. A resposta deve ser um JSON contendo uma lista de feriados.
5. Cada item precisa conter os campos `date`, `localName` e `global`.
6. Apenas itens cujo campo `global` seja `true` são exibidos.
7. As datas são validadas no formato `AAAA-MM-DD`.
8. A saída mostra a data, o dia da semana em português, o nome local e, quando aplicável, a sugestão de emenda.

Erros de argumento, configuração, comunicação HTTP, JSON inválido ou dados de feriado inválidos são apresentados em português e resultam em código de saída `1`.

## Arquitetura

- `requirements.txt`: define as dependências do projeto.
- `src/radar_feriados_pontes/__init__.py`: expõe `Holiday`, `HolidayDataError`, `build_holidays` e `normalize_country_code`.
- `src/radar_feriados_pontes/__main__.py`: implementa a interface de linha de comando, a renderização textual e o tratamento de erros.
- `src/radar_feriados_pontes/client.py`: lê a configuração da URL base e realiza a requisição HTTP para os próximos feriados públicos.
- `src/radar_feriados_pontes/service.py`: valida o código de país e os dados retornados, filtra feriados nacionais e calcula sugestões de emenda.
- `tests/conftest.py`: arquivo de configuração compartilhada dos testes.
- `tests/test_cli.py`: testes da interface de linha de comando.
- `tests/test_client.py`: testes do cliente HTTP.
- `tests/test_service.py`: testes das regras de validação e transformação de feriados.

A dependência HTTP está isolada em `client.py`, enquanto as regras de validação e de cálculo de emenda permanecem em `service.py`.

## Tecnologias

- Python 3.11+
- `requests`
- `pytest` para execução dos testes
- Biblioteca padrão do Python, incluindo `argparse`, `dataclasses`, `datetime` e `os`

## Instalacao

Instale as dependências com:

```bash
python -m pip install -r requirements.txt
```

O pacote está no diretório `src/` e o projeto não possui arquivo de instalação. Portanto, é necessário incluir `src/` em `PYTHONPATH` ao executar o módulo.

## Configuracao

A aplicação lê a seguinte variável de ambiente:

| Variável | Obrigatória | Valor padrão | Descrição |
| --- | --- | --- | --- |
| `NAGER_API_BASE_URL` | Sim | Sem valor padrão | URL base da API de feriados. O programa adiciona `/api/v3/NextPublicHolidays/{country_code}` a essa URL. |

Se a variável estiver ausente ou vazia, a aplicação informa um erro de configuração.

Exemplo de definição usando um marcador de valor:

```bash
NAGER_API_BASE_URL=<url-da-api>
```

## Uso

Execute o pacote informando um código ISO de país com duas letras.

Linux/macOS:

```bash
PYTHONPATH=src python -m radar_feriados_pontes BR
```

Windows (PowerShell):

```powershell
$env:PYTHONPATH="src"; python -m radar_feriados_pontes BR
```

O código de país é normalizado para maiúsculas. Por exemplo, `br` é tratado como `BR`.

## Exemplos

Com `NAGER_API_BASE_URL` configurada, uma execução para o Brasil pode produzir uma saída no formato:

```text
Feriados nacionais para BR:
AAAA-MM-DD (terça-feira) - Nome local do feriado
  Sugestão de emenda: folgar em AAAA-MM-DD (segunda-feira).
AAAA-MM-DD (quinta-feira) - Outro nome local do feriado
  Sugestão de emenda: folgar em AAAA-MM-DD (sexta-feira).
```

Quando não houver feriados nacionais após a filtragem, a saída será:

```text
Feriados nacionais para BR:
Nenhum feriado nacional foi encontrado.
```

Um código inválido, como um valor que não tenha exatamente duas letras ASCII, resulta em uma mensagem de erro em `stderr` e código de saída `1`.

## Testes

Execute os testes com:

```bash
python -m pytest
```

Os testes não acessam a rede de verdade.

## Limitacoes

- A URL da API não é definida no código: `NAGER_API_BASE_URL` precisa ser configurada antes da execução.
- A aplicação depende da disponibilidade da API configurada e da compatibilidade de sua resposta com o formato esperado.
- Somente feriados cujo campo `global` seja booleano `true` são listados.
- A validação exige os campos `date`, `localName` e `global` em todos os itens recebidos, inclusive nos itens que não são nacionais.
- A regra de emenda abrange apenas feriados em terça-feira e quinta-feira.
- A sugestão de emenda não confirma disponibilidade de folga, políticas corporativas ou escolares.
- Não há persistência de dados, interface web, exportação de calendário ou consulta de múltiplos países em uma mesma execução.

## O que foi aprendido

O experimento separa a comunicação HTTP das regras de domínio, permitindo que a validação de dados, a filtragem de feriados nacionais e o cálculo de emendas sejam mantidos em funções independentes. Também demonstra a importância de validar respostas externas antes de apresentá-las ao usuário e de transformar falhas de configuração e comunicação em mensagens compreensíveis em português.

## Possivel aplicacao na FOX

Pode servir como ponto de partida para um utilitário de planejamento de equipes, ajudando a visualizar feriados nacionais e possíveis períodos de emenda ao organizar agendas e capacidade operacional.

## Status

O relatório de testes recebido informa sucesso: **22 testes passaram, de 22 testes coletados**.
