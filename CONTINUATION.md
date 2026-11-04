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
