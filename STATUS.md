# Status

## Reconstrução isolada Android — 2026-11-04

- Repositório de trabalho: `joaovitoroutlok821-dot/recomp-codeveronica`.
- Branch de reconstrução: `android-rebuild`.
- Base: `main` no commit `8da26ce9542c252ea24babafd3f3cf53dbf3eb75`.
- Plano detalhado: [ANDROID_REBUILD_PLAN.md](ANDROID_REBUILD_PLAN.md).
- A branch foi criada e verificada; a branch `main` não foi alterada.
- Ainda não foi produzido APK nesta branch.
- O utilitário local de inspeção XEX e a documentação não armazenam nem imprimem o hash do arquivo do jogo.
- O repositório de destino não apresenta execuções de Actions anteriores (API retornou zero runs); resultados históricos mencionados abaixo pertencem ao repositório anterior e são apenas referência documental, não artefatos disponíveis neste repositório.

## Fase atual

**Fase 2 — primeiro build do APK mínimo SDL/JNI.**

Concluído na branch `android-rebuild`:
1. Criada a branch isolada a partir de `main`, sem modificar a branch principal.
2. Criado `ANDROID_REBUILD_PLAN.md` e atualizado o registro de continuidade.
3. Endurecido `scripts/install-android-game-setup.py`: estimativa recursiva do tamanho, margem de espaço livre, verificação durante a cópia, progresso, limpeza de cópia temporária em falha e exigência de `Default.xex` na raiz.
4. Criado `android-smoke/SmokeTest.c`, um teste SDL3 de tela cheia que alterna cores e registra os erros de inicialização.
5. Criado `.github/workflows/android-smoke-test.yml`, que compila um APK debug ARM64 com SDL 3.5.0 fixado e verifica `libmain.so`, `libSDL3.so`, package ID, alinhamento, assinatura e ausência de arquivos de jogo.

Próximas tarefas:
1. Obter a primeira execução do workflow `RECVX Android SDL-JNI smoke test` e corrigir qualquer falha de build/empacotamento.
2. Confirmar o APK de diagnóstico e testar abertura/superfície SDL no Motorola Edge 30 Pro.
3. Só depois integrar codegen host e compilação do alvo `recvx` com NDK ARM64.
4. Validar o conteúdo do APK final e garantir que não contém o XEX.

## Histórico técnico preservado

## Verified target facts

- Title ID: `43430822`
- Media ID: `58A6EFFB`
- Internal module string: `Bio_cv.exe`
- ReXGlue baseline: `0.10.0-dev.g398e2ba`

## Android ARM64 SDK compile verified (2026-10-29)

GitHub Actions run [40925144992](https://github.com/marcussilvacastrooutlok-afk/recomp-codeveronica/actions/runs/40925144992), commit `ef6f1a3f71fd1b180fdaec759d52a280325bb142`, completed the Android NDK build. The archived `compile_commands.json` proves the compiler target is `aarch64-none-linux-android26` and the compile definitions include `REX_PLATFORM_ANDROID=1`; this is not a Linux ARM64 build mislabeled as Android.

The build log reached step 790/791 and linked at least:
- `librexruntime.so`
- `librexgpu-xenos.so`
- Android ARM64 `rexglue` executable

This is an SDK-level milestone only. The artifact contains logs and build metadata, not the compiled binaries. It does **not** yet prove that the game-specific `recvx` target links for Android, that the SDL Activity lifecycle and Vulkan surface work on-device, that an APK is packaged, or that the game renders.

### Remaining Android work

1. Build the title-specific generated C++ target for `arm64-v8a` against the Android SDK build.
2. Validate every shared-library dependency and package SDL Java/JNI plus the native libraries into an APK.
3. Verify Android Activity lifecycle, Vulkan surface creation/resume/pause, and storage access.
4. Install and launch on the user's Android device; then test rendering, audio, and controls separately.

## Local XEX verification

The user verified the local game file on an Android/Termux device on 2026-10-21:

- File: `Default.xex`
- Size: `13774848` bytes
- Header: `XEX2`
- ASCII module references: `Bio_cv.exe`, `xam.xex`, `xboxkrnl.exe`

The retail XEX is intentionally not committed to this repository. This identity check does not demonstrate Android gameplay.

## Linux code generation and native build verified (2026-10-25)

The Linux diagnostic completed successfully with the same locally verified XEX identity. It generated and compiled 214 title-specific C++ compilation units, linked the Linux x86-64 executable `recvx`, and staged `librexgpu-xenos.so` and `librexruntime.so`. This does not confirm Android compatibility or gameplay.

## Historical Android blocker (2026-10-25)

The earlier run [40219955322](https://github.com/marcussilvacastrooutlok-afk/recomp-codeveronica/actions/runs/40219955322) selected `linux-arm64` despite use of the Android NDK and was correctly rejected. That blocker is superseded by the successful Android ARM64 compile in run 40925144992. The old run must not be treated as the current platform result.

## Not yet verified

- Android title-specific `recvx` shared-library link
- APK packaging and install
- guest entrypoint execution on Android
- rendered frame
- audio correctness
- controller input
- gameplay



## Commits da reconstrução

- Plano e branch: `2983c5f13cfd02e1c171eaa1a1661ecd9bdad3fd`.
- Atualização de continuidade/status: `dbc0a8db7047e01fa772bb512845aeab401d8119` e `b64882531b7da264e6fd6f1418c9751aab838eb4`.
- Correção SAF: `b920f8d332940841c29872267f58bc9fc3f69e72`.
- Smoke test e workflow: `651ee75952c711c02d636c1bda7549a9f5c65cd5`, `4912a133057c2ba3f84eb210574682f2470ff62e`, `db4d433937a894673b65b70a16a330d797838610`, `3346889c3113cde7244fe652771e341d8268ae6f` e `6624918613acbe4dd1e56919913b4cc07a8799ff`.

**Execução do workflow:** a consulta à API de Actions retornou zero execuções neste repositório até a última verificação. O primeiro build ainda precisa ser iniciado/confirmado na aba Actions. Portanto, o APK ainda não foi compilado; a criação do workflow não deve ser confundida com um build concluído.

- Última branch head verificada: `5cb52baf68029553665e20d3c97db92f8eca8524`.
- `main` verificada sem alterações: `8da26ce9542c252ea24babafd3f3cf53dbf3eb75`.
