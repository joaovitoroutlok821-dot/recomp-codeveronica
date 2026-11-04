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
