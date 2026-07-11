# Transpositor de Cifras V2

Aplicação Streamlit para transpor cifras em Word e PDF e converter entre acordes e Nashville Number System. A V2 preserva os comportamentos da V1 e separa a lógica musical do processamento de documentos e da interface.

## Funcionalidades

- Acordes → acordes, acordes → Nashville e Nashville → acordes.
- Extensões, acidentes e inversões (`Bbm7`, `Ebsus4`, `Eb/G`, `b7`, `5/7`).
- Processamento de corpo, tabelas, cabeçalhos e rodapés do Word por `run.text`.
- PDFs com texto selecionável, preservando páginas e conteúdo não musical.
- Deteção conservadora para proteger letras, secções, BPM e compasso.
- O original nunca é alterado; é sempre produzida uma nova cópia.

## Arquitetura

```text
domain/          modelos, regras musicais e erros
application/     pedidos, portas e casos de uso
infrastructure/  processadores DOCX e PDF
presentation/    interface Streamlit
tests/           testes unitários, sintéticos e fixtures reais
```

## Instalação e execução

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest
python -m streamlit run app.py
```

Para desenvolvimento e testes, instale `requirements-dev.txt` em vez de
`requirements.txt`.

## Publicação na internet

A aplicação está preparada para o Streamlit Community Cloud. Para manter os
documentos de teste protegidos, recomenda-se um repositório GitHub privado e a
aplicação Streamlit configurada como pública.

1. Criar um repositório privado no GitHub e enviar este projeto.
2. Aceder a <https://share.streamlit.io> e entrar com a conta GitHub.
3. Selecionar **Create app** e indicar o repositório, a branch e `app.py`.
4. Em **Advanced settings**, selecionar Python 3.12.
5. Após publicar, abrir **Share** e escolher **Make this app public**.
6. Partilhar o endereço permanente `https://...streamlit.app`.

O servidor recebe os ficheiros enviados pelo navegador para os processar em
memória. Não envie documentos confidenciais para uma instalação pública sem
avaliar previamente os requisitos de privacidade da organização.

Exemplos: `Ab Eb Fm Db` de Ab para C produz `C G Am F`; em Nashville produz `1 5 6m 4`. `19 5sus4 2m7 4` em C produz `C9 Gsus4 Dm7 F`.

## Limitações

O Word pode dividir texto entre runs; a aplicação faz substituições localizadas e mantém a formatação do primeiro run afetado. Substituições ambíguas devem ser revistas.

PDF é menos editável: só são suportados PDFs com texto selecionável, sem OCR. A fonte original pode não estar disponível, acordes maiores podem sofrer pequenos desalinhamentos e o resultado deve ser revisto. As páginas não são rasterizadas.

Os testes de integração criam documentos DOCX e PDF sintéticos em memória, sem
publicar documentos reais no repositório.
