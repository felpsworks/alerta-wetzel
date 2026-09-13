# Painel Wetzel Automotiva

Sistema web para o time da Qualidade da Wetzel Automotiva: consulta de Part
Number (PN Wetzel ⇄ PN Cliente), geração de imagem de alerta/reclamação para
envio no WhatsApp, e Gestão CS1 (Controle de Estação de Verificação) com
exportação em PDF pronta para impressão em folha A4.

O app roda em dois modos, sem precisar de nenhuma mudança de código:

- **Standalone/offline** — abrindo `index.html` direto no navegador, ou
  hospedado como site estático (é assim que roda hoje no GitHub Pages, em
  <https://felpsworks.github.io/alerta-wetzel/>). Cada computador guarda seus
  próprios dados **só naquele navegador** (`localStorage`), sem
  compartilhamento entre máquinas nem backup automático.
- **Interno, com banco de dados** — rodando `python app.py` (Flask +
  SQLite). Todos os computadores que acessarem pela rede da empresa
  compartilham o **mesmo banco de dados central** — é este o modo pensado
  para uso definitivo pela empresa, e é o assunto deste README.

O front-end (`index.html`) detecta sozinho qual modo está em uso: ele tenta
falar com a API (`/api/store/...`); se responder, usa o banco de dados; se
não responder (modo standalone), cai automaticamente para o `localStorage`
de antes. Não existem dois arquivos/versões para manter — é o mesmo
`index.html` nos dois casos.

## Pré-requisitos

- Python 3.10 ou superior.

## Instalação

```bash
pip install -r requirements.txt
```

## Como rodar (modo interno, com banco de dados)

```bash
python app.py
```

O servidor sobe em `http://localhost:5000`. Como o `app.py` já está
configurado para escutar em `0.0.0.0`, outros computadores na mesma rede
também conseguem acessar pelo IP da máquina que está rodando o servidor, por
exemplo `http://192.168.1.50:5000` (veja o IP com `ipconfig`).

> **Antes de disponibilizar na rede da empresa**, o TI deve avaliar:
> - Rodar com `debug=False` e por trás de um servidor WSGI de produção
>   (ex.: `waitress`, `gunicorn`), em vez do servidor de desenvolvimento do
>   Flask usado hoje.
> - Adicionar autenticação — hoje o app não tem login nenhum; qualquer
>   pessoa com acesso à rede pode consultar, editar e excluir peças, fotos e
>   registros de CS1.
> - Rotina de backup do arquivo `data/app.db`.
> - Rodar como serviço do Windows (ou tarefa agendada) para o servidor subir
>   sozinho quando a máquina reiniciar, em vez de depender de alguém deixar
>   o terminal aberto.

## O que é compartilhado pelo banco de dados

- **Peças cadastradas** (lista de PN Wetzel ⇄ PN Cliente, usada na consulta
  e na aba Configuração).
- **Registros de CS1** (Controle de Estação de Verificação, aba Gestão
  CS1).
- **Fotos dos analistas** (usadas no card de resultado da consulta de PN).

Na primeira vez que o app roda sem nenhum dado salvo ainda, a lista de peças
começa com a base atual (a mesma que já está em uso hoje, embutida no
`index.html`); a partir daí, toda edição feita por qualquer computador passa
a ser salva no banco e aparece para todo mundo.

## Estrutura do projeto

```
index.html         Front-end completo (HTML + CSS + JS em um arquivo só)
consulta-pn.html    Link antigo — só redireciona para index.html
app.py              Servidor Flask: serve o index.html e a API do banco
db.py               Conexão SQLite e schema da tabela
requirements.txt    Dependências Python
data/app.db         Banco de dados SQLite (criado ao rodar o app; não versionado)
```

## Banco de dados

SQLite, em `data/app.db` (criado automaticamente na primeira execução). Uma
única tabela (`kv_store`) guarda as 3 coleções de dados acima, cada uma como
um registro JSON — o mesmo formato que o `index.html` já usava no
`localStorage`, só que agora centralizado no servidor.

Não é versionado no Git (veja `.gitignore`) por conter dados reais de
clientes assim que o sistema entrar em uso.

## Modo standalone (sem instalar nada)

Continua funcionando como sempre: basta abrir `index.html` direto no
navegador, ou publicar como site estático (GitHub Pages, intranet sem
Python, etc.). Nesse modo os dados ficam só no navegador de cada pessoa —
útil para demonstração ou para quem não tem o Python instalado, mas não
substitui o modo com banco de dados para uso real da empresa.
