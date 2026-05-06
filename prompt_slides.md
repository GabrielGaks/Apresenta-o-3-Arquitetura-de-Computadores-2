# PROMPT PARA GERAÇÃO DE SLIDES — Wolfenstein 3D Black Book

Cole este prompt diretamente no Claude (claude.ai) para gerar os slides em HTML/CSS.

---

## PROMPT COMPLETO:

```
Crie uma apresentação completa em HTML/CSS/JS com slides educativos sobre o renderizador 3D do Wolfenstein 3D, baseada no conteúdo abaixo. 

---

### REQUISITOS VISUAIS OBRIGATÓRIOS:

**Tema e visual:**
- Tema CLARO (fundo branco ou cinza muito claro, #f8f9fa ou #ffffff)
- Tipografia grande: títulos em 48-64px, subtítulos em 32-40px, tópicos em 24-28px
- Fonte moderna e legível: 'Segoe UI', Inter ou similar
- Sombras suaves, bordas arredondadas, cards com profundidade (box-shadow)
- Paleta de cores: azul-escuro (#1a1a2e), azul médio (#2563eb), laranja de destaque (#f59e0b), texto escuro (#1f2937)

**Objetos 3D em CSS:**
- Cada slide deve ter pelo menos UM elemento 3D construído em CSS puro (transform: perspective, rotateX, rotateY, translateZ)
- Exemplos de objetos 3D para cada slide estão especificados abaixo
- Os objetos 3D devem ser animados com @keyframes (rotação suave, flutuação, pulso)
- Use gradientes para dar profundidade e realismo

**Espaço para imagem do livro:**
- Cada slide deve ter um bloco reservado assim:
  
  ┌─────────────────────────────────────┐
  │         📷 IMAGEM DO LIVRO          │
  │   [substitua por img src="..."]     │
  │         (figura 4.XX)               │
  └─────────────────────────────────────┘
  
- O bloco deve ter borda tracejada (#2563eb), fundo #eff6ff, padding 16px
- Indicar qual figura do livro vai ali (ex: "Figura 4.53", "Figura 4.55", etc.)

**Formato dos tópicos (para narrador):**
- NÃO escreva parágrafos — apenas bullets curtos de 1 linha
- Cada bullet é uma deixa para o narrador expandir
- Máximo 5 bullets por slide
- Use ícones Unicode ou emojis simples para prefixar bullets (▶ → ✦ ●)

---

### ESTRUTURA DA APRESENTAÇÃO (9 slides):

**SLIDE 1 — Capa**
- Título: "Renderizador 3D do Wolfenstein 3D"
- Subtítulo: "Seção 4.7 — Como a magia acontecia em um 386"
- Objeto 3D: Cubo girando lentamente com face texturizada (simule tijolo com gradiente)
- Sem bullets — apenas apresentação visual

**SLIDE 2 — Correção do Efeito Fisheye (4.7.6)**
- Título grande: "Correção do Efeito Fisheye"
- Bullets:
  ▶ Raios medidos com distância direta (d) causam distorção nas bordas
  ▶ Solução: usar a distância projetada (z) no eixo do jogador
  ▶ Linhas retas das paredes ficam geometricamente corretas
  ▶ Diferença visível: cenas antes/depois nas págs. 180-181
- Objeto 3D: Dois raios divergindo de um ponto (player) em perspectiva — um curvo (incorreto) e um reto (correto)
- Espaço para imagem: Figura 4.53 (translação map space → player space)

**SLIDE 3 — Desenhando as Paredes (4.7.7)**
- Título grande: "Desenhando Paredes em um 386"
- Bullets:
  ▶ Altura da coluna calculada → desenhar coluna de texels escalada
  ▶ CPU 386 é limitada: escalar 64 texels é caro
  ▶ Wolfenstein supera outros engines da época com 2 otimizações
  ▶ Segredo: Compiled Scalers + Deferred Column Rendering
- Objeto 3D: Parede 3D em perspectiva com colunas verticais destacadas em cores diferentes
- Sem imagem neste slide

**SLIDE 4 — Compiled Scalers (4.7.7.1)**
- Título grande: "Compiled Scalers"
- Bullets:
  ▶ Abordagem genérica usa loop + acumulador → muitas instruções
  ▶ Solução: gerar funções hard-coded para cada altura em tempo de startup
  ▶ 256 funções pré-compiladas eliminam o loop completamente
  ▶ Custo: 83.160 bytes de RAM para 136 scalers
  ▶ Benefício: de dezenas de instruções para apenas 3-7 por pixel
- Objeto 3D: Pilha de "fichas" 3D empilhadas representando as 136 funções geradas, com seta apontando para uma coluna de pixels na tela
- Espaço para imagem: Código de BuildCompScale gerando x86 (págs. 183-184)

**SLIDE 5 — Tradeoff RAM vs CPU**
- Título grande: "RAM vs CPU — O Tradeoff Clássico"
- Bullets:
  ▶ Versão original: 255 scalers = 178.479 bytes → caro demais
  ▶ Otimização: acima de 76px, pular alturas (78, 82, 86...)
  ▶ Resultado: 136 scalers = 83.160 bytes — custo aceitável
  ▶ Artefato visual mínimo ao usar o scaler errado
  ▶ Re-geração necessária ao redimensionar o canvas 3D
- Objeto 3D: Balança 3D com "RAM" de um lado e "CPU" do outro, inclinada para CPU (mais leve)
- Sem imagem neste slide

**SLIDE 6 — Deferred Column Drawing (4.7.7.2)**
- Título grande: "Deferred Column Drawing"
- Bullets:
  ▶ Colunas similares são agrupadas e desenhadas juntas em batch
  ▶ "Similar" = mesmo ponto na textura horizontal
  ▶ Até 8 colunas escritas com apenas 3 operações no VGA
  ▶ 50% das operações de escrita são evitadas
  ▶ Funciona melhor com paredes magnificadas (jogador perto)
- Objeto 3D: Sequência de colunas 3D agrupadas com seta mostrando batch write, banks VGA coloridos (0-3)
- Espaço para imagem: Screenshot com colunas "gratuitas" em rosa (págs. 194-195)

**SLIDE 7 — VGA Banks e Masks (4.7.7.2 cont.)**
- Título grande: "VGA Plane Masking"
- Bullets:
  ▶ Tela dividida em 4 banks VGA: colunas 0,4,8... no Bank 0; 1,5,9... no Bank 1
  ▶ Máscara de bits seleciona quais banks recebem a escrita simultaneamente
  ▶ Escrita alinhada = 1 pass; desalinhada = até 3 passes
  ▶ mapmasks[1/2/3] pré-calculadas para lookup em runtime
  ▶ Retorno antecipado quando máscara = 0
- Objeto 3D: Grade 3D de pixels dividida em 4 banks com cores distintas, bits de máscara flutuando acima
- Espaço para imagem: Figura 4.54 (layout VRAM/Screen com banks)

**SLIDE 8 — Texturing com Luz Pré-Baked (4.7.7.3)**
- Título grande: "Baked Light Texturing"
- Bullets:
  ▶ Artistas criaram cada textura duas vezes: iluminada e não-iluminada
  ▶ Parede vertical (eixo Y no mapa) → textura iluminada
  ▶ Parede horizontal (eixo X no mapa) → textura escura
  ▶ Efeito de luz direcional gratuito — zero custo em runtime
  ▶ Resultado: cenas com muito mais profundidade e realismo
- Objeto 3D: Corredor 3D com paredes verticais brilhantes e horizontais escuras, luz direcional simulada
- Espaço para imagem: Figura 4.55 (texturas lit/unlit) e Figura 4.56 (cena com/sem baked)

**SLIDE 9 — Portas e Push Walls (4.7.7.4 e 4.7.7.5)**
- Título grande: "Portas e Paredes Deslizantes"
- Bullets:
  ▶ Portas renderizadas diretamente pelo raycaster — sem espessura
  ▶ Array doorposition[64] guarda posição de cada porta (0=fechada, 0xFFFF=aberta)
  ▶ Raio testa: AX + ystep/2 < doorposition[index]
  ▶ Push walls: offset aplicado ao intercept do raio quando ativadas
  ▶ Tudo resolvido como casos especiais dentro do loop de raycasting
- Objeto 3D: Porta 3D em perspectiva se abrindo com trilho, raio de luz atravessando
- Espaço para imagem: Figura 4.57 (raio atravessando porta parcialmente aberta)

---

### NAVEGAÇÃO E CÓDIGO:
- Botões Anterior / Próximo centralizados abaixo de cada slide
- Contador de slides (ex: "3 / 9")
- Teclas ← → para navegar
- Transição suave entre slides (opacity + transform, 300ms)
- Todo o código em um único arquivo HTML autocontido (sem dependências externas)
- CSS e JS inline no mesmo arquivo

Gere o arquivo HTML completo e funcional.
```
