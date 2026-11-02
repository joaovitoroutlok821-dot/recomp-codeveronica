# CONTINUIDADE DO PROJETO — Resident Evil Code Veronica X

Última atualização: 2026-11-01

Este arquivo registra o estado técnico confirmado para que outro chat ou colaborador possa continuar sem repetir etapas. Leia antes de alterar o projeto.

## Objetivo

Construir uma versão Android ARM64 em APK da recompilação nativa de Resident Evil Code Veronica X com ReXGlue/ReXRuntime. Não é um emulador. O aplicativo deve iniciar no Android e permitir localizar os arquivos do jogo no armazenamento do aparelho.

## Ambiente do usuário

- O usuário trabalha somente pelo celular Android (Motorola Edge 30 Pro, Android 13, Snapdragon 8 Gen 1).
- Usa Termux, ADB e GitHub Actions; não possui computador.
- Não pedir para reinstalar o conector GitHub nem repetir configurações já concluídas.
- Ao receber “Ok”, interpretar como autorização para continuar, sem pedir confirmação a cada etapa.
- Instruções no dispositivo devem ser compatíveis com Termux/Android.

## Repositório e conta

- Repositório: https://github.com/marcussilvacastrooutlok-afk/recomp-codeveronica
- Conta GitHub: marcussilvacastrooutlok-afk
- Manifesto: `recvx_manifest.toml`
- Código de entrada: `src/main.cpp`
- Fontes gerados: `generated/default/`

## Arquivo do jogo — informação privada

O usuário informou que o arquivo está no aparelho em:

`Download/Xbox360 Emulador/Jogos/RE Code Veronica X HD Dub PT-BR/Default.xex`

Dados verificados anteriormente:
- Nome: `Default.xex`
- Tamanho: 13.774.848 bytes
- Cabeçalho: `XEX2`
- Módulo: `Bio_cv.exe`
- Title ID: `43430822`
- Media ID: `58A6EFFB`

O jogo é um arquivo privado do usuário. **Não solicitar reenvio sem necessidade e nunca fazer commit do XEX, de seu hash ou de conteúdo protegido no repositório/artefatos públicos.** O manifesto usa `game/Default.xex` como entrypoint local, mas o arquivo não precisa ser versionado no Git.

## Estado confirmado do projeto

- Codegen do projeto foi concluído em workflow de diagnóstico.
- O workflow `41362868169` (`Resident Evil codegen diagnostic`) terminou com sucesso no commit `5c6fa1f45916172d5104580728f00df2216033c5`.
- O workflow `41362868165` (`Validate repository`) também terminou com sucesso no mesmo commit.
- Artefato de diagnóstico: `recvx-codegen-diagnostics.zip`, com aproximadamente 67 MB e 429 entradas. Contém fontes C++ gerados em `generated/default/`, `sources.cmake` e resultados Linux host.
- Codegen/build Linux host anterior compilou 214 unidades C++ e vinculou o executável `recvx` para Linux x86_64.
- Um probe do SDK para Android ARM64, workflow `40925144992`, commit `ef6f1a3f71fd1b180fdaec759d52a280325bb142`, terminou com sucesso. Verificou a branch de plataforma Android e vinculou bibliotecas Android ARM64 `librexruntime.so`, `librexgpu-xenos.so` e o executável `rexglue`.
- Esse probe é apenas validação do SDK/plataforma: **não prova que as fontes geradas específicas de Resident Evil foram compiladas para Android nem que existe APK**.
- Ainda não há APK Android de Resident Evil confirmado.

## Configuração técnica relevante

`recvx_manifest.toml`:
- Projeto: `recvx`
- SDK: `0.10.0`
- `game_root = "game"`
- Entry point: `game/Default.xex`
- Output: `generated/default`
- Há correções manuais de funções/switches no manifesto; não sobrescrever ou remover sem análise.

`CMakeLists.txt` atual:
```cmake
cmake_minimum_required(VERSION 3.25)
project(recvx LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
include(generated/rexglue.cmake)
set(RECVX_SOURCES src/main.cpp)
if(WIN32)
  add_executable(recvx WIN32 ${RECVX_SOURCES})
else()
  add_executable(recvx ${RECVX_SOURCES})
endif()
rexglue_setup_target(recvx GPU_PLUGINS xenos)
```

`src/main.cpp`:
```cpp
#include "generated/default/recvx_init.h"
#include "recvx_app.h"
REX_DEFINE_APP(recvx, RecvXApp::Create)
```

## Bloqueio técnico principal

O build atual `build.sh` é orientado a host Linux:
- verifica dependências Linux/Clang e bibliotecas desktop;
- compila SDK e CLI host;
- executa codegen no host;
- compila e vincula `recvx` para Linux;
- prepara bibliotecas Linux.

Ele não é um fluxo Android direto.

`generated/rexglue.cmake`:
- procura `rexglue 0.10.0`, salvo quando `REXSDK_DIR` é definido;
- inclui `generated/sources.cmake`;
- cria uma OBJECT library `${target_name}_recomp` com os fontes gerados e liga `rex::runtime`;
- adiciona dependência `recvx_codegen`, que chama o executável host `rex::rexglue` com `codegen recvx_manifest.toml`.

Para Android, o codegen deve continuar executando com o CLI Linux host. Depois, as fontes específicas do jogo devem ser compiladas com o Android NDK e ligadas às bibliotecas Android do SDK. Não tentar executar um `rexglue` compilado para Android como ferramenta de codegen no host.

Scripts existentes:
- `scripts/ensure-rexglue-android-platform.py`: adapta suporte da plataforma Android e superfície nativa SDL.
- `scripts/ensure-rexglue-android-thread-compat.py`: adapta TimerQueue de `jthread` para `thread`/flag atômica de parada.

Ambiente Android validado no probe:
- Android NDK 27.2.12479018
- CMake 3.31.6
- Android platform 35
- SDK API 26
- `REX_PLATFORM_ANDROID=1`

## Próximas etapas

1. Inspecionar os workflows atuais em `.github/workflows/`, os scripts Android existentes e os arquivos exportados pelo SDK.
2. Entender como o SDK exporta/importa os targets CMake `rex::runtime`, GPU Xenos e SDL para Android. Não presumir nomes/paths sem verificar.
3. Separar claramente duas fases: (a) codegen executado pelo CLI Linux host; (b) compilação/link das fontes `generated/default/` para `arm64-v8a` usando NDK e bibliotecas Android do SDK.
4. Criar ou adaptar workflow Android específico para compilar o alvo de jogo e preparar os `.so` necessários.
5. Empacotar um APK real: Activity/SDL Java, JNI e bibliotecas nativas ARM64, permissões/acesso ao armazenamento e ciclo de vida/superfície Android.
6. Validar que o APK contém as bibliotecas corretas e instalar/testar no telefone do usuário.
7. Só então investigar erros de execução/renderização/áudio/controles com logs do aparelho.

## Regras para continuar

- Não declarar que há APK enquanto não houver artefato APK confirmado.
- Sucesso do codegen ou do probe do SDK não equivale a um port Android completo do jogo.
- Não alterar cegamente o manifesto nem remover as correções manuais existentes.
- Não incluir o XEX ou seus dados privados em commits ou artefatos públicos.
- Registrar neste arquivo os novos commits, workflows, artefatos, testes e próximos passos sempre que o estado mudar.


## Registro de continuidade — 2026-11-02

### Verificação adicional do fluxo Android

- O workflow `Validate repository` disparado pelo commit de continuidade `80fbb979f9457c44ea9741d57f8fe14b72901a31` concluiu com sucesso (run `41375023157`).
- O workflow `codegen-diagnostico.yml` continua sendo a etapa de geração host; não é um builder de APK.
- O `CMakeLists.txt` do jogo continua usando `rexglue_setup_target(recvx GPU_PLUGINS xenos)`.
- O arquivo `generated/rexglue.cmake` mostra que o alvo `recvx_recomp` compila os fontes de `generated/default/sources.cmake`, liga `rex::runtime` e depende do alvo host `recvx_codegen`. O codegen chama `rex::rexglue` com `recvx_manifest.toml`.
- A configuração gerada atual não oferece, por si só, um APK: é necessário separar o executável host de codegen da compilação NDK do jogo e do empacotamento Android/SDL.
- O workflow de probe Android existente aplica patches locais ao SDK antes do CMake; ele é prova de compatibilidade do SDK, não de compilação do título.
- A árvore do repositório contém `scripts/ensure-rexglue-android-content-uri.py`, que instala uma ponte JNI para abrir URIs via Android ContentResolver. Isso é uma base técnica para o seletor de pasta/arquivos, mas ainda precisa ser integrada e testada na Activity/SDL do APK.
- Nenhuma alteração de código de runtime ou workflow de APK do Resident Evil foi feita nesta revisão. Nenhum APK foi produzido.

### Próximas ações registradas

1. Inspecionar os alvos exportados pelo SDK (runtime, Xenos/Vulkan, SDL e dependências) a partir dos artefatos do probe, sem presumir nomes de bibliotecas.
2. Criar workflow de Android ARM64 em duas fases: codegen host Linux usando o XEX temporário privado; compilação das fontes geradas com NDK; empacotamento SDL/Java/JNI.
3. Integrar o acesso ao jogo por Storage Access Framework/ContentResolver. Não embutir `Default.xex` no APK nem em artefatos públicos.
4. Validar bibliotecas, ABI, assinatura e conteúdo do APK antes de disponibilizá-lo para instalação.
5. Atualizar este arquivo em cada alteração, commit, execução, artefato ou teste.

### Pac-Man — acompanhamento cruzado

- Em 2026-11-02, run `41375019134` estava em andamento. Codegen e configuração Android ARM64 concluídos; etapa `Compilar codigo gerado para Android (ARM64)` em andamento; empacotamento e upload ainda pendentes.
- A revisão do workflow Pac-Man identificou que ele copia `default.xex` para `android-package/app/src/main/assets/game/default.xex`. Não usar esse APK como versão final enquanto esse comportamento existir.
- A revisão da árvore pública do Pac-Man confirmou que há um `default.xex` versionado no repositório público (8.970.240 bytes). Não foi feita alteração de visibilidade nem remoção do arquivo nesta etapa.


## Registro de continuidade — 2026-11-02 (validação e revisão SDK)

### Validação do repositório

- Run `41376034688` (`Validate repository`), commit `1fe538411cbf24794b78ed6aece59b29467643bc`: conclusão `success`.
- As verificações de scripts Python, shell, referências dos helpers, manifesto e regras de segurança passaram.
- Isso valida o repositório; não compila o jogo para Android e não produz APK.

### Verificação da plataforma SDK

- O `CMakeLists.txt` da revisão fixada do ReXGlue (`398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb`) detecta explicitamente Windows, Linux e macOS, e termina com erro para outras plataformas: `Unsupported platform. ReXGlue supports Windows, Linux, and macOS only.`
- O projeto define `REX_PLATFORM` e macros globais antes de incluir componentes CMake. Portanto, a compilação Android depende dos patches de plataforma já existentes no probe; não basta passar somente `-DANDROID_ABI=arm64-v8a` ao CMake.
- O script `scripts/ensure-rexglue-android-content-uri.py` adiciona uma função JNI que usa SDL Android JNI Environment/Activity e `ContentResolver.openFileDescriptor()`, detachando o file descriptor. **O script, por si só, não implementa o seletor SAF na Activity, não guarda permissões URI persistentes e não liga automaticamente essa função ao caminho de abertura usado pelo jogo.** Também requer revisão de compilação/integração antes de ser considerado funcional.
- Nenhum workflow de APK Android do Resident Evil foi criado ou executado nesta revisão; nenhum APK foi produzido.

### Próximas ações

1. Revisar todos os patches Android aplicados no probe e os targets CMake/exportados reais do SDK (runtime, Xenos/Vulkan, SDL e dependências).
2. Separar codegen Linux host e compilação ARM64 NDK, contornando de forma explícita a detecção upstream que não inclui Android.
3. Integrar SAF ponta a ponta na Activity/SDL, persistindo URI permission e ligando a URI/file descriptor ao filesystem do ReXGlue.
4. Garantir que o XEX privado seja usado apenas temporariamente para codegen, sem commit ou inclusão no APK/artefato.
5. Criar workflow Android apenas depois de identificar e validar targets e bibliotecas; validar ABI, conteúdo e assinatura do APK antes de solicitar teste no telefone.
6. Atualizar este registro a cada alteração, commit, run, artefato e teste.

### Acompanhamento Pac-Man

- O run `41375019134` concluiu com sucesso e publicou o artefato `pacman-android-apk`.
- Inspeção do APK confirmou XEX em `assets/game/default.xex` (8.970.240 bytes), portanto esse artefato não atende ao requisito de selecionar os arquivos do jogo no armazenamento e não deve ser tratado como versão final.
- O workflow também ainda não incorpora o seletor SAF. Ver detalhes e próximos passos no `CONTINUATION.md` do repositório RecompPacman.
