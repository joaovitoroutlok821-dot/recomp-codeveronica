# Plano de reconstrução Android — Resident Evil Code: Veronica X

## Escopo e isolamento

- Repositório: `joaovitoroutlok821-dot/recomp-codeveronica`.
- Branch de trabalho: `android-rebuild`.
- Base preservada: `main` no commit `8da26ce9542c252ea24babafd3f3cf53dbf3eb75`.
- A branch `main` não será reescrita nem usada para experimentos desta reconstrução.
- O projeto continua sendo uma recompilação nativa; não será substituído por um emulador.
- O arquivo comercial `Default.xex` permanece somente no armazenamento privado do usuário ou em entrada temporária privada de CI. Nunca versionar, embutir no APK ou publicar em artefatos.

## Diagnóstico de partida

1. O codegen e o executável Linux x86-64 já foram compilados em experimentos anteriores.
2. O SDK ReXGlue 0.10.0 foi compilado para Android ARM64 no probe anterior, incluindo runtime e backend Xenos.
3. Esses resultados não demonstram que o alvo específico `recvx` foi compilado para Android nem que há APK.
4. O `build.sh` atual é de host Linux e não deve ser reutilizado como se fosse um builder Android.
5. Já existe um helper inicial para integrar SAF, copiar a pasta escolhida para armazenamento privado e iniciar SDL; ele ainda precisa de revisão e validação.
6. O pacote SDL Java e a biblioteca nativa devem vir do mesmo commit SDL usado pelo SDK, evitando os erros JNI/versão já observados em tentativas anteriores.

## Arquitetura de reconstrução

### Fase 1 — Base Android mínima e identidade do app
- Definir application ID, nome e ícones próprios do jogo.
- Manter uma Activity de configuração separada da Activity SDL.
- Validar Manifest, Java/Kotlin e recursos Android sem iniciar o runtime.
- Não usar a logo padrão do SDL como identidade do launcher.

### Fase 2 — SDL e JNI
- Fixar o commit SDL compatível com a versão usada pelo ReXGlue.
- Construir `libSDL3.so` e integrar as classes Java do mesmo commit.
- Verificar ABI `arm64-v8a`, bibliotecas transitivas e métodos JNI antes de integrar o jogo.
- Produzir um APK mínimo de diagnóstico para validar inicialização/ciclo de vida no Android 13.

### Fase 3 — Preparação dos dados do jogo
- Usar Storage Access Framework para selecionar a pasta do usuário.
- Copiar a árvore para armazenamento privado do app, preservando nomes e subpastas.
- Verificar espaço livre, progresso, cancelamento, erros de I/O e existência de `Default.xex`.
- Não iniciar SDL/runtime antes de concluir a preparação.

### Fase 4 — Codegen e compilação do título
- Executar o CLI ReXGlue Linux x86-64 no host do GitHub Actions.
- Manter o XEX fora do Git e dos artefatos públicos; a entrada privada de CI deverá ser definida antes de automatizar esta fase.
- Compilar as unidades geradas do título com Android NDK para `arm64-v8a`.
- Ligar o alvo `recvx` ao runtime e ao backend Xenos Android reais, sem misturar binários Linux/host.

### Fase 5 — APK verificável
- Empacotar SDL Java/JNI, `libmain.so`, `librexruntime.so`, backend Xenos e dependências efetivamente necessárias.
- Verificar o APK com ferramentas Android: package, ABI, manifest, assinatura, presença de bibliotecas e ausência do XEX.
- Publicar artefato de teste somente depois dessas verificações.

### Fase 6 — Teste no aparelho
- Testar launcher e seletor sem dados do jogo.
- Testar cópia da pasta e inicialização separadamente.
- Capturar logs persistentes em caso de falha.
- Diagnosticar gráficos/superfície Vulkan, áudio e controles em etapas distintas.

## Critérios para declarar sucesso

- Build Android do alvo específico `recvx` concluído para `arm64-v8a`.
- APK gerado e validado; não basta compilar o SDK ou o codegen.
- O APK instala e abre a tela própria de configuração no Motorola Edge 30 Pro / Android 13.
- A pasta selecionada é preparada sem incorporar os dados comerciais ao pacote.
- A Activity SDL inicia sem incompatibilidade JNI ou bibliotecas ausentes.
- Só declarar jogo funcional após comprovar execução e saída gráfica real no aparelho.

## Próxima tarefa técnica

Executar pela primeira vez o workflow `.github/workflows/android-smoke-test.yml` na branch `android-rebuild`, corrigir erros de configuração/compilação e inspecionar o APK e os logs. A API de Actions retornou zero execuções até agora, portanto a existência do workflow não comprova build. Só depois de obter APK SDL/JNI válido e testá-lo no aparelho integrar codegen host e fontes do título. Cada fase terá workflow e artefato próprios, com logs e critérios de aprovação claros.
