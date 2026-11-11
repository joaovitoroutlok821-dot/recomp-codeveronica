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


## Primeiro teste físico do APK #21 — jogo abriu, desempenho baixo — 2026-11-07

- O usuário instalou e executou o APK #21 no Motorola Edge 30 Pro (Android 13, Snapdragon 8 Gen 1).
- Evidência visual enviada: cena 3D/cutscene de Resident Evil Code Veronica X aparece na tela do aparelho. O usuário confirmou: “O jogo abriu, mas está muito lento”.
- Isso confirma que o fluxo de inicialização, carregamento do XEX, plugin Xenos e apresentação de imagem chegaram a produzir saída visível no aparelho. A falha anterior de encerramento por caminho /data/.local foi superada para permitir esta execução.
- Sintoma atual: desempenho muito baixo/lentidão durante a cena. Ainda não há medição de FPS, logcat de execução ou diagnóstico de GPU/CPU; não atribuir a causa a resolução, Vulkan, compilação ou shader sem evidência.
- Revisão do código atual: src/recvx_app.h ativa explicitamente config.gpu_plugin = xenos; a rotina CaptureFirstVisibleGuestFrame() captura somente um frame visível e encerra a thread, portanto não deve ser presumida como carga contínua de captura durante o jogo. src/android_main.cpp configura HOME/XDG no armazenamento privado antes de inicializar o runtime.
- Próxima investigação: obter FPS aproximado e logcat enquanto o jogo está lento; identificar se o gargalo está em CPU/PPC, GPU/Xenos/Vulkan, compilação de shaders ou sincronização/present. Evitar reduzir resolução ou alterar flags de GPU antes de obter uma linha de base.
- Estado: primeiro resultado visual real do jogo no Android confirmado; execução ainda lenta e não jogável até otimização e novos testes.


## Detalhe do teste #21: cutscene lenta e sem controles táteis — 2026-11-07

- O usuário esclareceu que o sintoma é a opção 2: o jogo parece rodar em câmera lenta/baixa taxa de quadros já na primeira cutscene.
- Não há botões de toque visíveis na tela para tentar pular a cutscene; assim, o usuário não consegue testar a jogabilidade/interação além da reprodução automática da cena.
- Revisão do projeto confirma que a aplicação atual apenas registra `RecvXApp` e inicia ReXGlue (`src/main.cpp`); não há overlay Android próprio de controles táteis nos arquivos `src/` do projeto. Não assumir que os controles estejam implementados.
- `src/recvx_app.h` ativa Xenos e possui uma thread de captura de um único primeiro frame visível, encerrando após capturar; essa captura não é um loop contínuo de vídeo.
- Próximas prioridades técnicas: (1) implementar camada de controles táteis Android (stick/D-pad e botões Xbox A/B/X/Y, Start/Back e gatilhos, com eventos encaminhados à entrada SDL/Gamepad do runtime) para permitir pular cutscenes e jogar; (2) coletar diagnóstico de desempenho/FPS e logs durante a cutscene antes de escolher otimizações CPU/GPU. Não atribuir a lentidão apenas à cutscene nem reduzir resolução sem medição.
- Estado: jogo renderiza no aparelho, porém cutscene muito lenta e sem controles táteis; ainda não é possível confirmar interação/jogabilidade.


## Build de desempenho Release #22 iniciado — 2026-11-07

- Após o usuário confirmar continuação, foi alterado o workflow privado `private-android-apk.yml` para compilar `assembleRelease` em vez de `assembleDebug`, assinar a variante Release com `signingConfigs.debug` para permitir instalação direta de teste e publicar `app-release.apk` no artefato.
- Commits no repositório privado `recvx-private-build`: `e8b06039bf4a456f21e51edf3c31a65de77a7230` (troca para Release e configuração de assinatura) e `c0e8159ae60ca3a52643e9ae8c7733af6b676f01` (corrige caminho do artefato Release).
- Pedido de build criado em `.github/build-requests/recvx-release-perf-20261107.txt`; commit privado `736dc4eab1005d5796f6803ef288b02e0bf7e0c1`.
- GitHub confirmou Workflow privado #22, run ID `42425746734`, evento `push`, status inicial `queued`, URL https://github.com/joaovitoroutlok821-dot/recvx-private-build/actions/runs/42425746734.
- Objetivo: comparar o desempenho da variante otimizada Release com o APK #21 Debug no mesmo aparelho/cena. Isso é um teste de hipótese; não garante por si só aumento de FPS.
- Controles táteis: ainda não implementados. O projeto atual instala `GameSDLActivity` derivada de `SDLActivity`, mas não tem overlay próprio nem ponte validada para injetar botões virtuais na entrada SDL. Não alegar que os controles já foram adicionados; requer implementação e teste separados.
- Próximos passos: monitorar run #22, verificar logs confirmando checkout do branch `android-rebuild`, validar APK Release assinado e bibliotecas ARM64, e disponibilizar o artefato somente após sucesso. Depois continuar a integração real dos controles virtuais e medir FPS/CPU/GPU com logs.


## Teste com controle Bluetooth: menus aceitáveis, cutscenes e gameplay lentos — 2026-11-08

- O usuário conectou um controle Bluetooth e conseguiu pular a primeira cutscene no APK #21.
- Observação de desempenho: menus rodam em nível aceitável; cutscenes e gameplay ficam muito lentos. Isso indica que o problema não se limita à apresentação inicial nem à falta de controles. O custo elevado aparece em cargas de jogo/cenas 3D.
- Hipóteses ainda abertas: custo de CPU na execução recompilada (PPC), GPU Xenos/Vulkan, sincronização/present ou compilação/cache de shaders. Não há FPS medido nem logs/perfis suficientes para isolar o gargalo.
- Workflow #22 (Release otimizada) está em andamento, run ID `42425746734`, job `128563518683`; checkout privado/XEX e checkout da fonte pública concluídos, validação XEX passou, geração privada de fontes em andamento. URL: https://github.com/joaovitoroutlok821-dot/recvx-private-build/actions/runs/42425746734
- Próximo passo: aguardar APK Release, testar exatamente a mesma cena/trecho no mesmo aparelho e comparar com APK #21. Em paralelo, coletar FPS e logcat em gameplay; só então decidir se a otimização deve focar CPU, Xenos/Vulkan, shaders ou frame pacing. Controle Bluetooth já serve como meio temporário para navegar/pular cutscenes; overlay touch continua como melhoria separada, não como causa primária da lentidão.


## Solicitação: contador de FPS para próxima compilação — 2026-11-08

- O usuário pediu explicitamente adicionar contador de FPS na próxima compilação para medir objetivamente o desempenho.
- Incluir FPS visível na tela durante menus, cutscenes e gameplay, preferencialmente com opção de ligar/desligar nas configurações. Se o overlay visual não puder ser implementado com segurança na próxima build, ao menos registrar FPS médio/atual e frametime em log com amostragem periódica, sem gerar carga excessiva.
- A medição deve refletir frames efetivamente apresentados/renderizados, não simplesmente iterações de loop. Investigar ponto correto de apresentação no SDL/ReXGlue/Xenos antes de instrumentar.
- Workflow #22 Release já estava em andamento quando a solicitação chegou; não alterar runner/build já iniciado. Incorporar o contador na próxima compilação posterior ao #22, ou em uma nova build após confirmar o resultado do #22.
- Objetivo da telemetria: comparar menus, cutscenes e gameplay e ajudar a separar gargalo CPU/PPC, GPU/Xenos/Vulkan e sincronização/frame pacing.


## Atualização — acompanhamento do Workflow #22 (2026-11-07)
- Run #22: https://github.com/joaovitoroutlok821-dot/recvx-private-build/actions/runs/42425746734
- Estado consultado: `in_progress`; ainda não há artefatos publicados.
- Checkout do XEX privado, validação do XEX, checkout da fonte pública, geração privada das fontes, instalação do Android SDK/NDK/CMake, configuração do Java 17, patches de compatibilidade e checkout do SDL 3.5.0 concluídos com sucesso.
- Etapa atual: `Configure and compile Android ARM64 native libraries` em andamento. Verificação do APK, coleta de diagnóstico, upload e limpeza ainda pendentes.
- Nenhum APK #22 disponível para teste neste momento. Não iniciar nova build enquanto esta estiver ativa.
- Próximo passo: aguardar a conclusão, validar APK Release/ARM64 e só então solicitar teste no Motorola. A instrumentação de FPS permanece planejada para a compilação seguinte, depois de investigar o ponto real de apresentação dos frames.


## Atualização — Workflow #22 e correção do validador (2026-11-08)
- Workflow #22 terminou com conclusão `failure`, mas a compilação Gradle `assembleRelease` terminou em `BUILD SUCCESSFUL`.
- O APK foi gerado e enviado como artefato privado `recvx-private-android-arm64` (artefato ID 13595979670; retenção até 2026-11-11). O APK contém bibliotecas ARM64 `libmain.so`, `libSDL3.so`, `librexruntimerd.so` e `librexgpu-xenosrd.so`; dados do jogo não foram embutidos.
- A falha foi exclusivamente no validador: ele aceitava sufixo `d`, mas as bibliotecas foram produzidas com sufixo `rd` (RelWithDebInfo). A etapa interrompeu antes de executar zipalign/apksigner, então o artefato #22 não deve ser usado como entrega final.
- Corrigido o workflow privado para aceitar nomes Release, Debug e RelWithDebInfo (`rd`): commit `d23718a6f81ddd984dfed4252be7e37846fd875c`.
- Criado pedido de nova execução; Workflow #23 confirmado via API, run ID `42429276112`, estado inicial `queued`: https://github.com/joaovitoroutlok821-dot/recvx-private-build/actions/runs/42429276112
- Próximo passo: acompanhar #23 até completar validação nativa, zipalign e assinatura. Não solicitar teste do APK #22; aguardar o artefato validado do #23.
- O contador de FPS permanece planejado para a compilação posterior, após resolver a validação e confirmar a instalação do Release.


## Teste físico do APK #23 — desempenho melhorou; entradas sem funcionar — 2026-11-08
- Usuário instalou e executou o APK do Workflow #23 no Motorola Edge 30 Pro.
- Resultado de desempenho informado: a cutscene inicial agora roda em velocidade normal. É uma melhoria clara sobre o APK #21, cuja cutscene era muito lenta. Ainda não há medição numérica de FPS nem confirmação sobre a velocidade de gameplay completa.
- Regressões/problemas informados: controle Bluetooth não funciona no APK #23 e os controles virtuais/táteis não aparecem na tela.
- Workflow #23 run ID `42429276112`, conclusão `success`; job ID `128574326035`. Todas as etapas passaram: geração privada, compilação ARM64, verificação das bibliotecas, zipalign, assinatura, upload e limpeza dos dados privados. APK artifact ID `13598044311`, artefato `recvx-private-android-arm64`, digest SHA256 `72c4e22433f387aa5f3e70a1af49cc72e11db9d2669da063f5839e98cafde98d`, expira em 2026-11-11T01:14:43Z.
- Inspeção do código da branch `android-rebuild`: `scripts/install-android-game-setup.py` instala uma `GameSDLActivity` que apenas estende `SDLActivity` e sobrescreve `getArguments()`; não adiciona overlay, botões virtuais ou joystick virtual. Portanto, a ausência de controles na tela é explicada pela implementação atual.
- A mesma classe não sobrescreve callbacks Android de joystick/teclas nem registra mapeamento próprio. Ainda não foi isolado se o Bluetooth deixa de ser detectado pelo SDL/Android ou se os eventos chegam ao SDL mas não são mapeados para os controles do jogo/ReXGlue. Não declarar causa definitiva sem instrumentação.
- Próxima prioridade: (1) instrumentar detecção de dispositivos SDL GameController/Joystick e eventos de botão/eixos, verificar lifecycle/foco Android e mapeamento para entrada do título; (2) projetar overlay touch de baixo custo com D-pad/stick e botões ABXY, Start/Back, encaminhando eventos à mesma camada de entrada do runtime; (3) manter Release otimizado que normalizou a cutscene; (4) adicionar FPS/frametime com medição do frame efetivamente apresentado, evitando overlay pesado.
- Não desfazer Release nem fazer downgrade de desempenho. Não gerar nova build com controles fictícios: implementar e validar que os eventos alcançam o jogo antes de publicar.


## Investigação complementar após APK #23 (2026-11-08)
- Comparação dos logs reais dos jobs #21 (job 128538620833) e #23 (job 128574326035): ambos executaram `bash ./build.sh --release --jobs 2`, configuraram o ReXGlue como Release, compilaram com `--config Release`, prepararam o mesmo SDL 3.5.0 no commit `8bf3b7215ad9fc3deb583c6a3a37c6c67f2e24e4` e construíram o APK com `assembleRelease`.
- Portanto, a hipótese anterior de que a falha Bluetooth do #23 decorreu simplesmente de mudança Debug -> Release não é sustentada: os logs mostram Release nos dois builds comparados.
- A sequência de etapas e o SDL pinado também são iguais nos dois jobs; a causa permanece indeterminada e deve ser isolada por diagnóstico em runtime e comparação dos commits/artefatos de origem.
- O launcher gerado por `scripts/install-android-game-setup.py` cria `GameSDLActivity` que apenas estende `SDLActivity` e fornece argumentos. Não há camada de botões touch nem código próprio de captura de gamepad nesse projeto.
- Próxima investigação: comparar o SHA do checkout do projeto público usado por cada run e as configurações/patches efetivos; instrumentar enumeração de dispositivos e eventos SDL Android sem substituir os handlers padrão do SDL. Depois, implementar overlay touch ligado ao mesmo caminho de entrada usado pelo jogo e FPS/frame-time no ponto real de apresentação.
- Não iniciar novo build até concluir a revisão técnica e validar os patches; manter APK/game data fora do repositório público.


## Implementação de controles Android, diagnóstico Bluetooth e FPS — 2026-11-08

### Comparação da entrada Bluetooth entre os Builds #21 e #23
- O Build #21 usou o código público 38f62c55a099f54fc8302293366c9f602f98901f.
- O Build #23 usou 720427a4e48e35307c54d481ebc0f89a09d848aa.
- A comparação dos commits mostra oito commits de diferença, mas todos alteraram somente CONTINUATION.md; nenhum arquivo executável, JNI, SDL, CMake ou código de entrada foi alterado.
- Portanto, não há evidência de regressão de código entre #21 e #23 para explicar o controle Bluetooth. A causa permanece aberta e será isolada pelos novos logs Android/SDL.

### Código adicionado à branch android-rebuild
- Commit inicial: c30882eed982af4a51aa4f87fe04a1d8970a2cbf.
- Commit de correção de includes SDL: 55b671b6a5f69587307b7896637872e564ae5b14.
- Commit atual após instrumentação FPS visível: c0a7f790569c31410fbb3f3dfc983e571f5e7dbd.
- scripts/install-android-game-setup.py agora gera TouchControlsView.java e atualiza GameSDLActivity com enumeração de dispositivos Android e logs de eventos de teclas/eixos do controle.
- A camada tátil apresenta joystick analógico, D-pad digital, A/B/X/Y, LB/RB, Back e Start; os eventos são encaminhados a um gamepad virtual SDL.
- src/android_main.cpp cria o gamepad virtual sob demanda por JNI e atualiza seus eixos/botões com as APIs virtuais SDL. O gamepad tem nome estável Resident Evil Code Veronica Touch.
- scripts/ensure-rexglue-android-input-fps.py classifica esse dispositivo como sintético no driver SDL do ReXGlue para que ele seja atribuído ao usuário 0 sem deslocar controles físicos; também instrumenta as apresentações Vulkan bem-sucedidas.
- O FPS é calculado a partir de apresentações Vulkan confirmadas, amostrado a cada 2 segundos, registrado como [RECVX-FPS] e exposto por JNI para o rótulo FPS no overlay.
- O código de diagnóstico Bluetooth registra os dispositivos de entrada vistos pelo Android, eventos de teclas e movimentos de eixos, sem substituir os handlers SDL existentes.

### Validação e builds
- Validação pública do commit atual: workflow #81, run ID 42437789117, conclusão success.
- Smoke test Android SDL/SAF: workflow run ID 42437789139, conclusão success; o APK de teste compilou e passou na validação de package, ABI, SDL/JNI, manifest, zipalign e assinatura. Artefato recvx-android-sdl-saf-test ID 13600595696. Esse APK é apenas o teste SDL/SAF, não contém ReXGlue nem o jogo.
- Build privado #24: run ID 42437618738, ainda em andamento na última consulta. Foi iniciado antes da correção dos includes SDL explícitos; tratar seu resultado como diagnóstico, não presumir que contenha a revisão final.
- Build privado #25: run ID 42437695379, ainda em andamento na última consulta. Verificar nos logs qual SHA público foi efetivamente baixado antes de atribuir a ele a versão final do contador FPS visível.
- Workflow privado atualizado para executar ensure-rexglue-android-input-fps.py após os patches Android do SDK.
- Não declarar APK pronto até Gradle, validação das bibliotecas, zipalign, assinatura e upload terminarem com sucesso. Depois confirmar no Motorola Edge 30 Pro: overlay visível, botões táteis funcionando, controle Bluetooth detectado e FPS atualizado durante menus, cutscenes e gameplay.
- O Default.xex e as fontes geradas continuam exclusivamente no runner privado e devem ser removidos no passo de limpeza.


## Editor de posições dos controles táteis — 2026-11-08

- Adicionado `scripts/android/TouchLayoutEditorActivity.java`, um editor visual em orientação paisagem para arrastar joystick e os oito botões táteis.
- A aba Controles de `GameSettingsActivity` agora inclui o botão **Mover botões na tela**, que abre o editor; há opção para restaurar as posições padrão e concluir.
- As coordenadas são persistidas em `recvx_settings` (`touch_stick_x/y` e `touch_btn_x_0..7/y_0..7`).
- `TouchControlsView`, gerado por `install-android-game-setup.py`, agora lê essas preferências para desenhar e detectar os controles nas posições escolhidas.
- O instalador copia a nova Activity e a registra no AndroidManifest.
- Commits: `3fc21c7a` (persistência no overlay e manifesto), `de0c056f` (editor visual), `705640d2` (correção de seleção no editor), `89d4e23a` (integração na aba Controles).
- Validação automatizada do repositório: workflow #113, run ID `42499960948`, conclusão success. Isso valida o repositório, mas não substitui compilação Android nem teste no Motorola.
- Ainda não foi gerado APK privado com essa mudança. Não declarar o editor validado no aparelho até testar arraste, salvamento, restauração e posicionamento no jogo.


## Atualização — launcher HTML conectado ao Android (2026-11-10)

- A prévia aprovada foi mantida em `assets/launcher/index.html` e agora é copiada pelo instalador para `app/src/main/assets/launcher/index.html`.
- `GameSetupActivity` passou a carregar a página em um WebView em tela cheia, com JavaScript e armazenamento DOM habilitados.
- Foi adicionada a ponte JavaScript `GameBridge` com comandos para abrir o seletor Android de pasta, iniciar o jogo, consultar o estado do diretório, salvar preferências compatíveis, abrir o editor de controles e sair.
- Os botões da página Iniciar Jogo e Sair foram ligados aos comandos nativos. O rodapé e a página inicial recebem o estado real da pasta selecionada.
- O mecanismo SAF existente foi preservado: valida `Default.xex` como XEX2 e copia os arquivos para o armazenamento privado antes da inicialização.
- As opções de resolução e exibição de controles na tela são as únicas preferências dessa interface atualmente conectadas a chaves que o `GameSDLActivity` já lê. As demais opções continuam visuais/preferências da interface e não devem ser apresentadas como implementadas no runtime.
- O workflow `android-smoke-test.yml` agora é acionado também por alterações em `assets/launcher/**`.
- Commits desta etapa na branch `android-rebuild`: `151cc6ba7b49273faa257e76a1e0e7b9e83bd09c` (WebView e ponte), `1782799660c493b3a1eb24f36f8f6e10c568d4e5` (ações HTML), `f0e2530a4eb9126fed15f2597be551f000e56e9c` (controles independentes de Bluetooth), `78454bf241cfcc6fba6c210af5e5596c4328695b` (preservar preferências fora da aba ativa).
- Ainda falta executar e validar o workflow. Esse teste cobre a integração SDL/JNI/SAF e o empacotamento; não prova que a recompilação do jogo inicia ou que todos os ajustes alteram o runtime.

- A interface também restaura ao abrir Configurações as preferências já salvas de resolução (1080p/720p) e controles na tela; opções sem suporte nativo continuam sem efeito declarado. Commit: `395dbb44ced60047b1c879d8fd8ae406209f1275`.


## Teste físico do APK SDL/SAF com launcher HTML — 2026-11-10

- O usuário instalou e executou o APK do workflow Android #37 no Motorola Edge 30 Pro.
- Resultado confirmado pelo usuário: o aplicativo abriu corretamente e exibiu os menus da launcher.
- Isso valida no aparelho o carregamento do WebView e a apresentação da interface HTML dentro da Activity Android; também confirma que o APK de teste não fecha imediatamente ao abrir a launcher.
- Workflow #37: run ID `42740989435`, conclusão `success`, commit `395dbb44ced60047b1c879d8fd8ae406209f1275`.
- Artefato `recvx-android-sdl-saf-test`, ID `13729935435`, aproximadamente 29 MB, retenção até 2026-11-24.
- Escopo ainda não confirmado pelo teste relatado: seleção de pasta via SAF, cópia/validação do `Default.xex`, persistência de preferências e inicialização do runtime do jogo. Não assumir que essas etapas foram testadas só porque os menus apareceram.
- Este APK continua sendo smoke test SDL/JNI/SAF com launcher HTML; não contém a recompilação real do Resident Evil nem demonstra inicialização do jogo.
- Próxima etapa técnica: usar o sucesso do WebView como base e avançar na integração do entrypoint Android com ReXGlue/runtime e no caminho de dados SAF, mantendo a interface visual. Depois gerar um APK de jogo separado e validar seleção de pasta, inicialização e logs.


## Build privado #37 iniciado após validação física da launcher — 2026-11-10

- Depois que o usuário confirmou que o APK SDL/SAF #37 abriu no Motorola Edge 30 Pro e exibiu os menus, foi solicitado um novo build privado do aplicativo completo usando a branch `android-rebuild`.
- Pedido criado no repositório privado `recvx-private-build`: `.github/build-requests/recvx-launcher-runtime-20261110.txt`, commit `bd465a2d3b050be0cc534161f72ca7a66f4baead`.
- GitHub Actions confirmou a execução privada #37, run ID `42743201092`, estado inicial `queued`: https://github.com/joaovitoroutlok821-dot/recvx-private-build/actions/runs/42743201092
- O build usa o XEX exclusivamente do repositório privado e o mantém apenas no workspace efêmero do runner; fontes geradas e SDK também são removidos na limpeza. Nenhum dado do jogo foi adicionado ao repositório público.
- Objetivo: compilar o app ReXGlue ARM64 completo com a launcher WebView recém-validada, SDL 3.5.0, runtime e plugin Xenos, mantendo a configuração Release, controles táteis e diagnóstico FPS.
- Estado no momento do registro: aguardando execução; ainda não há APK #37 privado nem resultado de compilação confirmado.
- Próxima etapa: acompanhar codegen, compilação Android, validação de bibliotecas, alinhamento/assinatura e artefatos. Mesmo que o build passe, testar no aparelho a seleção/cópia da pasta e o início real do jogo antes de declarar sucesso.

## Correções após teste físico do APK #37 — 2026-11-10

- Usuário confirmou que o APK #37 abre e mostra as opções da launcher. Reportou dois problemas no aparelho: indicador de progresso/tamanho desapareceu durante a cópia SAF; controle Bluetooth é detectado e faz os botões táteis sumirem, mas os comandos não funcionam no jogo.
- Causa do progresso: `GameSetupActivity` já calculava bytes e porcentagem, mas a interface de progresso era uma View nativa escondida atrás do WebView (`setContentView`). Correção: `scripts/install-android-game-setup.py` agora envia callbacks `onNativeCopyProgress` para a WebView; `assets/launcher/index.html` exibe barra, percentual e tamanho copiado/total na tela inicial.
- Causa provável do fallback de controles: `GameSDLActivity` escondia o overlay após qualquer tecla/movimento Android, sem confirmar que SDL/ReXGlue consumiu o comando. Removida essa ocultação automática; os controles táteis permanecem visíveis como fallback. `src/android_main.cpp` inicializa explicitamente `SDL_INIT_GAMEPAD` antes do contexto ReXGlue.
- Commits das correções: script `3057cedda5893f60caea2ee2086559117e1b559b`; HTML `4b76e110831ea5ef19498b3c389c808967e7ba63`; C++ `36a9590704a957448593bf252d4ef7cf2b414e12` e ajuste de log subsequente.
- Ainda não declarar controle Bluetooth funcional: precisa compilar e testar no aparelho; conferir `RECVX-INPUT` e SDL gamepad logs, incluindo botões, D-pad e eixos analógicos. Se SDL detectar o controle mas o jogo não receber, investigar o mapeamento SDL/ReXGlue/guest input.
- Próximo build privado deve incluir essas alterações e preservar o XEX exclusivamente no workspace privado efêmero. Validar também barra de progresso, porcentagem e bytes no fluxo SAF.

## Auditoria funcional da launcher HTML — 2026-11-10

- Revisado o código efetivo de `assets/launcher/index.html` na branch `android-rebuild`, não apenas a documentação ou a prévia visual.
- A tela `settings()` atualmente cria os campos de Gráficos, Desempenho, Controles e Áudio dinamicamente. Os botões de toggle apenas alternam classe CSS/texto; sliders apenas atualizam o percentual mostrado; seletores não têm associação individual a chaves de configuração.
- `applySettings()` localiza e envia somente dois valores à ponte Android: `resolution` (mapeada apenas entre 1080p e 720p) e `touch_mode` (controles na tela ligados/desligados). Todos os outros valores visíveis são ignorados no momento de aplicar.
- `restoreSettings()` restaura somente `resolution` e `touch_mode`; não reconstrói os demais campos a partir de preferências persistidas. A função `loadSettings()` da ponte Java também retorna apenas essas duas chaves.
- `GameSDLActivity.getArguments()` passa ao ReXGlue somente `game_data_root`, largura/altura (720p ou 1080p) e `present_effect=bilinear`. Não há passagem atual dos demais controles da launcher.
- A classe `TouchControlsView` lê `show_fps` das preferências, mas o HTML atual não envia esse valor no método `applySettings()`; portanto, o toggle de contador FPS mostrado na launcher não controla atualmente essa preferência.
- O documento `LAUNCHER_SETTINGS_PLAN.md` já registra os limites conhecidos do SDK Android: FidelityFX está desabilitado no workflow privado, então CAS/FSR não devem ser oferecidos como funcionais; não foi encontrado suporte confirmado para limite exato de FPS, shader cache, qualidade de partículas/efeitos, anti-aliasing ou controles de áudio do jogo. V-Sync/FPS cap também não podem ser simulados por simples persistência.
- Resultado da comparação do baseline #25 (commit `55b671b6a5f69587307b7896637872e564ae5b14`) com `android-rebuild`: 68 commits à frente. Os arquivos modificados relevantes são `scripts/install-android-game-setup.py`, `scripts/ensure-rexglue-android-input-fps.py` e `src/android_main.cpp`; o HTML da launcher e as Activities de configurações/editor foram adicionados depois do baseline. Essa comparação não identifica por si só a causa da regressão Bluetooth.
- Próxima implementação: criar um modelo único de preferências com chaves estáveis, carregar os valores antes de desenhar a tela, associar cada controle a uma chave, salvar/restaurar de forma consistente e passar somente opções comprovadamente suportadas ao runtime. Opções sem hook real devem ficar desabilitadas com explicação, sem alternar visualmente como se funcionassem.
- Não alterar a arte, geometria ou identidade visual aprovada. Separar a correção funcional da investigação Bluetooth e preservar os ganhos de desempenho; comparar os diffs de entrada SDL/JNI entre o build funcional histórico e o atual antes de reverter qualquer alteração.


## Primeira integração real das opções da launcher — 2026-11-10

- Alterado `assets/launcher/index.html` para manter editáveis somente os três controles com integração nativa confirmada nesta etapa: resolução de saída, contador FPS e visibilidade dos controles na tela. Os demais seletores, sliders e toggles agora ficam desativados e mostram explicação de que ainda não há suporte confirmado; a aparência geral e a disposição visual foram preservadas.
- A resolução agora oferece apenas 1080p e 720p, que são os dois modos efetivamente mapeados por `GameSDLActivity.getArguments()`. Foram removidos 900p/480p da seleção ativa para evitar que a UI apresentasse valores que o código convertia incorretamente para 720p.
- O botão Aplicar agora envia `resolution`, `show_fps` e `touch_mode` à ponte Android, em vez de salvar somente resolução e modo de toque. A função de restauração lê os três valores e atualiza os controles correspondentes ao abrir cada aba.
- Atualizado `LauncherBridge.loadSettings()` no gerador `scripts/install-android-game-setup.py` para retornar também `show_fps`. O código nativo já lê essa preferência em `TouchControlsView`, então o toggle FPS passa a controlar a preferência efetiva após reiniciar/abrir o jogo; a resolução continua sendo aplicada como largura/altura nos argumentos do ReXGlue e `touch_mode` controla a exibição do overlay.
- Commits: HTML `fbecd5ab2aeaf56c1fe8a84181af905f7c0a4594`, correção dos atributos disabled `69d109aad3577cab07dc10cac128739ce8996689`, ponte Android `ad9a6e24fb7851172b113030f23a623d29fa4b3b`.
- Ainda não há APK validado. A próxima etapa é executar verificações de build/smoke test, confirmar que as preferências sobrevivem ao reinício e verificar no aparelho que o contador FPS pode ser ligado/desligado. As opções desativadas só devem ser reabilitadas quando forem ligadas a hooks reais do runtime.



## Validação das primeiras opções nativas da launcher — 2026-11-10 (continuação)

- Auditoria posterior confirmou que os rótulos usados no HTML coincidem exatamente com as chaves consultadas por `restoreSettings()`: `Resolução de saída`, `Contador de FPS` e `Controles na tela`.
- A função `rows()` passa todos os campos de configuração por `field()`; portanto, os campos sem suporte confirmado recebem `disabled` e a indicação de indisponibilidade. Os três campos liberados são os únicos com integração nesta etapa.
- A ação Aplicar envia os três valores pela ponte Android. A restauração ocorre ao abrir cada aba; a preferência de FPS agora também é retornada por `LauncherBridge.loadSettings()`.
- Smoke test Android #40 (run ID `42851819635`, commit `fbecd5ab2aeaf56c1fe8a84181af905f7c0a4594`), #41 (run ID `42851847630`, commit `69d109aad3577cab07dc10cac128739ce8996689`) e #42 (run ID `42851861396`, commit `ad9a6e24fb7851172b113030f23a623d29fa4b3b`) concluíram com sucesso. O run #42 compilou o APK debug, validou package/ABI/SDL-JNI/Activities/manifest/zipalign/assinatura e publicou o artefato `recvx-android-sdl-saf-test`, ID `13779909421` (aprox. 29,9 MB; expira em 2026-11-24).
- A validação geral #152 (run ID `42851910334`, commit `0bad06596b537c087330fa6e28d627958a8cae4b`) também concluiu com sucesso.
- Importante: esses workflows produzem um APK de smoke test SDL/JNI/SAF com launcher, não o APK privado completo com ReXGlue e a recompilação do jogo. O sucesso de compilação não confirma o funcionamento do FPS/resolução/overlay no jogo nem a inicialização do título.
- O HTML mantém os toggles de interface simples; a confirmação final de persistência e comportamento precisa ser feita no APK instalado. A resolução altera os argumentos de largura/altura, FPS altera a preferência lida pelo overlay, e touch_mode controla a exibição do overlay.
- Não foi encontrada uma ação disponível no conector GitHub para disparar manualmente um workflow novo; não declarar que o build privado foi iniciado. Próximo passo: continuar a auditoria do caminho de entrada Bluetooth e dos hooks de runtime, preservando as opções ainda desativadas, e depois gerar/validar o APK privado completo.


## Continuação — ação Restaurar padrões da launcher (2026-11-10)

- Commit `db348237ef473dc848a2b8406d198d1115c1bbca`: o botão **Restaurar padrões** deixou de exibir apenas uma mensagem demonstrativa e agora chama a ponte nativa `GameBridge.resetSettings()`, recarregando os valores restaurados na interface.
- Commit `f19d7a6538ec38513581aeb750ab7dc46392b427`: implementado `LauncherBridge.resetSettings()` no instalador Android. Ele limpa as preferências antigas e grava os padrões efetivamente suportados: resolução 1080p, contador FPS ativado e controles na tela ativados.
- Esta alteração não habilita opções ainda sem suporte e não altera a arte/layout da launcher.
- Ainda não houve compilação nem teste no Motorola após estes commits. É necessário reconstruir o APK para validar a ponte JavaScript/Android.
- **Salvar estado / Carregar estado** continuam sendo demonstrações sem backend de save-state. Não foi adicionada uma falsa implementação: é necessário localizar uma API real de snapshot/restore no runtime antes de ligar esses botões.


## Auditoria adicional — Salvar/Carregar (2026-11-10)

- Revisados `assets/launcher/index.html`, `scripts/install-android-game-setup.py`, `src/android_main.cpp`, `src/recvx_app.h` e `LAUNCHER_SETTINGS_PLAN.md`.
- Os botões **Salvar estado** e **Carregar estado** continuam sendo apenas demonstrações: o HTML chama mensagens de toast, sem ponte nativa.
- A ponte Android atual possui seleção de pasta, início do jogo, status do diretório, persistência/restauração de preferências, editor de controles e saída. Não possui métodos de save-state/load-state.
- `src/android_main.cpp` cria um diretório XDG `state` dentro do armazenamento privado, mas isso é apenas um diretório de dados; não comprova suporte a captura/restauração de memória, CPU, GPU, áudio e estado do runtime.
- As buscas no código versionado por `SaveState`, `save_state`, `snapshot`, `serialize` e `checkpoint` não localizaram uma API de save-state utilizável. Portanto, não conectei os botões a arquivos comuns nem simulei salvamento: isso poderia gerar arquivos inválidos e perda de progresso.
- Próximo passo técnico: identificar a versão/commit exatos do ReXGlue/ReXRuntime usados no build privado e verificar se a API de snapshot está disponível nessa dependência. Se não existir, será necessário desenvolver suporte coordenado no runtime; não é uma função que possa ser implementada corretamente apenas no HTML/Java.
- A ação **Sair** já chama `GameBridge.exitApp()` e finaliza a Activity da launcher. A página **Informações** é informativa/estática, o que é apropriado para essa seção.


## Auditoria de sincronização para Save/Load — 2026-11-10

- Revisado o código Android atual em `src/android_main.cpp`: o SDL main thread inicializa `SDLWindowedAppContext`, chama `RecvXApp::OnInitialize()` e permanece em `RunMainMessageLoop()`, que processa eventos SDL. Esse loop não é o loop de execução do jogo.
- Revisado `src/recvx_app.h`: `OnPostLaunchModule(XThread*)` é chamado após a criação da thread principal do guest ainda suspensa; o projeto inicia ali uma thread auxiliar para capturar o primeiro frame. `OnShutdown()` interrompe e aguarda essa thread auxiliar.
- Revisado `include/rex/runtime.h` do SDK fixado: Runtime expõe Memory, KernelState, GraphicsSystem, AudioSystem e InputSystem, mas não oferece uma operação pública única de pausa global ou SaveState/RestoreState.
- Revisado `include/rex/ui/windowed_app_context_sdl.h` e `src/ui/windowed_app_context_sdl.cpp`: o loop SDL espera e despacha eventos/paint; não constitui uma barreira que pare threads guest, áudio ou GPU.
- O contrato de Presenter documenta que a atualização da imagem guest tem regras de concorrência próprias; não se deve tratar captura de imagem como sincronização de todo o runtime.
- Conclusão: ainda não há uma barreira global demonstrada para congelar consistentemente guest threads/fibers, callbacks de kernel, áudio e CommandProcessor. Não implementar os botões Save/Load chamando isoladamente `Memory::Save`, `KernelState::Save`, `AudioSystem::Save` e `GraphicsSystem::Save` enquanto o jogo continua executando.
- Próxima etapa técnica: auditar o ponto de lançamento e a coordenação de threads/fibers no SDK (incluindo todos os threads do title process e execução assíncrona do GPU/audio); definir uma barreira cooperativa com timeout e rollback antes de qualquer serialização. Validar primeiro round-trip no mesmo processo e só então persistência após reiniciar o app.
- Nenhum código de jogo, launcher, APK ou runtime foi alterado nesta auditoria; nenhum Save/Load foi declarado funcional.


## Bloqueador confirmado no serializador de threads do ReXGlue — 2026-11-10

Auditoria adicional no SDK upstream `rexglue/rexglue-sdk`, commit fixado `398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb`:

- `KernelState::Save()` percorre objetos `XThread` e tenta serializar threads guest antes dos demais objetos. Threads host são omitidas porque devem ser recriadas.
- `XThread::Save()` retorna `false` imediatamente quando `running_ == true`, emitindo `serialization not implemented`. O próprio código contém TODO sobre serialização compatível com ReXGlue; o bloco que salvaria contexto de execução é inalcançável para threads em execução por causa desse retorno.
- Consequência: a thread principal do jogo e quaisquer outras threads guest ativas não podem ser salvas pelo serializador atual. Suspender a thread antes de chamar Save não resolve por si só: o estado de contexto/PC da thread ainda não tem suporte implementado no SDK.
- `AudioSystem::Pause()/Resume()` existem na implementação concreta de áudio, mas não fazem parte da interface abstrata `IAudioSystem`; exigiriam acesso/capacidade específica do backend ou extensão da interface.
- `IGraphicsSystem` também não expõe Pause/Resume/Save/Restore na interface pública revisada. O CommandProcessor exige pausa para Save/Restore, portanto a integração gráfica precisa de uma API explícita e sincronizada.
- Decisão: não conectar os botões Save/Load ao serializador atual. O próximo trabalho necessário é no SDK: implementar captura/restauração de contexto de XThread (PC, registradores, estado PPC/fiber e stack), definir como restaurar threads guest ativas sem executar parcialmente, e fornecer barreiras/APIs de pausa e retomada para GPU e áudio. Só depois integrar snapshots de memória + kernel + GPU + áudio em uma operação transacional com validação de versão e recuperação em falha.
- Este achado é um bloqueador técnico comprovado no código upstream fixado, não apenas ausência de uma função global. Nenhum APK ou teste de save-state foi produzido nesta etapa.


## Auditoria aprofundada de XThread Save/Restore — 2026-11-10

Continuação da leitura do SDK upstream `rexglue/rexglue-sdk`, commit `398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb`, agora incluindo o caminho de restauração:

- `XThread::Save()` rejeita qualquer thread guest com `running_ == true` antes de gravar o objeto. O trecho que chama `SaveContext()` fica depois desse retorno e, portanto, não captura o contexto de uma thread ativa.
- Mesmo nesse trecho atualmente inalcançável para threads ativas, o PC local é inicializado como zero e gravado como `state.context.pc = pc`; não existe captura demonstrada do PC real da execução guest nesse caminho.
- `SaveContext()` e `LoadContext()` copiam vários registradores PPC (GPR/FPR/vetores/CR/FPSCR/XER/VSCR), mas isso não basta para retomar uma thread: é necessário um ponto de parada seguro e uma forma real de retomar a execução guest a partir do PC salvo.
- `XThread::Restore()` também não implementa a retomada: quando `state.is_running` é verdadeiro, cria uma thread host suspensa, carrega os registradores e prepara o objeto, mas a rotina da thread apenas emite `Thread restore not implemented`; não há salto/dispatch para o contexto guest restaurado nem continuação do fluxo original.
- O comentário dentro de Restore confirma que as threads precisariam de uma abordagem diferente. Assim, mesmo que fosse possível produzir um arquivo de snapshot contendo os dados de uma thread ativa, o SDK fixado não sabe retomá-la.
- A inicialização normal de uma XThread cria uma thread host e executa `Execute()`; a restauração não pode simplesmente chamar esse caminho normal, pois isso iniciaria novamente a rotina guest desde o início, em vez de continuar do ponto salvo.
- `ThreadState` mantém um `PPCContext` por thread, mas o código revisado não fornece uma API de checkpoint cooperativo que capture o contexto no limite correto da execução recompilada. Não foi encontrada evidência de que `Suspend()` do host thread capture um estado PPC reiniciável pelo ReXGlue.
- Portanto, há dois bloqueios independentes: (1) captura consistente do contexto/PC de todas as threads guest ativas e (2) restauração/retomada efetiva dessas threads. Resolver apenas o primeiro ainda produziria saves que não podem ser carregados.

### Próxima investigação técnica

1. Mapear o executor/dispatch das funções recompiladas e os pontos em que uma thread guest troca de função, espera ou retorna ao kernel; verificar se existe um ponto seguro para checkpoint sem interromper código nativo no meio de uma operação.
2. Rastrear fibras guest: como `X_FIBER_CONTEXT` armazena SP e área de registradores não voláteis, como as fibras se relacionam com o contexto PPC da thread e como o dispatcher alterna entre elas. Não confundir contexto de fiber com o contexto completo da thread host.
3. Inspecionar o mecanismo de execução de uma função recompilada para determinar se há um dispatcher capaz de reentrar por PC/endereço guest e restaurar registradores sem reiniciar a função.
4. Só depois propor uma mudança no SDK com formato de estado versionado, captura cooperativa, recriação de threads e retomada testável. Fazer teste unitário de round-trip em thread controlada antes de expor Save/Load na launcher.

Nenhum arquivo de runtime/SDK foi modificado nesta etapa; foi uma auditoria de leitura. Os botões Save/Load continuam sem backend e devem permanecer indisponíveis/demonstrativos até que captura e retomada reais sejam implementadas.

## Mapeamento de execução PPC e fibras — 2026-11-10

Leitura do SDK fixado `rexglue/rexglue-sdk@398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb`, incluindo `XThread::Execute`, `FunctionDispatcher`, `rexcrt threading.cpp` e o backend POSIX de fibras:

### Como o código recompilado realmente executa

- Cada `XThread` possui um `runtime::ThreadState` com um `PPCContext`; a thread host é criada suspensa e, ao iniciar, faz bind desse estado e chama `Execute()`.
- `FunctionDispatcher::Execute()` resolve o endereço guest para um ponteiro `PPCFunc*` e chama diretamente a função C++ recompilada: `fn(*ctx, memory_->virtual_membase())`. Não há interpretação/instrução PPC individual nesse caminho.
- O dispatcher ajusta temporariamente o SP guest, salva/restaura LR ao redor da chamada e retorna quando a função recompilada termina. Portanto, durante uma função recompilada ativa, a continuação real também depende da pilha de chamadas C++ nativa do host; não existe necessariamente um único PC guest que permita reconstruir o ponto exato.
- O caminho de interrupção usa o mesmo dispatcher e protege a execução com uma região crítica global, mas isso não é um mecanismo de checkpoint nem uma barreira geral para todas as threads.

### Como as fibras são representadas

- `X_FIBER_CONTEXT` é uma estrutura em memória guest de 0xA50 bytes. Ela guarda parâmetros, limites/base da pilha guest, SP guest e uma área de registradores não voláteis PPC.
- `SwitchToFiber_entry()` salva os registradores não voláteis e SP guest da fibra de saída, restaura os dados da fibra de destino e então chama `rex::thread::Fiber::SwitchTo()`.
- O backend POSIX usado em plataformas Linux/macOS implementa a troca com `ucontext_t` (`getcontext/makecontext/swapcontext`) e mantém uma pilha host separada em um `std::vector<uint8_t>` para cada fibra criada. A troca preserva a pilha C++ inteira durante a execução normal.
- A estrutura guest `X_FIBER_CONTEXT` não contém `ucontext_t`, a pilha host, os endereços de retorno C++ nem o estado de alocação do objeto host Fiber. Salvar somente a memória guest e essa estrutura não é suficiente para restaurar uma fibra que estava no meio de uma função recompilada.
- A fibra principal convertida por `ConvertThreadToFiber` representa a execução da própria thread host; as fibras criadas por `CreateFiber` têm pilhas guest e host distintas. O mapa `KernelState::fiber_map_` contém ponteiros host e metadados que também não são serializados pelo caminho de KernelState observado.

### Implicações para Save/Load

- O obstáculo não é apenas copiar o PC e registradores PPC. O ReXGlue executa funções recompiladas como chamadas C++ nativas, e o backend de fibras preserva continuação por meio de contexto e pilha host.
- Uma captura no meio de uma função precisaria preservar/relocar de forma segura a pilha host e o contexto de troca de cada fibra, incluindo referências e endereços internos, ou mudar a arquitetura de execução para pontos de checkpoint explícitos. Copiar bytes de uma pilha host para outro processo/execução não é uma solução segura presumível.
- Uma alternativa potencialmente mais simples seria permitir snapshots somente em pontos cooperativos comprovados nos quais todas as threads e fibras estejam fora de funções recompiladas e em estados reiniciáveis; a auditoria ainda não provou que o jogo oferece tais pontos nem que o estado de todas as chamadas pode ser reconstruído.
- O SDK fixado tem backend de fibra POSIX baseado em `ucontext`; não confundir isso com o backend Win32 baseado em `ConvertThreadToFiber/CreateFiber`. A serialização teria que ser desenhada e testada para a plataforma Android efetivamente usada.

### Próxima etapa

1. Rastrear os chamadores de `FunctionDispatcher::Execute` e os caminhos de entrada/saída do módulo principal para identificar fronteiras reais entre chamadas guest.
2. Verificar quais estados de espera/bloqueio deixam `PPCContext`, pilha guest e fibras em uma condição consistente e se a pilha host está fora de qualquer função recompilada.
3. Avaliar um protótipo isolado de checkpoint cooperativo para uma thread de teste, sem tocar ainda no jogo nem expor Save/Load na launcher.
4. Definir se o escopo viável é snapshot de sessão em execução, ou apenas save em pontos específicos/retomada após reinício. Não prometer compatibilidade universal antes dos testes.

Nenhum código do SDK ou do jogo foi alterado; esta etapa foi somente leitura e atualização documental. Save/Load continua sem backend funcional.


## Rastreamento de chamadas recompiladas e pontos de espera — 2026-11-10

Leitura adicional do SDK upstream `rexglue/rexglue-sdk@398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb`, incluindo `XThread::Execute()`, `FunctionDispatcher::Execute()`, callbacks de áudio/kernel e `KeWaitForSingleObject_entry()`:

### Fronteiras reais de execução identificadas

- A thread guest principal não entra inicialmente por `FunctionDispatcher::Execute()`: `XThread::Execute()` resolve `creation_params_.start_address` para `PPCFunc*` e chama diretamente `func(*ctx, base)`. A chamada só retorna quando a função inicial termina ou o fluxo de fibra retorna à thread principal.
- O caminho de `FunctionDispatcher::Execute()` é usado para chamadas guest adicionais, incluindo callbacks de cliente de áudio (`AudioSystem`), callbacks de entrada/saída de DLL em `KernelState` e callbacks de interrupção via `ExecuteInterrupt()`.
- `ExecuteInterrupt()` mantém uma região crítica global durante o callback, mas a região protege somente esse dispatch; não suspende todas as demais threads, fibras, áudio ou GPU e não pode ser tratada como barreira de snapshot.
- `XThread::Execute()` chama a função inicial uma vez e, quando ela retorna, trata o retorno como término implícito da thread (ou chama `Exit()`). Não existe nesse método um loop central que receba um PC guest, faça dispatch repetido e permita retomar arbitrariamente uma função interrompida.

### Espera e bloqueio não equivalem a checkpoint

- O caminho de espera do kernel (`KeWaitForSingleObject_entry`) delega a espera ao objeto/primitive de sincronização correspondente. Uma thread bloqueada pode estar parada dentro de uma cadeia de chamadas C++ nativas que entrou no kernel a partir de uma função recompilada.
- O retorno de uma espera pode continuar a mesma cadeia de chamadas nativas. Portanto, observar uma thread em estado de espera não prova que ela esteja fora de uma função recompilada, nem que sua pilha host possa ser descartada e reconstruída somente com `PPCContext`.
- O caminho de suspensão de thread altera o estado/contagem de suspensão e usa os mecanismos de thread host; não foi encontrada uma conversão geral desse evento em contexto PPC de retomada. Suspensão de host não cria, por si só, um ponto de checkpoint serializável.
- O caminho de fibra salva/restaura SP guest e registradores não voláteis no `X_FIBER_CONTEXT`, mas a continuação host fica preservada pelo mecanismo de fibra (`ucontext_t`/pilha host no backend POSIX). A troca de fibra é uma suspensão cooperativa da pilha nativa, não uma serialização dessa pilha.

### Conclusão desta etapa

- Foram identificados chamadores concretos do dispatcher, mas eles não formam um scheduler central capaz de reconstruir a execução guest a partir de um endereço salvo.
- Esperas, callbacks e trocas de fibra podem produzir pontos em que uma thread deixa de executar temporariamente, mas não comprovam um estado global consistente e restaurável para todas as threads/fibras.
- Não há evidência suficiente para afirmar que o jogo oferece fronteiras seguras universais para snapshots em execução. Um checkpoint só poderá ser considerado se for desenhado cooperativamente e validar explicitamente o estado de todas as threads, fibras, pilhas guest/host e subsistemas.

### Próxima etapa recomendada

1. Inspecionar o restante de `KeWaitForSingleObject_entry()` e as primitivas de wait usadas por eventos, semáforos e timers para mapear exatamente onde o fluxo guest bloqueia e retoma.
2. Rastrear `OnPostLaunchModule`, criação/suspensão/liberação da thread principal e criação de threads secundárias do título para saber se existe uma janela de inicialização anterior ao início do código recompilado que permita apenas um snapshot inicial (não um save de gameplay).
3. Projetar um teste isolado de checkpoint cooperativo com uma thread/fibra controlada e medir se a continuação pode ser retomada sem reiniciar a função; não ativar Save/Load na launcher até o teste passar.
4. Manter a interface Save/Load desabilitada ou claramente indisponível enquanto não houver backend de captura e restauração comprovado.

Nenhum código do runtime, do jogo ou da launcher foi alterado nesta etapa. Foi uma auditoria de leitura e atualização deste documento; não houve compilação nem teste de APK.


## Auditoria de waits e janela de lançamento — 2026-11-10

Leitura do SDK fixado `rexglue/rexglue-sdk@398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb`: `XObject::Wait/WaitMultiple/SignalAndWait`, imports `KeWaitForSingleObject`, `NtWaitForSingleObjectEx`, `KeWaitForMultipleObjects`, `KeDelayExecutionThread`, objetos Event/Semaphore/Mutant e `ReXApp::LaunchModule`.

### O que ocorre quando uma thread guest espera

- `KeWaitForSingleObject_entry` resolve o objeto guest para um `XObject` e chama `XObject::Wait()`. O método obtém o wait handle nativo e bloqueia a própria thread host chamando `rex::thread::Wait()`; após a espera, retorna pela mesma cadeia C++ que chamou o import.
- `WaitMultiple` usa `WaitAny` ou `WaitAll`; `SignalAndWait` também executa uma espera nativa. Nos três casos, a espera não despacha a thread para um loop central de PPC nem grava um contexto de continuação serializável.
- Antes e depois da espera simples/múltipla, o código chama `XThread::CheckTitleTermination()`. Isso é uma verificação de encerramento do título, não um checkpoint. Em timeout, chama `MaybeYield()`; yield apenas cede tempo de CPU e não captura pilha/contexto.
- `KeDelayExecutionThread` chama `XThread::Delay()`, que usa sleep/alertable sleep do host. `NtYieldExecution` chama `MaybeYield()`. Nenhum dos caminhos registra PC PPC, pilha C++ ou contexto ucontext para Save/Load.
- Espera alertable pode entregar APCs depois do retorno do wait. `DeliverAPCs()` executa callbacks guest através de `FunctionDispatcher::ExecuteTrap()` na própria thread/contexto; assim, até a fase de entrega de APC pode acrescentar chamadas recompiladas à cadeia nativa antes de voltar ao chamador.
- Eventos e semáforos usam primitivas nativas de sincronização. `XEvent::WaitCallback()` não fornece contexto de thread; o evento mantém sinalização. `XSemaphore::Save()` consulta o contador consumindo temporariamente tokens via waits de timeout zero e depois os libera novamente. Isso serializa o contador, não os waiters bloqueados nem a pilha das threads.
- Mutants registram a thread proprietária em `WaitCallback()`; seu estado de propriedade não equivale à continuação da thread proprietária. O código de restore tenta associar a propriedade a um objeto XThread, mas não restaura uma pilha guest/host em execução.

### Janela de lançamento encontrada

- `ReXApp::LaunchModule()` agenda a preparação na UI thread, chama `Runtime::PrepareModuleLaunch()` para criar a thread principal guest, executa `OnPostLaunchModule(main_thread.get())` enquanto ela ainda está suspensa e só então chama `main_thread->Resume()`.
- O contrato de `OnPostLaunchModule` confirma que a thread principal foi criada mas ainda não começou a executar. Este é um ponto consistente para anexar monitores ou registrar metadados pré-execução.
- Essa janela não é um save de gameplay: o código guest ainda não executou, e as threads/fibras/subsistemas criados depois não foram capturados. Também não resolve como retomar uma sessão no meio de uma função recompilada.
- O worker `module_thread_` aguarda a conclusão da thread principal e chama `OnGuestThreadExit()`; ele não atua como scheduler de execução PPC nem oferece pausa global.

### Decisão técnica

- A auditoria confirma que waits e sleeps bloqueiam a pilha nativa atual e retomam a mesma cadeia de chamadas. Portanto, uma thread em espera continua exigindo a pilha/contexto host preservados; o estado de espera não é um checkpoint automaticamente serializável.
- A única janela segura adicional identificada é anterior ao primeiro `Resume()` da thread principal. Ela pode servir para diagnóstico/instrumentação ou captura de estado inicial, mas não permite salvar progresso de gameplay.
- Não há base para ativar Save/Load em execução. O próximo protótipo deve ser um teste isolado de checkpoint cooperativo explícito, com thread e fibra controladas, demonstrando parada em fronteira definida, captura e retomada da continuação. Se a arquitetura atual não permitir isso, será necessário limitar formalmente o escopo ou redesenhar a execução no SDK.

### Próximas ações

1. Inspecionar `Runtime::PrepareModuleLaunch()` e o ciclo de criação/registro de threads para confirmar se a janela pré-`Resume()` permite uma captura inicial apenas para diagnóstico.
2. Examinar backend POSIX de wait/fiber e requisitos de Android para saber quais contextos host podem ser pausados/retomados sem corrupção; não presumir que `ucontext_t` é portável entre versões/arquiteturas.
3. Desenhar um protótipo de teste isolado, sem integrar ao jogo nem à launcher, que valide a retomada de uma função recompilada após yield cooperativo.
4. Manter Save/Load sem backend funcional até round-trip de teste passar.

Nenhum código de runtime, jogo ou launcher foi alterado; esta etapa foi somente leitura e documentação. Não houve build nem teste de APK.



## Investigação da janela pré-lançamento e fibras Android — 2026-11-10

Continuação da auditoria de Save/Load. Foram lidos no SDK upstream os caminhos de preparação do módulo, lançamento da aplicação, thread principal e backend POSIX de fibras. A leitura de código disponível nesta etapa confirma:

### Janela antes do início do jogo

- `Runtime::PrepareModuleLaunch()` obtém o módulo executável e delega a `KernelState::PrepareModuleLaunch()`.
- `KernelState::PrepareModuleLaunch()` cria a thread principal com `X_CREATE_SUSPENDED`, chama `Create()` e a retorna ainda suspensa.
- `ReXApp::LaunchModule()` chama `OnPreLaunchModule()`, prepara a thread, executa `OnPostLaunchModule(main_thread.get())` e somente depois chama `main_thread->Resume()`.
- Portanto, a janela pré-`Resume()` permite anexar instrumentação e registrar estado inicial antes do primeiro código guest. Ela não contém progresso do jogo e não é um ponto de Save State durante gameplay.
- Em `XThread::Execute()`, a função inicial é resolvida uma vez pelo endereço de entrada e chamada diretamente como função C++ recompilada. Quando retorna, o método trata o retorno como término da thread; não há ali um scheduler PPC central para reentrar arbitrariamente por PC salvo.

### Backend de fibras no Android

- `include/rex/platform.h` define `REX_PLATFORM_ANDROID` e também `REX_PLATFORM_LINUX` quando `__ANDROID__` está definido.
- O cabeçalho `include/rex/thread/fiber.h` seleciona o membro `ucontext_t context_`, pilha própria `std::vector<uint8_t> stack_`, entry/arg e estado de thread-fiber para `REX_PLATFORM_LINUX || REX_PLATFORM_MAC`. Android entra nesse caminho por também definir Linux.
- O backend `src/core/fiber_posix.cpp` usa `getcontext()` para capturar contexto inicial, `makecontext()` para montar fibras novas e `swapcontext()` para alternar entre contextos. Cada fibra criada possui uma pilha host alocada em seu próprio vetor.
- A troca normal preserva a continuação da pilha C++ host. O objeto Fiber, seu vetor de pilha, o `ucontext_t` e o TLS `tls_current_` são estado host separado da estrutura guest `X_FIBER_CONTEXT`.
- Consequentemente, salvar somente memória guest, registradores PPC e `X_FIBER_CONTEXT` não restaura uma fibra ativa. Seria necessário preservar de modo seguro o contexto host, a pilha host, a identidade/associação da fibra e as referências internas, ou introduzir pontos cooperativos que retornem a um estado reconstruível.
- `ucontext_t` não deve ser tratado como formato de arquivo portátil nem como estado seguro para transferir entre processos, versões do Android, versões de libc ou execuções diferentes. A auditoria não encontrou garantia no SDK de que um contexto capturado possa ser serializado e restaurado após reiniciar o app.

### Decisão e próximo experimento

- A janela pré-`Resume()` é útil apenas para instrumentação/diagnóstico inicial.
- O backend Android usa contexto e pilha host POSIX para preservar a continuação de fibras; isso reforça o bloqueio de Save/Load em execução.
- Não implementar snapshot copiando bytes de pilha host nem persistindo `ucontext_t` sem contrato explícito e testes de ABI/versão.
- Próxima etapa: projetar um teste isolado, com função recompilada controlada e uma fibra, que faça yield cooperativo em fronteira explícita, registre estado lógico e retome a execução sem reiniciar a função. O teste deve validar round-trip no mesmo processo primeiro; persistência após reinício só pode ser considerada se houver uma estratégia independente de reconstrução.
- Antes de qualquer alteração no SDK, comparar estes trechos com o commit exato fixado no build privado. A leitura desta etapa confirma o desenho do backend POSIX disponível, mas não autoriza assumir que a branch atual do upstream e o commit fixado são idênticos.

Nenhum código de runtime, jogo ou launcher foi alterado. Nenhum Save/Load foi ativado. Não houve compilação nem teste de APK nesta etapa.


## Protótipo isolado de retomada cooperativa de fibra — 2026-11-10

Foi criado um teste experimental, separado do runtime do jogo e da launcher:

- Fonte: `tests/fiber-checkpoint/fiber_checkpoint_test.cpp`.
- Workflow: `.github/workflows/fiber-checkpoint-prototype.yml`.
- O workflow clona o SDK upstream no commit exato fixado `398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb` e compila diretamente o backend real `src/core/fiber_posix.cpp` com o teste, usando `include/rex/thread/fiber.h` do mesmo commit.
- O teste cria uma fibra e chama duas funções C++ aninhadas que simulam uma cadeia de chamadas recompiladas. A função interna faz `Fiber::SwitchTo(main_fiber)`; depois a thread principal volta à fibra e o teste verifica que as variáveis locais das duas pilhas continuam intactas e que a execução prossegue até o fim.
- A verificação esperada é `FIBER_COOPERATIVE_RESUME=PASS`. O teste não serializa `ucontext_t`, não copia pilhas e não tenta restaurar após encerrar o processo.
- O workflow executa em Linux x86-64 com o backend POSIX real. Isso valida a semântica de yield/retomada no host, mas ainda não comprova a execução no Android ARM64 nem a integração com XThread, PPCContext, dispatcher, GPU ou áudio.

### Limite de interpretação

Este protótipo é somente uma prova de que uma fibra POSIX pode suspender e retomar a mesma cadeia C++ no mesmo processo. Ele **não** é um Save State, não gera arquivo de save e não autoriza habilitar os botões Save/Load.

### Próximos passos após o resultado do workflow

1. Confirmar que o workflow realmente executou e ler o resultado/artefato.
2. Se passar, compilar o mesmo teste para Android ARM64 com o NDK e depois executá-lo no aparelho; a compilação cruzada isolada não substitui o teste físico.
3. Só então avaliar uma API de checkpoint cooperativo integrada ao estado PPC e às fibras do kernel. Será necessário coordenar todas as threads e subsistemas; uma única fibra de teste não resolve essa barreira global.
4. Manter Save/Load indisponível até existir um round-trip real, validado e com recuperação de falhas.

Commits desta etapa:
- `7852ee7f1358dad52d3a9759c35b2471a8c287be` — adiciona o teste isolado.
- `16dd10aa955197fd0e460b95db75370260fcae52` — adiciona o workflow.

Nenhum arquivo de jogo, XEX, código de launcher ou runtime de produção foi alterado. O resultado do teste ainda está pendente; nenhum APK foi compilado nesta etapa.

## Resultado verificado do protótipo de fibra e etapa Android ARM64 — 2026-11-10

### Teste Linux x86-64

- Workflow [#42904963200](https://github.com/joaovitoroutlok821-dot/recomp-codeveronica/actions/runs/42904963200), execução #3 de `ReXGlue cooperative fiber checkpoint prototype`, concluído com `success`.
- Commit testado: `515eb95962d2516b7eae8c894aecc78eebb0907e`.
- Job `linux-fiber-roundtrip` passou ao compilar o teste com o backend real `src/core/fiber_posix.cpp` do SDK fixado e executar o binário.
- Saída confirmada: `FIBER_COOPERATIVE_RESUME=PASS`.
- Artefato `recvx-fiber-checkpoint-prototype`, ID `13803624185`, contém o resultado textual de 200 bytes. Não é APK nem binário Android.

### Próxima etapa automatizada

- Commit `d83b9da2b5813bca24518ba413184f1da0f8cdb5` acrescentou ao workflow um job separado `android-arm64-cross-compile`.
- O job instala NDK `27.2.12479018`, compila o mesmo teste e o backend POSIX com o compilador `aarch64-linux-android24-clang++), e verifica que o ELF resultante é AArch64.
- O binário é publicado como artefato `recvx-fiber-checkpoint-android-arm64`.
- Essa etapa é apenas compilação cruzada: não executa o binário no runner Linux nem comprova execução no Motorola. O teste físico no Android continua obrigatório.
- O job Linux permanece separado para preservar a prova executável de round-trip no host.
- A execução deste novo job ainda precisa ser verificada; não presumir sucesso só porque o workflow foi atualizado.

### Limite técnico mantido

- O teste comprova retomada da mesma pilha C++ de fibra no mesmo processo. Não serializa contexto/pilha, não restaura após reinício e não integra XThread/PPCContext, dispatcher, áudio ou GPU.
- Save/Load na launcher permanece sem backend funcional e deve continuar desabilitado/indisponível.
- Nenhum XEX, conteúdo do jogo, código de runtime de produção ou APK foi incluído/alterado nesta etapa.

### Ajuste do runner Android — 2026-11-10

- A primeira execução da nova etapa Android (#42907560724) falhou antes de compilar o teste: `android-actions/setup-android@v3` tentou instalar o pacote legado `tools`, que o repositório atual do SDK não disponibilizou (`Failed to find package 'tools'`).
- O log não apresentou erro de compilação C++ nem erro de `ucontext`; o compilador NDK ainda não foi executado.
- Commit `4b3ac3787cd4d0848fd0a70c74a5c10ce2b91969` removeu essa ação e passou a usar o Android SDK pré-instalado no runner em `/usr/local/lib/android/sdk`, instalando diretamente o NDK `27.2.12479018`.
- A nova execução deve ser consultada antes de considerar o cross-compile concluído. O job Linux de round-trip permanece separado.

- Segunda tentativa Android (#42907697532) falhou no passo de localizar o `sdkmanager`: o caminho fixo `cmdline-tools/16.0/bin/sdkmanager` não existe nessa imagem do runner. O job Linux voltou a passar.
- Commit `7e0e6605a7ece088e273e087b46b762a04cba9d4` substituiu o caminho fixo por descoberta do executável dentro de `cmdline-tools`. A nova execução precisa confirmar se a instalação do NDK e a compilação ARM64 avançam.


## Correção do pipeline de instalação do NDK — 2026-11-10

- A execução [#42907983712](https://github.com/joaovitoroutlok821-dot/recomp-codeveronica/actions/runs/42907983712) confirmou que a descoberta dinâmica do `sdkmanager` funcionou e que o NDK 27.2.12479018 foi baixado e descompactado.
- A etapa falhou depois da extração porque o workflow usa `set -o pipefail`: o `sdkmanager` encerrou a leitura de stdin ao terminar e o processo `yes` recebeu SIGPIPE (exit 141, mensagem `yes: standard output: Broken pipe`). Isso foi um falso negativo do pipeline, não uma falha de download do NDK nem de compilação C++.
- Ajustado o passo para desabilitar `pipefail` somente durante o pipeline `yes | sdkmanager`, mantendo `set -e` para que o status do próprio sdkmanager continue determinando o resultado; `pipefail` é reativado imediatamente depois.
- O job Linux continuou passando. A etapa Android ainda não compilou o teste; aguardar a próxima execução para verificar instalação, compilação AArch64 e inspeção ELF.


## Bloqueio do backend de fibras no Android NDK — 2026-11-10

### Resultado da execução #10

- Workflow [#42908337316](https://github.com/joaovitoroutlok821-dot/recomp-codeveronica/actions/runs/42908337316) terminou com o job Linux `linux-fiber-roundtrip` em `success` e o job Android `android-arm64-cross-compile` em `failure`.
- A correção do pipeline do sdkmanager funcionou: NDK 27.2.12479018 foi instalado, o SDK ReXGlue no commit fixado foi clonado e verificado. Portanto, a falha anterior de instalação foi resolvida.
- A compilação ARM64 parou no backend `src/core/fiber_posix.cpp`: o NDK/Bionic não declara `getcontext`, `makecontext` nem `swapcontext`; os quatro erros são símbolos não declarados, antes da linkedição. Não é erro do teste C++ nem de arquitetura AArch64.
- A documentação do Bionic distingue `sys/ucontext.h`, que fornece tipos/contextos, das funções de troca de contexto; o backend POSIX do SDK depende das três funções que não estão disponíveis na API pública do NDK. Referência técnica consultada: https://android.googlesource.com/platform/bionic/+/c124baa/libc/include/sys/ucontext.h.

### Decisão

- Não tentar resolver isso apenas mudando API level ou adicionando macros: o problema observado é ausência das declarações/implementações públicas requeridas, não somente um protótipo oculto por feature macro.
- Removida temporariamente a etapa de cross-compile Android deste workflow para não manter um job previsivelmente vermelho. O teste Linux continua como prova isolada da semântica do backend POSIX em host.
- O Android precisa de um backend de fibra próprio (por exemplo, troca de contexto AArch64 implementada e revisada em assembly, ou outra biblioteca/abstração compatível e licenciada). Antes de escolher, auditar ABI AArch64, registradores callee-saved incluindo SIMD, alinhamento de stack, TLS de `Fiber::tls_current_`, retorno da trampoline, unwinding e integração com CMake.
- Não copiar nem serializar `ucontext_t`/pilhas como solução de Save State. Um backend de troca de contexto Android funcional só permitirá yield/retomada cooperativa no mesmo processo; ainda não resolve checkpoint persistente, barreira global de threads nem subsistemas GPU/áudio.

### Próximos passos

1. Inspecionar o layout de `Fiber`, a seleção de backend no CMake e as convenções de chamada AArch64 usadas pelo NDK.
2. Projetar backend Android isolado e teste ARM64 de round-trip com variáveis locais aninhadas, registradores preservados e várias trocas; validar execução no Motorola, não apenas cross-compile.
3. Manter Save/Load indisponível até a integração completa provar um round-trip real e seguro.

Nenhum runtime de produção, código do jogo ou launcher foi alterado. Nenhum APK foi produzido nesta etapa.


## Protótipo independente de fibras Android ARM64 — 2026-11-10

- Adicionados `tests/fiber-checkpoint/android/fiber_android_arm64.cpp`, `arm64_context.S` e `fiber_android_arm64_test.cpp` como protótipo isolado, sem integração ao SDK.
- O assembly preserva x19–x30, SP e os 64 bits inferiores de v8–v15; a pilha inicial é alinhada a 16 bytes e a fibra inicia por trampoline C++.
- O teste cobre chamadas aninhadas, endereço de variável local e oito alternâncias cooperativas antes do retorno.
- O protótipo ainda não foi compilado pelo NDK nem executado no Android. Não comprova integração CMake, estabilidade de unwinding/exceções, TLS multi-thread ou persistência/checkpoint.
- Próximo passo: configurar e executar cross-compilação NDK; depois corrigir ABI e preparar teste físico. Save/Load continua desabilitado e a launcher não foi alterada.


## Resultado da primeira cross-compilação Android ARM64 — 2026-11-10

- Workflow: https://github.com/joaovitoroutlok821-dot/recomp-codeveronica/actions/runs/42910240006
- Commit testado: `1c56bef4c9b156e0e8129e8f97f611bd5431dba9`.
- Job `cross-compile`: **success**. NDK `27.2.12479018` compilou os três arquivos do protótipo sem erros com `-Wall -Wextra -Werror`.
- Verificação ELF confirmou `ELF64`, `Machine: AArch64`; o símbolo `rex_fiber_swap` foi encontrado.
- Log confirmou `ANDROID_ARM64_FIBER_CROSS_COMPILE=PASS`.
- Artefato de evidência: `recvx-android-arm64-fiber-prototype`, ID `13807685583`, 2.094 bytes; contém relatório ELF, símbolos e resultado. Não é APK e não foi executado no dispositivo.
- Próxima etapa: construir um APK de teste mínimo que empacote o binário nativo e execute o teste em Android ARM64 real; validar alternâncias repetidas e retorno antes de qualquer integração ao SDK. A cross-compilação sozinha não prova a troca em runtime.


## APK de teste de fibras ARM64 compilado e verificado — 2026-11-10

- Commit do harness: `098cd308953437aae5bf2a3e0c20606dd79443f7`.
- Workflow Android: [execução #42911406508](https://github.com/joaovitoroutlok821-dot/recomp-codeveronica/actions/runs/42911406508), job `build-apk`: **success**.
- Gradle montou o APK debug; a etapa de verificação também passou.
- Verificações concluídas: APK existe e não está vazio; pacote `org.rexglue.fiberprobe`; biblioteca nativa `lib/arm64-v8a/libfiber_test.so` presente; zipalign e apksigner aprovados.
- Artefato: `recvx-android-arm64-fiber-test-apk`, ID `13807526778`, 130.660 bytes, expira em 2026-11-24.
- Link de acesso ao artefato: https://github.com/joaovitoroutlok821-dot/recomp-codeveronica/actions/runs/42911406508
- O APK é um app de diagnóstico independente, sem SDL, sem jogo e sem integração ao runtime de produção. A aprovação do pipeline confirma empacotamento/assinatura, **não** execução bem-sucedida no Motorola.
- Próximo passo: instalar no Motorola Edge 30 Pro, abrir o app e tocar em EXECUTAR TESTE. Registrar exatamente o resultado apresentado ou eventual fechamento. Só considerar o backend validado no dispositivo após observar `ANDROID_ARM64_FIBER_RESUME=PASS`.
- Save/Load permanece desabilitado; launcher e arquivos do jogo não foram alterados.


## Ampliação do teste de fibras Android ARM64 — 2026-11-10

- O teste Android foi ampliado para executar 32 ciclos independentes de criação, alternância e destruição da fibra worker.
- Cada ciclo realiza oito yields para a fibra principal e uma retomada final até o retorno da função: 256 alternâncias cooperativas no total.
- As verificações continuam cobrindo variáveis locais em funções C++ aninhadas, valor preservado, endereço da variável local, sequência de fases e retorno da fibra concluída.
- A fibra principal é convertida uma única vez e liberada ao final; cada worker é destruído somente depois de concluir e devolver o controle.
- O texto de resultado do APK foi atualizado para informar os 32 ciclos e 256 alternâncias.
- Alterações feitas apenas nos arquivos de teste/JNI; não houve integração no runtime, mudança na launcher ou ativação de Save/Load.
- Commit do teste: `c3ac82611bdc9865c2faa60ec1bcdd9e97e0167c`.
- Commit da mensagem JNI: `1376405df5981fa3bb4c2ebc71fb19c6aafa1e68`.
- A nova execução do workflow Android precisa ser verificada. A aprovação da compilação não substitui a execução no Motorola.
- Limite: esta ampliação não constitui ainda um teste explícito de valores artificiais em cada registrador x19–x30/d8–d15, nem valida TLS multi-thread, unwinding, exceções ou integração com XThread/dispatcher. Esses pontos permanecem pendentes antes da integração de produção.
- Save/Load permanece indisponível.


## Teste de estresse Android ARM64 confirmado no Motorola — 2026-11-10

- O usuário executou no Motorola o APK do workflow Android ARM64 #6.
- Resultado visual confirmado: `ANDROID_ARM64_FIBER_RESUME=PASS`.
- Saída exibida: `32 ciclos concluídos; 256 alternâncias.`
- Saída adicional: `Variáveis locais e endereços preservados.`
- Isso confirma o teste de ciclos repetidos de criação, alternância cooperativa, retorno e destruição de workers no dispositivo ARM64 real.
- Workflow #6: `42912702596`, conclusão `success`.
- Artefato APK: `13807912238`, nome `recvx-android-arm64-fiber-test-apk`, SHA-256 `5252a4c51e2d63e5e5bf55351a3f3b4683d417af62600225b9d54b11e937aa3b`.
- Próxima etapa: criar teste explícito de preservação de valores nos registradores callee-saved x19-x30 e d8-d15, usando assembly de teste controlado e verificável. A aprovação atual não prova isoladamente cada registrador.
- Ainda não há integração com o runtime de produção nem suporte Save/Load; não alterar esses estados até validar ABI, TLS, interação com dispatcher/threads e ciclo de vida.


## Teste explícito de registradores ARM64 adicionado — 2026-11-10

- Adicionada rotina assembly `rex_fiber_register_probe` em `tests/fiber-checkpoint/android/arm64_context.S`.
- A rotina salva o estado original do chamador, carrega sentinelas distintas em x19-x29 e nos 64 bits inferiores de d8-d15, cede a execução para a fibra principal e verifica os valores ao retomar.
- A rotina restaura os registradores originais e a pilha antes de retornar, respeitando a ABI da função de teste.
- O worker executa essa prova uma vez em cada ciclo de vida, antes do teste de variáveis locais e das oito alternâncias.
- O JNI informa que o resultado cobre x19-x29 e d8-d15.
- Esta prova testa diretamente os registradores callee-saved especificados pela AAPCS64; x30 é o endereço de retorno da chamada e sua retomada é exercitada pelo fluxo de retorno, não como registrador callee-saved.
- Alterações ainda são exclusivas do APK de diagnóstico; nenhuma integração no runtime de produção e nenhum Save/Load.
- O workflow Android ARM64 precisa compilar e validar o novo APK antes de qualquer teste no aparelho.


## Resultado do APK de teste explícito de registradores ARM64 — 2026-11-10

- O workflow Android ARM64 #13 concluiu com sucesso: https://github.com/joaovitoroutlok821-dot/recomp-codeveronica/actions/runs/42914685645
- Run ID: `42914685645`; commit: `5b4703b79b51b88168984f6c0ab7c65968b9156c`.
- Job `build-apk` ID `130173959425`: `success`.
- Gradle: `BUILD SUCCESSFUL`.
- Verificações do APK passaram: pacote `org.rexglue.fiberprobe`, biblioteca `lib/arm64-v8a/libfiber_test.so`, alinhamento `zipalign` e assinatura `apksigner`.
- Artefato: `recvx-android-arm64-fiber-test-apk`, ID `13808981777`, 131.223 bytes; SHA-256 `c71f05d302c39f463c6d7f498f40a3a9a90ecb0fa814d5e1f828c7b0d06cdf6f`; expira em 2026-11-24T22:28:19Z.
- A revisão do assembly e harness confirmou que a prova carrega sentinelas independentes em x19-x29 e d8-d15, cede para a fibra principal e compara os valores ao retomar. O teste também preserva os registradores originais do chamador antes de retornar.
- **Limite:** o workflow prova compilação, empacotamento ARM64, alinhamento e assinatura; ainda não prova que o teste foi executado no aparelho com esta nova prova explícita. O teste físico anterior de 32 ciclos/256 alternâncias não cobria cada registrador individualmente.
- Próximo passo obrigatório: instalar o APK do artefato #13 no Motorola Edge 30 Pro, abrir `Fiber Probe`, tocar em `EXECUTAR TESTE` e enviar o resultado mostrado. Sucesso esperado: `ANDROID_ARM64_FIBER_RESUME=PASS` com menção a x19-x29 e d8-d15.
- Se falhar ou fechar, capturar logcat do pacote `org.rexglue.fiberprobe`; não integrar o backend ao ReXGlue de produção antes de resolver.
- Save/Load continua desabilitado. Nenhum código do runtime de produção, launcher ou conteúdo do jogo foi alterado.


## Teste físico explícito de registradores ARM64 aprovado — 2026-11-10

- O usuário executou no Motorola Edge 30 Pro o APK de diagnóstico do workflow Android ARM64 #14 (commit `bcb2091`), pacote `org.rexglue.fiberprobe`.
- Resultado mostrado na tela: `ANDROID_ARM64_FIBER_RESUME=PASS`.
- Resultado detalhado: `32 ciclos concluídos; 256 alternâncias.`
- A tela confirma: variáveis locais/endereço e registradores `x19-x29`, `d8-d15` preservados.
- Esta evidência física conclui a validação isolada da troca/retomada cooperativa ARM64 e da preservação dos registradores callee-saved testados no Motorola real.
- A validação **não** demonstra ainda integração com `Fiber`/TLS do SDK ReXGlue, XThread, PPCContext, dispatcher, áudio, GPU, unwinding/exceções, múltiplas threads ou Save State.
- Próxima etapa: auditar novamente o contrato completo da classe `Fiber`, seleção de backend no CMake e uso de `Fiber::tls_current_`; então portar o backend assembly para a estrutura real do SDK em uma branch/commit isolado e criar testes de integração. Não substituir o backend de produção antes de compilar o SDK completo e passar os testes Android e host.
- Save/Load permanece desabilitado. Nenhum código de jogo, launcher ou runtime de produção foi alterado nesta prova.


## Auditoria do contrato Fiber do SDK para Android — 2026-11-10

- Inspecionada a implementação pública atual do SDK `rexglue/rexglue-sdk`: `include/rex/thread/fiber.h`, `src/core/fiber_posix.cpp`, `src/core/CMakeLists.txt`, `include/rex/platform.h` e o CMake raiz.
- A API pública de `Fiber` é pequena e estável: `ConvertCurrentThread()`, `Create(stack_size, entry, arg)`, `SwitchTo(target)`, `Destroy()` e `Current()`; `tls_current_` é um membro estático `thread_local`.
- O backend POSIX atual guarda `ucontext_t`, stack vector, entry/arg e flag de thread-fiber; `ConvertCurrentThread` captura contexto, `Create` configura stack e `makecontext`, `SwitchTo` atualiza TLS antes de `swapcontext`, e `Destroy` limpa TLS apenas para a fibra da thread.
- `REX_PLATFORM_ANDROID` também define `REX_PLATFORM_LINUX`. No CMake atual, `elseif(UNIX)` seleciona `fiber_posix.cpp`; no header, `#if REX_PLATFORM_LINUX || REX_PLATFORM_MAC` inclui `ucontext.h`. Isso explica por que Android cai no caminho POSIX incompatível com Bionic.
- A integração correta requer três mudanças coordenadas: (1) condicionar a inclusão/armazenamento de `ucontext_t` a Linux não-Android/macOS; (2) adicionar um backend Android AArch64 próprio e selecioná-lo antes do bloco POSIX no `src/core/CMakeLists.txt`; (3) manter exatamente a semântica de TLS/ownership da API pública, incluindo retorno da trampoline e destruição apenas fora da fibra ativa.
- O protótipo aprovado no telefone usa uma estrutura/contexto e um TLS próprios, não a classe `rex::thread::Fiber`. Portanto, seu PASS valida a rotina assembly isolada, mas não prova ainda a semântica completa da API do SDK.
- O CMake raiz atual classifica Android como UNIX/Linux e define `REX_PLATFORM_LINUX`; a plataforma Android já é identificada no `platform.h`. Evitar redefinir essa detecção global sem revisar todas as dependências POSIX.
- **Cuidado de versão:** os arquivos acima foram lidos da branch `main` do repositório upstream. O build do projeto fixa o SDK no commit `398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb`; antes de portar qualquer patch, confirmar esses mesmos arquivos no commit fixado e basear o patch exatamente nele. Não aplicar alteração de produção ainda.
- Próxima etapa: criar patch experimental no workflow do projeto contra o commit fixado, compilar primeiro `rexcore`/teste de contrato Fiber para Android e Linux, e executar round-trip real da API `rex::thread::Fiber` no Motorola. Só então considerar integração ao APK do jogo.
- Save/Load continua desabilitado; nenhum arquivo de runtime de produção foi alterado nesta auditoria.


### Refinamento do fluxo de término da fibra — 2026-11-10

- A leitura de `src/kernel/crt/threading.cpp` no commit fixado confirmou que a função real `FiberEntryPoint` já trata o retorno da função guest: ela chama `Fiber::SwitchTo(thread->main_fiber())`; se não houver fibra principal, chama `std::terminate()`.
- Portanto, o campo `return_to` do protótipo Android não deve ser copiado automaticamente para a classe de produção. A volta normal do fiber guest já é responsabilidade do `FiberEntryPoint`/kernel.
- O backend Android precisa manter a mesma semântica do backend POSIX/Win32: `SwitchTo` suspende e retoma; `Destroy` só é permitido fora da fibra ativa; a fibra principal convertida é destruída no encerramento da thread.
- O protótipo isolado tem um trampoline que volta ao contexto de origem ao terminar; isso é um detalhe do harness de teste e não constitui, por si só, requisito para adicionar `return_to` à API pública.
- Antes do patch de produção, adicionar testes de contrato cobrindo: retorno explícito via `SwitchTo(main)`, duas ou mais retomadas, término de `FiberEntryPoint` com retorno à principal, atualização de `tls_current_` antes/depois de cada troca, destruição de fibra suspensa e limpeza da fibra principal na thread proprietária.


### Contrato real de XThread e testes existentes — 2026-11-10

- No commit fixado `398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb`, `XThread::Execute()` chama `Fiber::ConvertCurrentThread()` antes de executar o código guest. O resultado é armazenado em `main_fiber_`, que também é destruído pelo destrutor de `XThread`.
- `ConvertThreadToFiber_entry` reutiliza `thread->main_fiber()`; se estiver nulo, tenta converter a thread naquele ponto. O backend Android deve portanto suportar conversão de thread principal de forma confiável e não criar uma segunda fibra principal inadvertidamente.
- A chamada atual em `XThread::Execute()` não verifica imediatamente se `ConvertCurrentThread()` retornou nulo. O backend deve reportar falha de forma consistente; avaliar separadamente se a camada XThread precisa de tratamento explícito para falha de alocação/conversão.
- O teste unitário existente `tests/unit/core/fiber_test.cpp` cobre apenas duas alternâncias de uma fibra que chama `SwitchTo(main)`. Não cobre múltiplas fibras, retorno da função entry, TLS em cada contexto, criação falha, destruição de fibra suspensa nem conversão/destruição repetida.
- Plano de testes proposto para o backend Android: (1) converter thread e verificar `Current()`; (2) criar fibra e alternar 2+ vezes; (3) alternar entre duas fibras; (4) verificar `Current()` em cada lado da troca; (5) retornar via `SwitchTo(main)` pelo caminho real de `FiberEntryPoint`; (6) destruir fibra suspensa a partir da principal; (7) destruir a fibra principal apenas no encerramento da thread proprietária; (8) testar stacks pequenas/inválidas e falha de alocação.
- A implementação POSIX atual define `uc_link=nullptr`; por isso, não se deve tratar retorno espontâneo da entry como se o contexto principal fosse automaticamente retomado. No fluxo guest real, `FiberEntryPoint` explicitamente volta para `thread->main_fiber()`; testes devem cobrir esse contrato, não presumir um retorno implícito.
- Ainda não foi criado patch de produção nem modificado o SDK upstream. O repositório upstream é somente leitura para a conexão atual. O trabalho permanece na branch experimental/documentação do projeto recomp-codeveronica até existir uma branch gravável do fork do SDK.


### Revisão linha a linha do backend POSIX e requisitos dos testes — 2026-11-10

- Conferido o conteúdo exato do commit fixado para `fiber.h`, `fiber_posix.cpp` e `src/core/CMakeLists.txt`.
- O header só declara o armazenamento de contexto quando `REX_PLATFORM_LINUX || REX_PLATFORM_MAC`; como Android define Linux no SDK, o caminho atual inclui `ucontext.h` e declara `ucontext_t`. O backend Android deve alterar essa guarda para excluir Android sem quebrar Linux desktop/macOS.
- O CMake usa `elseif(UNIX)` e inclui incondicionalmente `fiber_posix.cpp`; a seleção Android AArch64 deve ocorrer antes de `elseif(UNIX)`, para evitar compilar dois backends ou deixar símbolos ausentes.
- `Fiber::SwitchTo` atualiza `tls_current_` antes de `swapcontext`. A implementação ARM64 precisa manter a mesma propriedade: quando o contexto suspenso retomar, o TLS já deve apontar para ele, e o primeiro ingresso na trampoline deve enxergar a fibra recém-ativada.
- `Fiber::Create` POSIX não valida `entry`, stack size, falha de alocação do vetor nem retorno de `getcontext` além do contexto; os testes Android devem definir explicitamente comportamento para entrada nula, stack mínima e falha de alocação, sem introduzir exceções/abortos silenciosos no caminho normal.
- O backend POSIX não implementa retorno automático da trampoline: o fluxo do guest deve voltar explicitamente à fibra principal via `FiberEntryPoint`. A trampoline ARM64 não deve inventar um `return_to` público; deve detectar retorno inesperado e terminar de forma definida, sem continuar em stack inválida.
- Limitação de repositório: a conexão GitHub usada nesta tarefa tem permissão de leitura no upstream `rexglue/rexglue-sdk` e não existe um fork gravável identificado na conta conectada. Por isso, ainda não é possível commitar a alteração do SDK diretamente. A documentação e os testes auxiliares permanecem no repositório recomp-codeveronica; nenhum backend de produção foi alterado.
- Antes do primeiro patch de código, é necessário disponibilizar um fork gravável do SDK ou incorporar o SDK como submódulo/cópia controlada no projeto privado. A partir daí, criar branch experimental, implementar backend e executar testes unitários host + Android no dispositivo.


### Opções ampliadas de resolução na launcher — 2026-11-11

- Atualizado `assets/launcher/index.html` na branch `android-rebuild`, commit `6f2e12bacb9c8a7ae64ae71cb61b8e8a96159a4d`.
- O seletor de resolução agora oferece Automática, 480p (854×480), 540p (960×540), 720p (1280×720), 900p (1600×900), 1080p (1920×1080) e 1440p (2560×1440).
- Os valores existentes foram preservados para compatibilidade com preferências antigas: 720p = 0 e 1080p = 1. Os novos modos usam códigos 2–6.
- A restauração e gravação da escolha no SharedPreferences foram ajustadas para usar os códigos numéricos das opções.
- IMPORTANTE: esta alteração amplia o seletor e persiste a escolha. Ainda não comprova que o ReXRuntime/SDL aplica todas essas resoluções à renderização. A integração efetiva de resolução de saída e resolução interna continua pendente de inspeção do caminho nativo e teste no APK. Não anunciar os modos novos como resoluções já aplicadas pelo jogo.
- Nenhuma alteração foi feita no Save State nem nos arquivos privados do jogo.


### Inspeção do caminho de resolução SDL/ReXGlue — 2026-11-11

- Inspecionado `src/android_main.cpp`: atualmente executa `rex::cvar::Init` e `rex::cvar::ApplyEnvironment` antes de criar `SDLWindowedAppContext`; ainda não lê SharedPreferences nem injeta resolução escolhida.
- Inspecionado o SDK ReXGlue no commit fixado `398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb`.
- `WindowSDL::OpenImpl()` cria a janela via `SDL_CreateWindow`; o tamanho inicial vem de `ResolveWindowWidth/Height`, que consulta cvars `window_width/window_height`, `video_mode_width/video_mode_height` e presets de modo de vídeo. Em Android o código do SDK entra no ramo não-Windows/macOS, usando tamanho físico e SDL.
- `include/rex/graphics/flags.h` declara cvars reais `resolution_scale`, `draw_resolution_scale_x/y`, `vsync` e `async_shader_compilation`. `src/graphics/graphics_system.cpp` usa `REXCVAR_GET(vsync)` no worker de vblank e define `store_shaders=true` para persistência de shaders.
- Isto confirma que existem controles internos reais para escala de resolução, V-Sync e armazenamento de shaders; ainda não confirma que todos aceitam alteração em runtime, nem que o seletor de resolução externa deve ser mapeado diretamente a `resolution_scale`.
- Decisão técnica: separar resolução da janela/superfície Android (a tela física continua sob controle do Android/SDL) de escala interna de renderização do Xenos. Os modos 480p–1440p não devem ser descritos como saída física garantida em um telefone com tela própria.
- Nenhuma alteração nativa foi feita nesta etapa. Próxima investigação: localizar declarações/definições e lifecycle das cvars de janela/GPU no commit fixado, determinar valores permitidos e quando podem ser aplicadas, e verificar como o Android SDL surface/presenter reage a mudanças. Só então conectar as preferências antes de `cvar::Init` ou via mecanismo suportado.


### Confirmação de limites e ciclo de vida das cvars ReXGlue — 2026-11-11

- Inspecionadas definições no SDK fixado:
  - `src/ui/window.cpp`: `video_mode_width` padrão 1280, faixa 640–4095; `video_mode_height` padrão 720, faixa 480–4095; ambas `kRequiresRestart`.
  - A cvar string `resolution` aceita presets como `720p`, `1080p`, `1440p`, `4k` e dimensões explícitas; `kRequiresRestart`.
  - `window_width/window_height` são dimensões lógicas de janela, faixa 0–8192, `kRequiresRestart`; no Android não assumir que equivalem à resolução física da tela.
  - `src/graphics/pipeline/texture/cache.cpp`: `resolution_scale` e escalas X/Y aceitam inteiros 1–8, padrão 1, `kRequiresRestart`. Não mapear percentuais arbitrários da UI diretamente para essa cvar.
  - `src/graphics/command_processor.cpp`: `vsync` padrão true e sem lifecycle explícito (hot reload por padrão); `async_shader_compilation` padrão true e `kHotReload`.
  - `src/graphics/graphics_system.cpp`: `store_shaders` padrão true; ainda precisa confirmar lifecycle e comportamento de persistência antes de expor toggle.
- A UI atual oferece escalas percentuais 50–100%; isso não corresponde diretamente à API inteira 1–8. Precisamos redefinir o significado da escala para opções compatíveis ou implementar uma escala de apresentação separada, se houver suporte.
- Modos 480p/540p/720p/900p/1080p/1440p podem ser expressos como presets de modo de vídeo quando válidos nos limites do SDK, mas a superfície Android pode impor a dimensão física real; validar no dispositivo.
- Nenhuma alteração de código nativo ou APK nesta investigação. Não habilitar opções apenas por terem cvar com nome parecido.



### Investigação da escala interna e da API de configuração — 2026-11-11

- Inspecionado o arquivo completo `src/graphics/pipeline/texture/cache.cpp` no ReXGlue SDK fixado em `398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb`.
- A implementação de `TextureCache::GetConfigDrawResolutionScale()` confirma que `resolution_scale` é um atalho para X e Y, a menos que uma das cvars específicas `draw_resolution_scale_x/y` tenha valor não padrão.
- As três cvars têm faixa mínima 1 e máxima 8, padrão 1, e lifecycle `kRequiresRestart`. Não existe escala inferior a 1 nesses parâmetros.
- No backend Vulkan, as escalas são usadas para multiplicar dimensões de imagens/recursos de resolve marcados como `scaled_resolve`; isso é supersampling/resolução ampliada de recursos específicos, não redução geral da resolução interna. Não mapear 90%, 80%, 70% ou 50% a esses valores.
- A busca no caminho Vulkan não identificou uma cvar de redução global de renderização. O SDK contém um pós-efeito FXAA selecionável por `swap_post_effect`, mas isso não equivale a FSR nem a render scale inferior a 100%.
- API de Cvars confirmada em `include/rex/cvar.h`: `LoadConfig(path)`, `SetFlagByName(name,value)`, `GetFlagByName(name)`, `SaveConfig(path)`, além de lifecycle e validação. `SetFlagByName` registra fonte `kRuntime`; valores `kRequiresRestart` só passam a ter efeito após reinício.
- `src/core/cvar.cpp` confirma que `LoadConfig` lê TOML. `src/ui/rex_app.cpp` carrega o TOML do aplicativo durante `OnInitialize`, depois da inicialização inicial das Cvars. O projeto Android pode fornecer configuração em arquivo no diretório privado antes desse ponto ou aplicar cvars apropriadas antes da criação da janela/runtime, mas a ordem e a precedência precisam ser preservadas.
- `src/android_main.cpp` atual chama `cvar::Init` e `ApplyEnvironment`, mas não chama `LoadConfig` explicitamente e não consome SharedPreferences. A bridge Java salva valores em `recvx_settings`, porém a launcher só envia atualmente resolução, FPS e controles de toque, e `loadSettings()` só devolve esses três campos.
- Próximo passo: definir uma ponte segura entre as preferências Android e o TOML/Cvar registry, com validação por nome/tipo/lifecycle e logs dos valores efetivamente aceitos. Não gravar chaves arbitrárias da UI diretamente como cvars.
- Priorizar primeiro opções com suporte comprovado: `vsync`, `async_shader_compilation`, `store_shaders` e modo de vídeo. Verificar lifecycle e persistência de `store_shaders` no commit fixado antes de habilitar a opção.
- Escala interna percentual permanece pendente: ou localizar/implementar um mecanismo real de redução no caminho de apresentação/renderização, ou ajustar a UI para não oferecer percentuais que o runtime não consegue cumprir. Não usar `draw_resolution_scale_x/y` para esse fim.
- Nenhum código de produção foi alterado nesta investigação; nenhum APK foi compilado. O jogo, launcher e Save State permanecem intocados.


### Primeira integração de opções GPU da launcher — 2026-11-11

- A auditoria do SDK fixado \`398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb\` confirmou as cvars \`vsync\` e \`async_shader_compilation\` em \`src/graphics/command_processor.cpp\`.
- \`vsync\` é declarado com padrão true; o código consulta essa cvar no worker de sincronização vertical. Não há lifecycle explícito, portanto o valor de inicialização é a via conservadora.
- \`async_shader_compilation\` é declarado com padrão true e lifecycle \`kHotReload\`; controla a compilação assíncrona de shaders/pipelines.
- O parser de Cvars do SDK aceita flags booleanas \`--nome\` e \`--no-nome\`. A Activity agora passa as preferências \`vsync\` e \`async_shader_compilation\` como argumentos nativos no início do jogo.
- A bridge Java restaura também essas duas preferências, e o reset define ambas como true.
- A launcher habilita os controles de V-Sync e compilação assíncrona, salva seus valores no SharedPreferences e restaura os valores ao abrir a aba correspondente. A gravação continua parcial por aba, mas o SharedPreferences preserva chaves não enviadas, evitando apagar escolhas de outras abas.
- **Ainda não validado em APK/aparelho:** é necessário compilar o APK privado, verificar os logs do parser/runtime e testar V-Sync ligado/desligado e compilação assíncrona. Não afirmar que a opção está confirmada em execução até esse teste.
- As opções de cache de shaders, FPS cap, FSR, escala de renderização, áudio e controles avançados continuam sem implementação real e permanecem desativadas.
- Nenhum arquivo de jogo, XEX ou código gerado privado foi copiado para o repositório público. Save State continua fora deste trabalho.


### Auditoria do suporte existente a Save State no ReXGlue — 2026-11-11

- A compilação completa do fork ReXGlue SDK para Android ARM64 foi concluída com sucesso no workflow [#42954638794](https://github.com/joaovitoroutlok821-dot/rexglue-sdk/actions/runs/42954638794), branch `android-arm64-fiber-experiment`, commit `6d05ac09fcf1e5be378dcc8979014a1a9473a48f`.
- O workflow concluiu configuração, compilação, instalação, empacotamento e publicação do artefato `rexglue-sdk-android-arm64`, ID `13826314819`. O ZIP foi baixado e sua integridade foi conferida. Isto valida o pacote SDK, não a integração com o APK de Resident Evil.
- Auditoria do código do SDK no branch experimental encontrou infraestrutura de serialização já existente:
  - `rex::system::memory::Memory::Save/Restore` serializa/restaura os heaps de memória do guest.
  - `BaseHeap::Save/Restore` percorre a tabela de páginas e grava/restaura conteúdo das páginas comprometidas.
  - `KernelState::Save/Restore` grava/restaura a tabela de objetos, threads guest e objetos serializáveis do kernel.
  - `XThread::Save/Restore` contém estrutura de estado com metadados de thread e contexto PPC (GPR, FPR, VR, CR, FPSCR, XER etc.).
- Bloqueio crítico confirmado: `XThread::Save` retorna false para thread guest em execução, com log explícito de serialização não implementada. O caminho `XThread::Restore` para thread marcada como running cria uma thread suspensa, mas o callback de execução ainda emite `Thread restore not implemented` e não retoma o contexto salvo. Portanto, o suporte existente não permite ainda um Save State completo e retomável de uma partida ativa.
- A serialização do kernel percorre objetos e threads; ainda não foi demonstrado um ponto de pausa global/consistente que impeça CPU, threads, GPU e áudio de alterarem o estado durante a captura.
- A fibra ARM64 já compila no SDK, mas o contexto host da fibra (SP, registradores callee-saved e stack) não é persistido por `XThread::Save`. O teste de retomada de fibra em processo não equivale a persistência de Save State entre execuções.
- Plano técnico: (1) localizar o ciclo de vida do Runtime e mecanismo de serialização no SDK fixado; (2) definir barreira de pausa/snapshot consistente; (3) completar captura/restauração de contexto e stacks sem persistir ponteiros/handles host inválidos; (4) auditar objetos de kernel e dependências GPU/áudio/input para serialização ou recriação; (5) implementar arquivo versionado, validado e gravado atomicamente no armazenamento privado Android; (6) conectar os botões Save State/Load State e validar salvar, fechar, reabrir e restaurar.
- Nenhum código de produção do jogo, launcher ou Save State foi alterado nesta auditoria. Os botões não devem ser anunciados como funcionais ainda. A versão do jogo que já funciona deve ser preservada.


### Investigação do ponto de pausa e captura de threads — 2026-11-11

- Inspecionado `src/system/runtime.cpp` e `include/rex/runtime.h`: o objeto `Runtime` mantém `memory_`, `kernel_state_`, `graphics_system_`, `audio_system_`, `input_system_` e `function_dispatcher_` como subsistemas separados. A API pública atual expõe `Setup`, `Shutdown`, `LoadXexImage`, `PrepareModuleLaunch` e `LaunchModule`, mas não expõe `SaveState`, `RestoreState` nem uma operação de pausa global.
- `Runtime::Shutdown()` encerra GPU, áudio e input e destrói o kernel; não é um mecanismo seguro de pausa/snapshot e não pode ser usado como substituto.
- `KernelState::Save()` já serializa object table, threads guest e objetos kernel, mas chama `XThread::Save()` enquanto itera os objetos. Não há, nesse caminho, uma barreira que suspenda todos os threads e mantenha o snapshot consistente.
- `XThread::Suspend()` incrementa o suspend count e chama a suspensão do host thread. Isso não resolve por si só a captura segura do contexto: a implementação atual de `XThread::Save()` rejeita qualquer thread com `running_ == true`, e o caminho de restore de thread running ainda termina em `Thread restore not implemented`.
- `KernelState::TerminateTitle()` é apenas encerramento cooperativo: sinaliza terminação, acorda waiters e espera threads saírem. Não deve ser reutilizado para Save State.
- A implementação de `XThread::Save()` contém um ramo que tentaria salvar contexto quando running, mas esse ramo é atualmente inalcançável devido ao retorno antecipado. Além disso, define `pc = 0` e grava esse valor como PC; portanto, simplesmente remover o retorno antecipado seria incorreto e perderia o ponto real de execução.
- Decisão: antes de alterar `XThread::Save/Restore`, projetar um protocolo de safepoint cooperativo para threads guest, que capture o contexto PPC em um ponto seguro e mantenha a thread parada até terminar o snapshot. Em seguida, definir tratamento para threads bloqueadas em waits/APCs, stacks guest, TLS, fibras e estado de scheduler. Suspensão forçada do host thread não será considerada suficiente sem captura/validação de contexto host e garantia de que não há locks host mantidos.
- Ainda falta auditar as APIs de memória e os estados GPU/áudio/input no commit exato usado pelo projeto. Não foi feita alteração de código de produção nem APK nesta etapa; nenhuma promessa de Save State funcional.
