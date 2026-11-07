# CONTINUIDADE DO PROJETO — Resident Evil Code Veronica X

Última atualização: 2026-11-04

## Estado da reconstrução nesta conta

- Repositório de trabalho: https://github.com/joaovitoroutlok821-dot/recomp-codeveronica
- Conta: joaovitoroutlok821-dot
- Branch isolada: `android-rebuild`
- Branch original preservada: `main`
- Commit-base: `8da26ce9542c252ea24babafd3f3cf53dbf3eb75`
- Plano: [ANDROID_REBUILD_PLAN.md](ANDROID_REBUILD_PLAN.md)

A branch `android-rebuild` foi criada com sucesso a partir de `main`. Toda nova alteração de reconstrução deve ser feita nessa branch até que a versão seja validada. Não reescrever a branch principal.

## Objetivo

Construir uma versão Android ARM64 em APK da recompilação nativa de Resident Evil Code Veronica X com ReXGlue/ReXRuntime. Não é um emulador. O aplicativo deve abrir uma tela própria, permitir selecionar a pasta do jogo e iniciar a Activity SDL somente depois de preparar os arquivos no armazenamento privado.

## Ambiente do usuário

- Motorola Edge 30 Pro, Android 13, Snapdragon 8 Gen 1.
- O usuário trabalha somente pelo celular Android; não possui computador.
- Usa Termux, ADB e GitHub Actions.
- Não solicitar que reinstale o conector GitHub nem que repita etapas já concluídas.
- Ao receber “Ok”, continuar o trabalho sem pedir confirmação a cada etapa.
- Toda instrução local deve funcionar no Android/Termux.

## Arquivo do jogo — privacidade

O usuário já informou que o arquivo está no aparelho em:

`Download/Xbox360 Emulador/Jogos/RE Code Veronica X HD Dub PT-BR/Default.xex`

Dados técnicos já verificados em conversa anterior: arquivo XEX2, 13.774.848 bytes, módulo interno `Bio_cv.exe`, Title ID `43430822`, Media ID `58A6EFFB`.

**Não solicitar reenvio sem necessidade. Não commitar o XEX, seu hash, arquivos do jogo, chaves ou conteúdo protegido. Não incluir o XEX no APK nem em artefatos públicos.** O repositório é público; não usar `game/Default.xex` como arquivo versionado.

## Estado técnico herdado

- O codegen do título e build Linux x86-64 foram concluídos anteriormente: 214 unidades C++ geradas e executável host `recvx` ligado.
- Um probe anterior compilou o SDK ReXGlue para Android ARM64, incluindo runtime e backend Xenos. Isso não demonstra que o alvo específico do jogo foi ligado para Android nem que um APK existe.
- O `build.sh` existente é orientado a host Linux. Não tratá-lo como builder Android.
- A geração de código deve executar com o CLI ReXGlue Linux x86-64 no runner; as fontes do jogo devem ser compiladas separadamente com NDK para `arm64-v8a`.
- O SDL Java e a biblioteca nativa devem vir do mesmo commit SDL fixado pelo SDK para evitar incompatibilidades JNI/versão.
- Já existe `scripts/install-android-game-setup.py`, que instala Activities de seleção de pasta e cópia SAF. A implementação ainda precisa de revisão e validação; não presumir que está pronta.
- O seletor deve copiar a pasta escolhida para armazenamento privado do app, verificar `Default.xex` e só então abrir SDL. Deve tratar espaço insuficiente, progresso, cancelamento, falhas de I/O e recuperação de cópia anterior.
- A logo padrão do SDL não deve ser usada como ícone final do launcher; a identidade visual do jogo deve ser aplicada quando a arte adequada estiver disponível no projeto.

## Progresso na branch android-rebuild — 2026-11-04

- Criado `ANDROID_REBUILD_PLAN.md`.
- Atualizado `scripts/install-android-game-setup.py`: pré-estimativa recursiva de espaço quando o provedor fornece tamanhos, margem preventiva de 128 MiB, reserva dinâmica de 32 MiB durante a cópia, progresso e remoção da pasta temporária se a cópia falhar.
- O seletor agora exige `Default.xex` na raiz da pasta selecionada, em vez de aceitar qualquer arquivo `.xex`.
- Criado `android-smoke/SmokeTest.c` para validar SDL3, criação de janela, renderer e ciclo de eventos sem depender do XEX.
- Criado `.github/workflows/android-smoke-test.yml`, usando o mesmo commit SDL fixado pelo SDK, NDK 27.2.12479018 e ABI arm64-v8a. O workflow valida as bibliotecas nativas, package ID, alinhamento, assinatura e ausência de imagens de jogo.
- O workflow força SDL compartilhada para garantir a inclusão de `libSDL3.so`.
- Última branch head conhecida antes desta atualização documental: `6624918613acbe4dd1e56919913b4cc07a8799ff`.
- `main` permanece no commit-base `8da26ce9542c252ea24babafd3f3cf53dbf3eb75`.
- A API de Actions ainda retornou zero execuções; não há APK nem resultado de compilação confirmado.

## Plano de execução

1. Auditoria da branch `android-rebuild`, scripts Android, SDL e targets exportados pelo SDK.
2. Corrigir e testar o helper SAF.
3. Criar workflow de APK mínimo SDL/JNI sem XEX; validar Activity, Manifest, bibliotecas e ABI.
4. Integrar o alvo recompilado do jogo: codegen host + compilação NDK ARM64 + link com runtime/Xenos Android.
5. Empacotar APK, inspecionar dependências e confirmar ausência do XEX.
6. Testar no Motorola Edge 30 Pro via APK e logs; depurar superfície gráfica/Vulkan, áudio, controles e execução do jogo em separado.

## Regras de continuidade

- Registrar commits, workflows, artefatos e testes com evidências.
- Não declarar APK funcional sem artifact APK confirmado e validação real no aparelho.
- Sucesso do SDK ou do codegen não equivale a jogo funcionando.
- Não alterar o manifesto nem remover correções de limites de funções sem análise.
- Não misturar binários Linux host com bibliotecas Android.
- Preservar `main`; usar `android-rebuild` para a reconstrução.


## Critério de próximo avanço

Não integrar o XEX nem o codegen do título ao workflow até que o APK SDL/JNI mínimo seja compilado e validado. A primeira execução do workflow precisa ser verificada; se o push pelo conector não iniciar Actions, habilitar/iniciar o workflow pela aba Actions do GitHub antes de considerar a fase concluída.


## Privacidade e integridade — 2026-11-04

- Removida a impressão e a constante de hash SHA-256 do script `scripts/inspect-xex.py`; a inspeção local agora exibe somente metadados e strings de identificação.
- Removida a referência ao hash da documentação `README.md` e `STATUS.md` nesta branch.
- Nenhum XEX foi enviado ao repositório ou ao workflow de diagnóstico SDL/JNI.
- Último commit de README/script/status/continuidade será refletido pelo HEAD atual da branch; `main` permanece intacta.


## Resultado do primeiro APK SDL/JNI — 2026-11-04

- Workflow [#41768874041](https://github.com/joaovitoroutlok821-dot/recomp-codeveronica/actions/runs/41768874041) concluído com sucesso na branch `android-rebuild`.
- Artefato: `recvx-android-sdl-jni-smoke`, artifact ID `13293936559`.
- APK debug compilado: package `com.rexglue.recvx.smoketest`, ABI `arm64-v8a`, minSdk 21 e targetSdk 35.
- APK contém `libmain.so` e `libSDL3.so`; inspeção ELF confirmou 64-bit AArch64, NDK r27c (27.2.12479018), e `libmain.so` declara `libSDL3.so` como dependência.
- Verificações de package ID, assinatura debug, zipalign e ausência de XEX/ISO/XISO/WUD/WAD passaram.
- Este APK só prova o caminho SDL/Java/JNI e criação de janela/renderer no build. Não contém o runtime ReXGlue, fontes recompiladas do título ou dados do jogo; não é o APK final.
- Próxima etapa: instalar no Motorola Edge 30 Pro e confirmar que a tela SDL colorida permanece aberta. Só depois avançar para SAF e runtime.

### Workflow legado de codegen

- O workflow antigo falhou na etapa de baixar o release `recvx-xex-private` porque esse release não existe nesta nova conta/repositório (`release not found`). O codegen nem chegou a começar.
- O arquivo de workflow foi removido apenas da branch `android-rebuild` para evitar tentativas automáticas inúteis e impedir que se tente colocar um XEX privado em release de um repositório público.
- `main` foi preservada.


## Atualização de continuidade — 2026-11-04 (estado verificado)

### APK SDL/JNI + SAF

- Workflow [#41770101231](https://github.com/joaovitoroutlok821-dot/recomp-codeveronica/actions/runs/41770101231) terminou com sucesso na branch `android-rebuild` (commit `146220eb1ed24bd3201da722f0a8f1aeb994677f`).
- Artefato `recvx-android-sdl-saf-test`, ID `13294387823`.
- APK debug compilado e verificado: SDL3/JNI ARM64, package `com.rexglue.recvx.smoketest`, Activities SAF e SDL, assinatura e alinhamento válidos, sem XEX embutido.
- O usuário confirmou em teste físico que o APK SDL anterior abre e exibe a tela de cores sem fechar.
- A versão SAF ainda precisa ser instalada e testada no telefone. O botão de ação é rotulado como teste SDL e não inicia o jogo.

### Auditoria do codegen

- A árvore Git da branch não contém `generated/default/`; essa pasta está no `.gitignore`. Logo, as 214 unidades C++ citadas no histórico não estão atualmente disponíveis nesta branch para auditoria ou compilação Android.
- O executável Linux `recvx` foi ligado em experimento anterior, mas isso não equivale a código gerado persistido nem a um alvo Android.
- Workflow de diagnóstico [#41768927121](https://github.com/joaovitoroutlok821-dot/recomp-codeveronica/actions/runs/41768927121) falhou na etapa de download do release `recvx-xex-private` (release inexistente); o codegen não chegou a executar.
- O manifesto contém entradas manuais e correção de switch table; não ampliar esses endereços sem evidência do XEX e dos logs de codegen.
- Removida a validação por hash fixo de `scripts/common.sh`. Agora verifica o cabeçalho XEX2, tamanho mínimo e string interna `Bio_cv.exe`, sem imprimir hash. Isso não é autenticação criptográfica da versão do jogo.

### Próxima sequência correta

1. Testar no Motorola Edge 30 Pro o APK SAF do artefato #41770101231: selecionar a pasta do jogo e confirmar a cópia para armazenamento privado; o botão abre apenas a tela de teste SDL.
2. Resolver um caminho privado e seguro para disponibilizar o XEX ao codegen no runner, ou preparar execução local do CLI em ambiente compatível. Não usar release público, não versionar o XEX e não solicitar hash.
3. Regenerar as fontes com a versão ReXGlue fixada; guardar relatórios/manifestos e métricas de geração em artefato sem o XEX.
4. Auditar quantidade de funções/unidades, lacunas, imports/stubs, limites manuais e switches antes da compilação NDK.
5. Compilar o alvo específico `recvx` para `arm64-v8a`, ligá-lo ao runtime/Xenos Android e só então empacotar o APK de jogo.

As instruções anteriores deste arquivo que diziam que não havia APK ou que o primeiro smoke test ainda precisava ser executado foram superadas pelos resultados acima. O APK SAF está construído, mas o jogo recompilado ainda não está pronto.


## Auditoria Android/ReXGlue — continuação 2026-11-04

### Entrada da aplicação e modelo Android

- Revisados `src/main.cpp`, `src/recvx_app.h`, `CMakeLists.txt`, `generated/rexglue.cmake`, `CMakePresets.json` e o SDK fixado em `398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb`.
- `src/main.cpp` usa `REX_DEFINE_APP(recvx, RecvXApp::Create)`; não contém lógica SDL/Android própria.
- `include/rex/ui/windowed_app.h` do SDK define `XE_UI_WINDOWED_APPS_IN_LIBRARY=1` quando `REX_PLATFORM_ANDROID` está ativo. Nesse modo, `REX_DEFINE_APP` registra a aplicação em uma biblioteca em vez de exportar o criador de um executável.
- O ponto de entrada SDL atual do SDK (`src/ui/windowed_app_main_sdl.cpp`) implementa `main()` para plataformas não-Windows. O arquivo não contém uma implementação Android `SDL_main`/ponte JNI específica. Portanto, não é correto compilar o `main.cpp` atual como se fosse um executável Android.
- O SDK fixado não reconhece Android no seletor de plataforma de seu `CMakeLists.txt`: no estado original aceita Windows, Linux e macOS e termina com erro para outras plataformas. A configuração Android precisa da camada de compatibilidade, incluindo definição `REX_PLATFORM_ANDROID` e superfície SDL/Vulkan Android.
- O repositório já contém `scripts/ensure-rexglue-android-platform.py`, uma adaptação idempotente que injeta o alvo `android-arm64`, seleciona `surface_android.cpp`, evita dependências desktop via pkg-config e liga a superfície nativa Android à janela SDL. O script deve ser executado e validado no SDK clonado; sua existência isolada não prova que a compilação completa funciona.
- `generated/rexglue.cmake` cria um executável do projeto, liga `rex::runtime` e inclui fontes geradas em uma object library. Para Android será necessário um target `SHARED` e uma entrada SDL/Android coerente com o registro da aplicação; não modificar o target atual até provar o fluxo correto.

### Próximas verificações obrigatórias

1. Inspecionar o CMake completo do SDK e como `rexui`, `rex::runtime`, SDL3 e o target de plataforma são exportados/ligados.
2. Confirmar o contrato SDL Android usado pelo projeto SDL 3.5.0 fixado: símbolo de entrada, `SDLActivity`, carregamento de `libmain.so` e lifecycle JNI.
3. Implementar uma entrada Android mínima que obtenha o criador registrado para `recvx`, inicialize o contexto SDL/ReXGlue e respeite pause/resume/destroy do Android. Não presumir que chamar `main()` ou somente exportar `SDL_main` seja suficiente.
4. Adaptar CMake do projeto para biblioteca compartilhada Android, incluindo fontes recompiladas e runtime; compilar no workflow sem XEX embutido no APK.
5. Só depois integrar SAF para definir o caminho privado do jogo e iniciar runtime real.

### Evidência e limites desta auditoria

- A auditoria foi somente leitura; nenhum código-fonte de runtime, CMake ou APK foi alterado nesta etapa.
- O smoke APK SDL/SAF existente continua sendo apenas um teste de preparação e SDL; não executa ReXGlue nem Resident Evil.
- A compilação Android do SDK já validada em probe anterior continua sendo evidência de SDK ARM64, mas não valida o entrypoint Android da aplicação do título.


### Confirmação do registro e entrada SDL Android — 2026-11-04

- Inspecionado `include/rex/ui/windowed_app.h`: Android define `XE_UI_WINDOWED_APPS_IN_LIBRARY=1`; `REX_DEFINE_APP(recvx, RecvXApp::Create)` registra o creator sob a chave textual `recvx`.
- Inspecionado `src/ui/windowed_app.cpp`: `WindowedApp::creators_` é definido como ponteiro estático zerado; `WindowedApp::GetCreator("recvx")` recupera o creator depois do carregamento da biblioteca. Isso confirma o mecanismo de seleção da aplicação, mas não fornece por si só uma função exportada para iniciar a aplicação.
- SDL 3.5.0 no commit fixado `8bf3b7215ad9fc3deb583c6a3a37c6c67f2e24e4` usa `SDLActivity.getMainFunction() == "SDL_main"`; a atividade chama `nativeRunMain(library, function, arguments)` em thread SDL dedicada. O pacote Android SDL carrega `libSDL3.so` e `libmain.so`. Logo a biblioteca do jogo precisa expor o símbolo SDL_main compatível com o ABI C esperado por SDL, e o entrypoint deve obter `WindowedApp::GetCreator("recvx")`.
- A amostra `Android.mk` do SDL confirma o módulo nativo `main` como shared library e SDL3 como dependência compartilhada. O projeto atual usa Gradle/CMake, mas o contrato JNI/SDL é o mesmo; não copiar cegamente o Android.mk legado.
- O helper `scripts/ensure-rexglue-android-platform.py` cria uma superfície Android usando `ANativeWindow` e propriedades SDL. Revisar antes de executar: seu header novo usa `ANativeWindow*` sem incluir explicitamente `<android/native_window.h>`; também é necessário conferir se a classe Surface e o enum `kTypeIndex_AndroidNativeWindow` existem exatamente como assumido. Não tratar o sanity check textual do script como validação de compilação.
- Correção de interpretação da auditoria anterior: `include/rex/platform.h` já define `REX_PLATFORM_ANDROID` automaticamente para `__ANDROID__` (e também `REX_PLATFORM_LINUX`). A lacuna está no CMake do SDK, que seleciona UNIX/Linux antes de tratar Android, não na ausência da macro no cabeçalho.

### Plano técnico revisado

1. Confirmar definições de Surface/SurfaceType e os requisitos de ownership/refcount de ANativeWindow.
2. Adaptar CMake SDK com Android branch antes de UNIX, surface Android e dependências Android NDK; validar configuração e compilação do SDK completo, não apenas do probe.
3. Implementar `SDL_main` em uma fonte Android separada: inicializar logging/cvars sem argv desktop, criar SDLWindowedAppContext, obter creator via `WindowedApp::GetCreator("recvx")`, chamar OnInitialize, executar o loop e sempre invocar InvokeOnDestroy em encerramento/erro conforme contrato. Confirmar a ordem de SDL_Init/SDL_InitSubSystem e o lifecycle SDL Android para evitar inicialização dupla ou bloqueio no pause.
4. Construir `libmain.so` ARM64 com runtime, UI, fontes geradas e entrypoint; garantir que símbolos de registro não sejam removidos pelo linker e que todas as dependências SDL/ReXGlue estejam no APK.
5. Integrar SAF ao caminho `game:\\Default.xex` por PathConfig/URI ou staging privado interno, sem copiar XEX para APK e sem persistir conteúdo em repo público.

Nenhum código de runtime ou APK foi alterado nesta etapa; somente este registro de continuidade foi ampliado.


## Análise do APK Black Android e revisão Vulkan — 2026-11-04

### Referência externa analisada

- APK fornecido pelo usuário: `Black.apk.zip`; análise estrutural confirmou bibliotecas ARM64 `libmain.so`, `libSDL3.so` e `libc++_shared.so`.
- Projeto de referência: `RanggaCasper/Black-Android`. A arquitetura usa Activity derivada de `SDLActivity`, `getLibraries() = {"SDL3", "main"}`, SDL3 e uma biblioteca principal própria.
- O `native/main.cpp` do Black inicializa SDL, cria janela Vulkan, prepara arquivos e executa o runtime. Seu fluxo de jogo é específico do XboxXBE-Recomp e NÃO pode ser copiado diretamente para ReXGlue.
- O CMake do Black constrói `main` como biblioteca compartilhada incluindo runtime, código do jogo e host Android. O APK não depende de um executável Android separado.
- O Black usa SDL 3.4.16 e NDK 28.2; o nosso SDK fixa outra versão SDL (3.5.0 no estado atual). Não misturar classes Java SDL nem bibliotecas de versões diferentes.

### Correção importante após leitura do SDK ReXGlue fixado

- No commit SDK `398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb`, `Surface::TypeIndex` já contém `kTypeIndex_AndroidNativeWindow` e `kTypeFlag_AndroidNativeWindow`.
- `src/ui/vulkan/vulkan_instance.cpp` já habilita `VK_KHR_android_surface` quando `VK_USE_PLATFORM_ANDROID_KHR` está definido.
- `src/ui/vulkan/vulkan_presenter.cpp` já contém o caminho Android que chama `vkCreateAndroidSurfaceKHR` com o `ANativeWindow*` fornecido por `AndroidNativeWindowSurface`.
- Portanto, o helper `scripts/ensure-rexglue-android-platform.py` não deve duplicar nem reimplementar a parte Vulkan do presenter. Seu papel é habilitar plataforma Android no CMake, selecionar a superfície Android, evitar dependências desktop X11/Wayland e permitir que `window_sdl.cpp` obtenha a janela nativa SDL.
- A superfície proposta guarda ponteiro emprestado de `ANativeWindow` obtido das propriedades SDL; o tempo de vida deve ficar limitado ao SDL_Window e não deve liberar a referência emprestada.
- A revisão identificou também que `WindowSDL::OpenImpl()` cria a janela com flags `RESIZABLE | HIGH_PIXEL_DENSITY | HIDDEN`; ainda falta confirmar/implementar o requisito de janela Vulkan no Android. O Black cria a janela explicitamente com `SDL_WINDOW_VULKAN`. Antes de aplicar essa flag ao ReXGlue, verificar o comportamento de `SDL_WINDOW_VULKAN` no commit SDL fixado e se a abstração atual não a adiciona em outro ponto.

### Entrada Android: decisões de arquitetura

- `REX_DEFINE_APP(recvx, RecvXApp::Create)` registra o creator "recvx" em modo Android-library; `WindowedApp::GetCreator("recvx")` é a API prevista para recuperar a aplicação.
- `SDLWindowedAppContext::Initialize()` inicializa `SDL_INIT_VIDEO` e registra eventos; seu loop `RunMainMessageLoop()` espera eventos e despacha janelas, quit e tarefas da UI. O contexto faz `SDL_QuitSubSystem(SDL_INIT_VIDEO)` no destrutor.
- O entrypoint desktop `windowed_app_main_sdl.cpp` não pode ser reutilizado como Android: contém `main()` e chama `cvar::Init(argc, argv)`, fluxo que não representa o ciclo de vida SDLActivity.
- O host Android deve ser um arquivo separado exportando `SDL_main`, preparar logging/cvars sem pressupor argumentos desktop, criar e inicializar `SDLWindowedAppContext`, recuperar creator "recvx", chamar `OnInitialize()`, executar `RunMainMessageLoop()` e sempre chamar `InvokeOnDestroy()` depois de inicialização (inclusive falha parcial), respeitando o contrato da classe.
- Não foi ainda feita alteração de código Android nem novo build nesta etapa. O adaptador anterior permanece apenas uma proposta e precisa de validação de SDL init order, janela Vulkan, pause/resume e encerramento.

### Próximas verificações obrigatórias

1. Inspecionar a versão SDL exata fixada pelo SDK para confirmar flags Vulkan, `SDL_main`, carregamento de `libmain.so` e callbacks Android.
2. Corrigir o helper Android para adicionar superfície/seleção CMake sem duplicar o suporte Vulkan que o SDK já possui.
3. Confirmar `VK_USE_PLATFORM_ANDROID_KHR`, headers NDK e ligação de `android`/Vulkan no target SDK.
4. Criar entrypoint `SDL_main` em fonte separada e integrar SAF com `game:\\Default.xex` via armazenamento privado, sem embutir XEX.
5. Executar build ARM64 do SDK e do target específico em workflow isolado antes de gerar APK.

O APK Black é referência arquitetural, não prova de compatibilidade binária nem de funcionamento do nosso jogo.


## Validacao da correcao SDL/Vulkan Android — 2026-11-04

- O commit `80f0fe325dcc915aa6dde015a021bd8d2bf09ffb` atualizou `scripts/ensure-rexglue-android-platform.py` para solicitar `SDL_WINDOW_VULKAN` em janelas Android.
- O push acionou o workflow **Android ARM64 platform probe** #41842550526, que terminou com sucesso. Etapas confirmadas: checkout do SDK fixado, aplicacao dos patches, configuracao CMake com selecao Android real, validacao de `REX_PLATFORM_ANDROID`, e compilacao do SDK para `arm64-v8a`.
- Job ID `126617622126`; artefato de logs `recvx-android-arm64-probe`, ID `13330153452`.
- Isso valida a compilacao do SDK ReXGlue Android ARM64 com o helper atualizado. Ainda nao valida o novo entrypoint SDL_main, o alvo recompilado do jogo, APK final ou execucao do jogo no aparelho.
- Proximo passo: implementar e compilar o entrypoint Android SDL_main e conectar o ciclo de vida da WindowedApp `recvx`; manter o XEX e fontes geradas do titulo fora do repositorio publico.


## Integração do ponto de entrada e target Android — 2026-11-04

- Revisado o SDK fixado em `398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb`: `cvar::Init(argc, argv)` retorna os argumentos posicionais; o inicializador oficial os associa a `WindowedApp::GetPositionalOptions()` e chama `SetParsedArguments()`.
- Corrigido `src/android_main.cpp` para reproduzir esse mapeamento antes de `OnInitialize()`, mantendo o registro Android por `WindowedApp::GetCreator("recvx")`, o loop SDL e a destruição da aplicação.
- Commit: `eddc4238f36d7ecfb3419c1ed466429f02901b95` — `fix(android): forward positional arguments to ReXGlue app`.
- Atualizado o `CMakeLists.txt`: em Android, cria uma biblioteca compartilhada incluindo `src/android_main.cpp` e define o nome de saída como `main`, que é o nome esperado pelo `SDLActivity`; desktop mantém o executável `recvx`.
- Commit: `cb17959247926e5d453ed25431c7c9bcef2cec39` — `build(android): add SDLActivity shared library target`.
- O SDK confirma a assinatura do creator, `GetCreator`, `OnInitialize`, `InvokeOnDestroy` e `RunMainMessageLoop`. A implementação foi alinhada com a passagem de argumentos do inicializador oficial.
- **Ainda não compilado:** não há nesta branch a pasta `generated/default/` com `recvx_init.h` e as unidades C++ do jogo. A integração CMake/entrypoint ainda precisa de um build Android privado que obtenha o XEX e regenere o código no runner, sem publicar XEX ou fontes geradas.
- O workflow de probe SDK compila o SDK isoladamente e não valida este target de jogo. O APK SDL/SAF existente também não contém este entrypoint ReXGlue. Portanto, ainda não há APK do jogo nem validação de execução do Resident Evil.
- Próxima etapa técnica: preparar workflow privado para codegen + compilação do target `recvx` Android ARM64, transferindo somente artefatos não sensíveis e mantendo XEX/fontes geradas em ambiente privado.


## Correção do adaptador CMake Android — 2026-11-04

- Corrigido o adaptador `scripts/ensure-rexglue-android-cmake.py`: as âncoras do `generated/rexglue.cmake` agora usam quebras de linha reais em vez de procurar a sequência literal `\\n`.
- O adaptador passou a aceitar o prefixo de instalação do SDK e a localizar/ajustar os arquivos instalados `rexglue_helpers.cmake`. Isso é necessário porque `find_package(rexglue)` usa a cópia instalada, não apenas o helper na árvore de fontes.
- `build.sh` agora passa `SDK_PREFIX` como terceiro argumento depois de instalar o SDK e gerar o código.
- Commits: `858e8ebb395a9e91a58ef1795a6cdfbeaa5a8d13` (adaptador) e `6741c48686411ec282fad7ffdfdd884f8f64ff82` (`build.sh`).
- Revisão do conteúdo no GitHub confirmou que os padrões de newline foram corrigidos e que o argumento `SDK_PREFIX` está sendo passado.
- **Ainda não validado por execução:** não há resultado de workflow após esses commits. O script precisa ser executado no runner com o SDK instalado e o scaffold gerado para confirmar que todos os anchors correspondem ao conteúdo real.
- Próxima barreira independente: resolver o target único `libmain.so` entre o CMake do SDL Android e o target do jogo, e adaptar o carregamento do plugin Xenos para Android. Nenhum APK final foi produzido nesta etapa.


### Correção preparada para carregamento do plugin Xenos no Android — 2026-11-04

- Commit: `98d8b207f44abab9948f5ece5f81bf2789912f71`.
- Atualizado `scripts/ensure-rexglue-android-platform.py` para adaptar `src/system/gpu_plugin_loader.cpp` do SDK fixado.
- Em Android, o carregador passa a chamar `dlopen` pelo nome `librexgpu-xenos.so`, usando o linker namespace do aplicativo, em vez de procurar o plugin junto ao caminho do executável `app_process64`.
- Em Linux/macOS/Windows, a lógica original de localização ao lado do executável é preservada.
- Esta é uma alteração no script de compatibilidade; ainda não foi executada numa compilação Android completa. É necessário confirmar que o plugin Xenos é efetivamente produzido, copiado para `app/src/main/jniLibs/arm64-v8a/` e carregado no aparelho.
- O alvo SDL `main` ainda precisa receber as fontes `src/main.cpp`, `src/android_main.cpp`, as unidades recompiladas e a configuração `rexglue_setup_target(main GPU_PLUGINS xenos)`. Nenhum APK de jogo foi produzido por este commit.


### Integração CMake com o alvo SDL main — 2026-11-05

- Commit `bd395b2f2724883c7e1691fd54e0809d734cc79a`: a raiz do projeto agora reconhece o alvo `main` já criado pelo SDL Android e anexa `src/main.cpp`, `src/android_main.cpp` e `rexglue_setup_target(main GPU_PLUGINS xenos)` a ele. O modo Android independente e os builds desktop continuam com seus próprios alvos.
- Commit `2892f92622f044b4bb980abbd59dca56de3c9d6f`: corrigida a estrutura condicional do CMake após revisão do arquivo; cada caminho configura seu alvo uma única vez.
- Commit `66db71470cf3d3fe4277757b349d9cc60f1b1697`: criado `scripts/attach-recvx-to-sdl.py`. Ele adapta o CMake do projeto Android SDL 3.5.0 fixado, remove `YourSourceHere.c` do alvo `main` e adiciona o diretório do projeto ReXGlue como subdiretório, validando o alvo existente.
- O script ainda não foi executado num workflow Android real. A configuração precisa passar `-DRECVX_SOURCE_ROOT=<checkout privado do projeto>`, instalar/encontrar o SDK ReXGlue e disponibilizar `generated/default/sources.cmake` do artefato privado.
- O carregador Xenos adaptado no commit `98d8b207f44abab9948f5ece5f81bf2789912f71` ainda precisa ser exercitado e o plugin deve ser copiado para `app/src/main/jniLibs/arm64-v8a`.
- Nenhuma alteração foi feita na branch `main`; nenhum XEX foi colocado no repositório público; nenhum APK de jogo foi produzido.

## Workflow privado de APK Android — 2026-11-05

- Criado no repositório privado `joaovitoroutlok821-dot/recvx-private-build`, branch `main`, o workflow `.github/workflows/private-android-apk.yml`.
- Commit privado: `626e01493f34aebbfaf1dd0a6b04870f6e7a915d` (última correção dos argumentos CMake).
- O workflow valida o XEX no checkout privado, gera as fontes no runner efêmero, prepara SDL 3.5.0, aplica os patches Android do ReXGlue e tenta montar o APK ARM64.
- O CMake do Gradle recebe explicitamente `RECVX_SOURCE_ROOT` e `REXSDK_DIR`, além das opções Vulkan/Android.
- A validação exige `libmain.so`, `libSDL3.so`, `librexruntime.so` e `librexgpu-xenos.so` no APK e verifica alinhamento/assinatura.
- O artefato e relatórios são publicados somente no workflow do repositório privado; o XEX e as fontes geradas são removidos no final.
- **Estado:** workflow criado, mas ainda não executado. Não há APK Android do jogo confirmado. A execução manual em GitHub Actions ainda é necessária; depois será preciso analisar o resultado e corrigir os erros reais de compilação/linkagem.


## Correção do primeiro build privado completo — 2026-11-05

- Inspecionada a execução privada #6, run ID `42077632509`, no repositório `joaovitoroutlok821-dot/recvx-private-build`.
- A validação do XEX, checkout do código, geração privada das fontes, instalação Android/NDK, patches do SDK, preparação SDL e compilação de grande parte das bibliotecas passaram.
- A etapa que falhou foi o link de `librexruntimed.so`, com erros explícitos do linker NDK: `unable to find library -lpthread` e `unable to find library -lrt`.
- Causa confirmada no SDK ReXGlue fixado: `src/core/CMakeLists.txt` adicionava `pthread rt dl` para todo `UNIX`, condição que também é verdadeira no Android. Android/Bionic não fornece bibliotecas separadas `libpthread` e `librt`; pthread já faz parte de libc.
- Criado `scripts/ensure-rexglue-android-link-libs.py` na branch `android-rebuild`, commit `5b0b583951be4ceb5b62e9c091c5b14a2322a195`. O patch preserva pthread no macOS, usa somente `dl` no Android e mantém `pthread rt dl` no Linux.
- Atualizado o workflow privado para executar o patch após o patch de plataforma, commit `5b904c176ed6147ea4f10bb747ba0e280bde80a0`.
- O run #6 foi encerrado com falha antes de empacotar/validar o APK; não houve APK final. O artefato de diagnóstico pode conter apenas relatórios parciais.
- Próxima ação: iniciar novamente o workflow privado #7 pelo botão **Run workflow**, mantendo `source_ref=android-rebuild`. Verificar se o link de `librexruntimed.so` passa; depois investigar qualquer próximo erro real de linkagem/compilação.
- Nenhum XEX foi adicionado ao repositório público; o workflow continua removendo XEX, fontes geradas e checkout SDK do runner ao final.


## Resultado do workflow privado #7 e correção seguinte — 2026-11-05

- Workflow privado #7, run ID `42092445762`, terminou com falha na etapa de compilação Android ARM64.
- A correção anterior foi confirmada: não reapareceram os erros de link `-lpthread` e `-lrt`.
- Passaram validação XEX, checkout, geração privada de fontes, instalação SDK/NDK/CMake, patches de plataforma, checkout SDL 3.5.0 e preparação do pacote Android.
- A falha real foi `/bin/sh: .../.deps/rexglue-sdk/out/android-arm64/rexglued: Exec format error`. O CMake Android tentou executar o CLI ReXGlue compilado para Android ARM64 como ferramenta host Linux.
- A compilação parou durante a etapa 14; a verificação do APK foi ignorada. O artefato foi tentado, mas não há APK validado.
- O script existente `scripts/ensure-rexglue-android-cmake.py` contém o mecanismo para definir `REXGLUE_SKIP_CODEGEN=ON` no Android e usar as fontes geradas pelo job host. A etapa de compatibilidade Android do workflow privado não o reaplicava explicitamente depois do codegen privado.
- Atualizado o workflow privado para executar `python3 scripts/ensure-rexglue-android-cmake.py "$SDK" "$PWD"` após os patches de SDK, reforçando a guarda CMake antes da configuração Android.
- Commit privado: `9d65e4691fb3a2d8dfe5743f63750779bdaa8ab8`.
- Próximo passo: executar workflow privado #8 com `source_ref=android-rebuild` e confirmar que não tenta executar `rexglued` Android no runner. Depois investigar a próxima falha real, se houver.
- Nenhum XEX ou fonte gerada do título foi adicionado ao repositório público.


## Build privado Android #10 — diagnóstico e correção #11 (2026-11-05)

- Build #10: https://github.com/joaovitoroutlok821-dot/recvx-private-build/actions/runs/42123035684
- O compilador confirmou C++23 (`-std=gnu++23`), portanto a correção anterior resolveu a falha de headers da biblioteca padrão.
- A compilação avançou até aproximadamente 779/999 tarefas e falhou ao compilar `rex_app.cpp`, incluído diretamente no target SDL `main`: `fatal error: 'imgui.h' file not found`.
- A auditoria do SDK fixado `398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb` confirmou que `rexui` é um object library, publica `imgui::imgui` e propaga o diretório de headers do ImGui. O target SDL `main` só estava ligado a `rex::runtime`, não a `rex::ui`.
- Correção aplicada em `CMakeLists.txt`: ligar explicitamente `main` a `rex::ui` após `rexglue_setup_target`. Isso propaga os include directories do ImGui e inclui a implementação UI do SDK no `libmain.so`. O mesmo vínculo foi adicionado aos modos Android standalone e host para manter a configuração consistente.
- Commit público da correção: `3e5eb9e12d98fafb71d47863ec760154e9849235`.
- Próximo passo: executar build privado #11 e verificar se a compilação passa da unidade `rex_app.cpp`; ainda não existe APK final validado.



## Atualização de continuidade — correção de armazenamento Android e build privado #21 — 2026-11-07

### Diagnóstico do APK #20

- O APK do workflow privado #20 foi compilado com sucesso e incluiu as bibliotecas ARM64 esperadas, inclusive `librexgpu-xenosd.so`.
- O usuário testou o APK #20; ao iniciar, a aplicação fechou e retornou ao launcher.
- O log enviado pelo usuário (`recvx20-falha.txt`) identificou a falha fatal:
  `filesystem error: in create_directories: Permission denied ["/data/.local"]`.
- O backtrace passa por `std::filesystem::__create_directories` dentro de `librexruntimed.so` e pelo plugin `librexgpu-xenosd.so`. Isso confirma que o plugin Xenos foi carregado e executou; a falha imediata é a tentativa de criar dados em `/data/.local`, local sem permissão para o aplicativo Android.
- A falha não deve ser confundida com a antiga ausência do plugin GPU nem com um erro de compilação.

### Correção aplicada na branch pública android-rebuild

- Commit `bfad73025588b04c87ab42ac62de650beafd585d`: primeira implementação de redirecionamento de dados Android para armazenamento externo específico do aplicativo.
- Commit mais recente `38f62c55a099f54fc8302293366c9f602f98901f` — `fix(android): redirect HOME and XDG paths to app storage`.
- Em `src/android_main.cpp`, a configuração Android obtém `getExternalFilesDir(null)` da Activity SDL; se indisponível, usa `SDL_GetPrefPath("ReXGlue", "recvx")`.
- Cria diretórios separados para home, dados, configuração, cache e estado sob a raiz `rexglue`, e define `HOME`, `XDG_DATA_HOME`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME` e `XDG_STATE_HOME` antes de iniciar o runtime.
- O destino primário esperado é a pasta externa específica do app, em `Android/data/com.rexglue.recvx.privateapp/files/rexglue/`; não é necessário root. A pasta do jogo/XEX permanece independente e não é incorporada ao APK.
- A alteração foi enviada ao GitHub, mas ainda precisa ser compilada e validada em aparelho. Não declarar que o problema de armazenamento está resolvido até testar o novo APK.

### Workflow privado #21

- Repositório: `joaovitoroutlok821-dot/recvx-private-build`.
- Para iniciar o workflow sem depender da ação manual `workflow_dispatch), foi usado o gatilho `push` já existente no workflow, que observa `.github/build-requests/**`.
- Criado `.github/build-requests/recvx-storage-fix-38f62c5.txt` no repositório privado.
- Commit do pedido de build: `4b6c2878f984357ddf9586ae80487f570c91df0f`.
- Execução confirmada pela API do GitHub: workflow run **#21**, ID `42417490244`, evento `push`, commit `4b6c2878f984357ddf9586ae80487f570c91df0f`.
- URL: https://github.com/joaovitoroutlok821-dot/recvx-private-build/actions/runs/42417490244
- Na última consulta, estado `queued`; ainda não havia resultado final.
- O pedido informa ao workflow que deve usar `source_ref=android-rebuild`, incluindo a correção de armazenamento do commit `38f62c5`.

### Próxima etapa

1. Acompanhar a execução #21 até terminar; confirmar o ref/commit de origem realmente usado e verificar logs de configuração Android, compilação, validação e artefatos.
2. Se o build falhar, corrigir a causa concreta dos logs antes de iniciar outra execução.
3. Se o APK for produzido, verificar as bibliotecas e disponibilizar o artefato; o usuário deve testar e enviar logcat novo se ainda fechar.
4. No próximo log, confirmar que não aparece mais tentativa de criar `/data/.local`; verificar também o caminho `HOME`/XDG registrado no início do runtime.
5. Atualizar este arquivo `CONTINUATION.md` sempre que houver novo commit, execução, artefato, teste no aparelho ou diagnóstico relevante. Registrar apenas resultados confirmados, distinguindo build bem-sucedido de jogo funcional.



## Resultado confirmado do build privado #21 — 2026-11-07

- Workflow #21, run ID `42417490244`, terminou com `conclusion=success`; job `android-apk` ID `128538620833` também terminou com sucesso.
- Logs confirmam que o checkout público foi feito na branch `android-rebuild` e que o commit efetivamente compilado foi exatamente `38f62c55a099f54fc8302293366c9f602f98901f`, contendo o redirecionamento de HOME/XDG para armazenamento privado do app. Não foi apenas o texto do pedido de build: o `git log -1` do checkout registrou esse SHA.
- A validação privada do XEX passou; codegen privado e compilação Android ARM64 concluíram; o APK foi assinado e verificado, e `APK native library validation: PASS`.
- O APK contém bibliotecas `arm64-v8a`: `libSDL3.so`, `libmain.so`, `librexgpu-xenosd.so` e `librexruntimed.so`. O plugin Xenos está presente no pacote.
- Artefato APK: `recvx-private-android-arm64`, ID `13593797262`, tamanho ZIP 88.122.339 bytes, SHA-256 do ZIP `3e61ff3357a6ba46940aef663f87c8fadae577d2b4a607e1ea0af4b19ccc4acc`. APK extraído durante a inspeção: 89.226.057 bytes, SHA-256 `31ee5f6cfc973233ea421f81e8a456bc68e4019b6ae5cc0da835d9e872c89ea3`.
- Artefato de diagnóstico: `recvx-private-diagnostics`, ID `13593667462`; validação de bibliotecas nativas registrada como PASS.
- O workflow removeu do runner o XEX privado, as fontes geradas do título e o checkout do SDK no passo final. O XEX e as fontes geradas não foram publicados no repositório público.
- URL do workflow: https://github.com/joaovitoroutlok821-dot/recvx-private-build/actions/runs/42417490244

### Interpretação e pendência

- O build #21 prova que a correção de armazenamento compila e está incluída no APK; não prova ainda que o runtime não tentará escrever em `/data/.local` em execução real.
- Próximo passo obrigatório: o usuário instalar e testar este APK no Motorola Edge 30 Pro, selecionar a pasta do jogo e iniciar. Se fechar, enviar novo logcat/crash log para verificar o caminho HOME/XDG e a próxima falha.
- Estado do projeto: APK #21 construído com sucesso; teste físico e execução do jogo ainda pendentes. Não declarar o jogo funcional até confirmação no aparelho.
