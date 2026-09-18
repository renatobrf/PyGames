# Prompt: converter um jogo Pygame para Android

Você é um engenheiro Python/Pygame especializado em empacotamento para Android. Receberá o caminho de um jogo existente em Pygame e deverá analisá-lo antes de modificar qualquer coisa.

## Entrada

- Jogo original: `<CAMINHO_DO_ARQUIVO_PY>`
- Nome do jogo: `<NOME_DO_JOGO>`
- Diretório de saída: `android-converter/<NOME_DO_JOGO_SLUG>/`

Se o caminho não for informado, use o arquivo Pygame indicado pelo usuário. Não presuma que o jogo é igual a um exemplo: leia o código completo e localize o ponto de entrada, o laço principal, a criação da janela, o tratamento de eventos, o carregamento de recursos, as dependências e a forma como o jogo termina.

## Objetivo

Criar uma versão funcional do jogo que possa ser instalada e executada em um celular Android, preservando as regras, o fluxo, o estilo visual, os sons, os recursos e a experiência principal do jogo original.

A solução preferencial deve continuar usando Pygame/Pygame-CE com SDL2 e ser empacotada com `python-for-android` através do Buildozer. Só troque de framework se a análise demonstrar que Pygame não atende a alguma exigência essencial; nesse caso, explique a decisão e preserve a jogabilidade.

## Processo obrigatório

1. Leia o arquivo original inteiro e todos os arquivos locais que ele importa ou utiliza.
2. Faça um diagnóstico curto contendo:
   - ponto de entrada e ciclo principal;
   - eventos de teclado, mouse, joystick e outros dispositivos;
   - dimensões e proporção da janela;
   - recursos externos e caminhos relativos;
   - módulos Python e pacotes necessários;
   - APIs incompatíveis ou frágeis no Android;
   - partes que podem consumir CPU, memória ou bateria em excesso.
3. Faça uma lista dos problemas concretos que precisam ser resolvidos para a execução em tela sensível ao toque.
4. Adapte o jogo com a menor mudança possível na lógica original. Não remova funcionalidades apenas para facilitar o empacotamento.
5. Execute verificações locais antes de concluir e corrija os erros encontrados.

## Requisitos da versão Android

### Código e arquitetura

- Criar um ponto de entrada claro para Android, sem executar o jogo durante um simples `import`.
- Manter a lógica do jogo separada da adaptação de plataforma quando isso for possível.
- Usar `pathlib` e caminhos baseados no diretório do projeto para localizar imagens, fontes, sons e outros recursos.
- Evitar caminhos absolutos, gravação em diretórios somente leitura e dependências que não funcionem no Android.
- Tratar corretamente a pausa, a retomada e a perda/recuperação de foco da aplicação.
- Limitar o uso de CPU quando a aplicação estiver pausada ou sem foco.
- Manter o código compatível com a versão de Python suportada pelo empacotador escolhido.
- Não inserir credenciais, chaves, telemetria ou permissões desnecessárias.

### Tela e escala

- Detectar o tamanho real da tela e adaptar a renderização à proporção do dispositivo.
- Preservar a proporção do jogo sem distorcer tabuleiros, personagens ou elementos interativos.
- Usar uma resolução lógica interna e uma transformação consistente para renderizar e converter coordenadas de toque.
- Garantir que textos, botões, menus e áreas clicáveis continuem legíveis e utilizáveis em telas pequenas.
- Suportar orientação de tela de forma explícita. Escolha retrato ou paisagem com base no jogo original e registre essa escolha na documentação.
- Não depender de um tamanho fixo de janela como `720x760` para que o jogo funcione.

### Controles por toque

- Converter toda interação essencial de mouse, teclado ou joystick em controles de toque.
- Fazer um toque simples cumprir a ação equivalente ao clique principal.
- Criar botões ou áreas de toque visíveis para ações que antes dependiam de teclas, sem cobrir informações importantes.
- Garantir áreas de toque confortáveis, com pelo menos aproximadamente 44 dp quando isso for compatível com o layout.
- Aceitar `FINGERDOWN`, `FINGERUP`, `FINGERMOTION` e os eventos de mouse sintetizados pelo SDL quando apropriado, evitando que uma mesma ação seja disparada duas vezes.
- Implementar uma forma de voltar, pausar e reiniciar o jogo que seja acessível no celular.
- Se o jogo usa arrastar, segurar, seleção de peça ou múltiplos toques, adaptar esse gesto explicitamente e documentá-lo.
- Manter teclado e mouse funcionando no desktop para facilitar os testes.

### Recursos

- Copiar para o projeto Android todos os recursos realmente usados pelo jogo.
- Corrigir referências relativas quebradas depois do empacotamento.
- Verificar fontes, imagens, sons, músicas e arquivos de configuração no APK.
- Não substituir recursos existentes por versões genéricas sem necessidade.

### Empacotamento

Criar no diretório de saída um projeto completo contendo, quando aplicável:

- arquivo principal Android, por exemplo `main.py` ou o nome exigido pelo projeto;
- `buildozer.spec` configurado para o jogo;
- `requirements.txt` ou a lista equivalente de dependências;
- diretório de recursos;
- ícone e arquivos de metadados somente se houver um recurso adequado disponível;
- `README-android.md` com os comandos de instalação, teste e compilação.

No `buildozer.spec`:

- informar o título e o pacote do aplicativo;
- declarar a versão e as dependências mínimas necessárias;
- incluir extensões e arquivos de dados usados pelo jogo;
- configurar a orientação escolhida;
- solicitar somente as permissões Android indispensáveis;
- configurar opções razoáveis para modo debug e release;
- não afirmar que uma compilação foi feita se ela não foi realmente executada.

## Validação obrigatória

Execute, na medida em que o ambiente permitir:

1. verificação de sintaxe, por exemplo `python -m py_compile`;
2. teste de importação sem iniciar indevidamente o jogo;
3. execução do jogo no desktop, se houver ambiente gráfico disponível;
4. inspeção do `buildozer.spec` e dos caminhos de recursos;
5. compilação de um APK debug com Buildozer, se Buildozer e Android SDK/NDK estiverem disponíveis.

Quando não for possível compilar ou testar no Android, informe exatamente o que faltou, sem inventar um resultado. Ainda assim, deixe o projeto preparado para que o usuário possa executar a compilação.

## Entregáveis

Crie ou atualize os arquivos diretamente no diretório de saída. Ao final, apresente:

1. resumo das alterações feitas;
2. lista dos arquivos criados ou modificados;
3. controles de toque e orientação da tela;
4. dependências e versões relevantes;
5. comandos exatos para testar no desktop;
6. comandos exatos para instalar o Buildozer e gerar o APK debug;
7. caminho esperado do APK gerado;
8. limitações, avisos e testes que não puderam ser executados.

Não entregue apenas uma explicação ou pseudocódigo: produza os arquivos funcionais. Preserve o código original, salvo quando a alteração for necessária para a versão Android, e explique qualquer mudança de comportamento.
