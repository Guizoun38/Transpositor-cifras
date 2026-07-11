# Transpositor de Cifras em Word

Aplicação Streamlit que importa uma cifra musical em `.docx`, transpõe o
tom indicado no cabeçalho e os acordes da música para uma nova tonalidade,
mantendo intacta toda a restante formatação e conteúdo do documento
(letra, estrutura, tabelas, cabeçalhos, rodapés, fontes, cores, etc.).

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
streamlit run app.py
```

## Como usar

1. Carregar o ficheiro Word (`.docx`) com a cifra.
2. Selecionar o tom original da música.
3. Selecionar o novo tom pretendido.
4. Clicar em "Transpor ficheiro".
5. Clicar em "Descarregar ficheiro" para obter a cópia transposta
   (o ficheiro original nunca é alterado).

## Como funciona

- A linha `Tom <nota>` no cabeçalho do documento é localizada e apenas a
  nota é substituída.
- Linhas identificadas como linhas de acordes (compostas maioritariamente
  por acordes, espaços, `/` e `|`) têm os seus acordes transpostos pela
  mesma distância em semitons entre o tom original e o novo tom.
- A escolha entre sustenidos e bemóis é feita automaticamente consoante a
  tonalidade de destino (ex: `Ab`, `Eb`, `Bb`, `Db`, `Gb`, `F` usam
  bemóis; `G`, `D`, `A`, `E`, `B`, `F#` usam sustenidos).
- Acordes com baixo invertido (ex: `Eb/G`) têm a nota principal e a nota
  do baixo transpostas separadamente.
- A extensão do acorde (`m`, `7`, `sus4`, `maj7`, `add9`, `dim`, `aug`,
  etc.) é sempre preservada.
- A letra da música, indicações musicais, observações e nomes de secções
  (ex: `[Intro]`, `[Refrão]`) nunca são alterados.
- A alteração é feita ao nível dos `run.text` de cada parágrafo (nunca
  `paragraph.text`), para preservar fonte, tamanho, cor, negrito, itálico,
  sublinhado e restante formatação do Word.
- São verificados parágrafos do corpo do documento, tabelas, cabeçalhos e
  rodapés.

## Limitações desta primeira versão

- Suporta apenas ficheiros `.docx` (não PDF, imagem, TXT ou OCR).
- Não converte Nashville Number System.
- Não identifica automaticamente o tom original — tem de ser selecionado.
- Não corrige acordes escritos incorretamente no documento original.
- Não altera a estrutura, a letra ou as indicações musicais da cifra.
