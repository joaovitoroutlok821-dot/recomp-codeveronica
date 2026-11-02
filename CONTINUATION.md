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


## Evidência adicional do probe Android — artefato inspecionado em 2026-11-02

O artefato real do run `40925144992` foi baixado e inspecionado (não apenas inferido pelo status do workflow):

- ZIP: `recvx-android-arm64-probe`, 910 entradas.
- Resultado interno: `Android ARM64 SDK compilation: SUCCESS`.
- O log Ninja chegou a 791 tarefas; compilou o backend Vulkan/Xenos e linkou:
  - `.deps/rexglue-sdk/out/android-arm64/librexgpu-xenos.so`
  - `.deps/rexglue-sdk/out/android-arm64/librexruntime.so`
  - `.deps/rexglue-sdk/out/android-arm64/rexglue` (CLI ARM64; não usar como codegen host).
- A árvore Ninja também contém o alvo `SDL3-static`; portanto o probe não demonstra a existência de uma `libSDL3.so` pronta para copiar. O pacote SDL Android deve ser construído/integrado separadamente, como feito no workflow Pac-Man.
- O SDK Android ARM64 foi efetivamente compilado no probe; isto é mais forte que uma simples configuração CMake, mas ainda não compila as fontes `generated/default` do Resident Evil e não cria APK.
- Artefato de origem: run `40925144992`, artifact ID `12920314229`, commit `ef6f1a3f71fd1b180fdaec759d52a280325bb142`.

### Decisão para o futuro workflow APK

- Usar o executável `rexglue` Linux x86_64 produzido/instalado na fase host para gerar `generated/default`.
- Compilar o alvo do jogo com NDK ARM64 e ligar às bibliotecas Android efetivamente produzidas pelo SDK, incluindo runtime e Xenos.
- Não copiar a CLI `rexglue` Android para o lugar da ferramenta de codegen host.
- A biblioteca SDL Android e o carregamento das dependências transitivas ainda precisam ser verificados no APK final.


## Decisão de arquitetura de seleção dos arquivos — 2026-11-02

O usuário confirmou, com base em outros jogos recompilados que já utilizou, que selecionar a pasta do jogo pode consumir armazenamento interno aproximadamente equivalente ao tamanho dos arquivos selecionados. Adotar esse comportamento como referência para Pac-Man e Resident Evil.

### Estratégia preferida

- Abrir o seletor de diretório do Android (Storage Access Framework / `ACTION_OPEN_DOCUMENT_TREE`).
- Solicitar e persistir a permissão de leitura da URI escolhida.
- Copiar recursivamente a árvore selecionada para uma pasta privada do aplicativo, preservando subpastas e nomes necessários ao jogo.
- Exibir progresso e erros; verificar espaço disponível antes e durante a cópia e não iniciar o runtime se a preparação falhar.
- Reutilizar a cópia preparada em inicializações seguintes, com opção futura de trocar/repreparar a pasta.
- Passar ao ReXGlue um caminho POSIX privado normal como `--game_data_root`, evitando depender de URIs `content://` no filesystem POSIX atual.
- Manter a tela/configurações do aplicativo acessíveis mesmo sem dados do jogo; só iniciar SDL/runtime quando os dados estiverem preparados.
- Nunca embutir o `Default.xex` privado do usuário no APK, commit ou artefato público.

### Verificação Android/SDL

- O manifesto do SDL 3.5.0 no commit fixado `8bf3b7215ad9fc3deb583c6a3a37c6c67f2e24e4` declara `SDLActivity` como única Activity LAUNCHER. A integração precisará adicionar uma Activity de configuração/seleção como launcher e iniciar SDLActivity após a preparação, ou implementar fluxo equivalente sem quebrar o ciclo de vida SDL.
- O helper `ensure-rexglue-android-content-uri.py` atual só injeta uma ponte JNI para ContentResolver; não implementa o seletor, a persistência de permissão, a cópia da árvore nem a integração com o filesystem. Não considerá-lo uma implementação SAF completa.
- A cópia para armazenamento privado é a estratégia preferida por ser compatível com as operações POSIX `open/fopen/stat/opendir` observadas no filesystem atual do SDK. Ainda requer implementação e testes de cópia recursiva, cancelamento, espaço insuficiente, falhas de I/O, retomada e detecção de dados já preparados.
- Nenhum código de seleção/cópia foi implementado nesta atualização; nenhum APK foi produzido.

### Próximos passos

1. Implementar e testar um componente Android reutilizável de seleção SAF + cópia recursiva + verificação de espaço/progresso.
2. Integrar a Activity de configuração ao pacote SDL, mantendo as configurações acessíveis sem XEX.
3. Só depois ligar o caminho privado preparado ao argumento `--game_data_root` e ao fluxo de inicialização do runtime.
4. Atualizar o workflow Android do Resident separando codegen host, compilação NDK e empacotamento SDL.
5. Registrar neste arquivo commits, runs, artefatos e resultados de testes; não incluir o XEX privado.


## Implementação inicial do seletor e preparação dos arquivos — 2026-11-02

- Commit `6692f86c289d6df475ec2651b84e93448f93876a`: adicionado `scripts/install-android-game-setup.py`.
- O script instala duas Activities Java no projeto Android do SDL:
  - `GameSetupActivity`: tela inicial, seletor de diretório via `ACTION_OPEN_DOCUMENT_TREE`, persistência da permissão de leitura, cópia recursiva para `files/game` e verificação de `Default.xex` na raiz.
  - `GameSDLActivity`: subclass de `SDLActivity` que fornece `--game_data_root=<caminho privado>` por `getArguments()`.
- O script altera o AndroidManifest para que a tela de preparação seja a launcher e a Activity SDL seja aberta somente após a cópia.
- A cópia é feita em `game.new`; a pasta anterior é preservada em `game.old` até a nova cópia ser renomeada para `game`. Em caso de falha na substituição, tenta restaurar a cópia anterior.
- Esta alteração é apenas o instalador/integração do seletor. Ainda não foi ligada a um workflow de APK, nem compilada, instalada ou testada em dispositivo.
- Limitações ainda a resolver antes de considerar a funcionalidade pronta: cálculo prévio confiável de espaço/tamanho, progresso de cópia mais informativo, reutilização da cópia quando a pasta já selecionada não mudou, nomes de entrada alternativos/capitalização, cancelamento de cópia, e testes de compilação Java/Manifest com o SDL fixado.
- Nenhuma compilação de APK foi iniciada por este commit. A validação automática do repositório pode executar verificações estáticas, mas não compila o APK.


## Registro de continuidade — 2026-11-02 (estado revisado)

- Revisado o estado do repositório e mantido o registro de implementação inicial do seletor Android já existente (commit `6692f86c289d6df475ec2651b84e93448f93876a`), com ajustes posteriores para detectar XEX sem diferenciar maiúsculas/minúsculas e só persistir a URI após cópia bem-sucedida.
- A tela de preparação usa `ACTION_OPEN_DOCUMENT_TREE`, copia a árvore selecionada para `files/game` e a Activity SDL recebe `--game_data_root` apontando para o armazenamento privado.
- **Estado confirmado neste registro:** ainda faltam validação prévia de espaço livre, progresso/cancelamento robustos, reaproveitamento seguro da cópia existente, testes de compilação/inicialização no Android e integração final com workflow que gere APK.
- **Privacidade:** o `Default.xex` particular não deve ser commitado, embutido no APK nem publicado em artefatos.
- Nenhum código-fonte ou workflow do Resident Evil foi alterado nesta atualização; nenhum build foi iniciado por esta atualização de documentação.
- Próxima etapa: concluir e validar as melhorias do instalador Android antes de configurar/acionar uma compilação final do APK.
