# Análise técnica: NFSMW Recompiled Mobile e aplicação ao Resident Evil Code Veronica X

**Data:** 2026-11-03  
**Tipo:** relatório de pesquisa e plano de diagnóstico  
**Escopo:** comparação técnica; este documento não altera código nem dispara compilação.

## 1. Resumo executivo

O [NFSMW-Recompiled-Mobile](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile) é uma recompilação estática nativa de Need for Speed: Most Wanted (2005), versão Xbox 360. A documentação descreve codegen PowerPC para C++, runtime ReXGlue, port Android ARM64 e caminhos gráficos Xenos e nativo.

Para Resident Evil Code Veronica X, o valor principal é servir como referência de integração e diagnóstico Android: estrutura Gradle/NDK/CMake, SDL/Activity, acesso aos arquivos, logs persistentes, separação entre código gerado e runtime e processo de correções reversíveis. A ferramenta de lacunas também pode inspirar uma auditoria do codegen, mas não há evidência atual de que o crash do Resident Evil seja causado por uma lacuna de função.

**Conclusão:** usar o NFSMW como referência de arquitetura e checklist, não como código pronto para copiar. O estado de Resident Evil continua sendo integração Android ARM64 em andamento; compilar o SDK, isoladamente, não comprova APK funcional nem execução do jogo.

## 2. O que foi confirmado no NFSMW

### 2.1 Pipeline de recompilação

O projeto documenta extração do XEX, análise PowerPC e geração antecipada de C++ pelo codegen ReXGlue, ajustes manuais para tabelas de salto/dados/limites de função, compilação e ligação ao runtime, e ciclo de execução com logs para identificar imports, stubs e comportamentos não implementados.

Referências:
- [README](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/README.md)
- [Codegen](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/docs/02-codegen.md)
- [Runtime](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/docs/03-runtime.md)
- [Arquitetura](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/docs/arquitectura.md)

### 2.2 Diagnóstico de lacunas e overrides

[tools/huecos.py](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/tools/huecos.py) estima tamanhos de funções contando instruções PowerPC comentadas, cruza os finais calculados com os inícios de codegen.partition.json e lista intervalos não atribuídos. Também permite consultar endereços específicos.

O próprio script alerta que uma lacuna pode conter várias funções pequenas/thunks ou dados. Declarar a lacuna inteira como uma função pode esconder entradas internas. Dividir tudo em blocos fixos também pode criar entradas falsas no meio de funções reais.

O NFSMW separa funções independentes e continuações em [app/huecos.toml](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/app/huecos.toml) e mantém declarações manuais e experimentos em [app/overrides.toml](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/app/overrides.toml). Isso é útil como modelo de documentação e cautela, não como arquivo para importar.

### 2.3 Patches rastreáveis

O projeto mantém patches em scripts separados, com aplicação, consulta de estado e reversão. A documentação registra ordem e evidências. Referência: [docs/parches.md](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/docs/parches.md).

### 2.4 Integração Android

A documentação do NFSMW descreve port Android ARM64 usando NDK 28.2, CMake 3.31.6 e Gradle, acesso ao arquivo do jogo e logs persistentes. Os testes relatados foram feitos em outro aparelho (Snapdragon 8 Elite/Adreno 830, Android 16) e ainda há limitações, incluindo ausência de controles táteis integrados e problemas de áudio e carregamento.

O projeto diferencia o caminho Xenos do renderer nativo feito sob medida para NFSMW. Esse renderer não é solução universal para jogos Xbox 360.

Referências:
- [Port Android](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/docs/android.md)
- [Gradle Android](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/android/app/build.gradle.kts)
- [Pipeline gráfico nativo](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/docs/pipeline-nativo.md)

## 3. Estado atual de Resident Evil registrado no repositório

O STATUS.md registra:
- XEX identificado como XEX2, módulo interno Bio_cv.exe e SHA-256 documentado.
- Codegen e build Linux x86-64 geraram 214 unidades C++ e ligaram o executável recvx.
- Um workflow confirmou compilação do SDK Android ARM64 para aarch64-none-linux-android26, com REX_PLATFORM_ANDROID=1, e ligação de componentes como librexruntime.so e librexgpu-xenos.so.
- Esse marco comprova a compilação do SDK Android, não a ligação do alvo recvx, criação do APK, funcionamento da Activity/SDL/Vulkan ou renderização do jogo.

O problema relatado no teste do APK #19 — tela preta após iniciar e retorno ao launcher — deve ser investigado na sequência de inicialização do jogo e na integração de apresentação Android. Não se deve presumir que seja o mesmo problema de callback do Pac-Man.

## 4. Técnicas reaproveitáveis

| Técnica do NFSMW | Aplicação proposta |
|---|---|
| Separar SDK, código gerado e camada da aplicação | Identificar quais alvos Android ainda faltam ligar |
| Build Android explícito com NDK/CMake/Gradle | Comparar ABI, API level, dependências e bibliotecas empacotadas |
| Logs persistentes em arquivo | Preservar diagnóstico mesmo quando o processo fecha ou logcat é limitado |
| Seleção/acesso a arquivos por SAF ou URI | Validar que a pasta selecionada chega corretamente ao runtime |
| Teste Vulkan separado do jogo | Isolar falha de driver/surface de falha no código do jogo |
| Patches pequenos e reversíveis | Corrigir uma camada por vez |
| Checklist de limitações e estado | Não confundir compilação de SDK com execução funcional |

## 5. Plano de diagnóstico Android

### Etapa A — fechar a cadeia de build

1. Confirmar que o alvo gerado recvx é compilado para arm64-v8a, não apenas o SDK.
2. Confirmar a ligação de todas as bibliotecas compartilhadas exigidas.
3. Inspecionar o APK: bibliotecas nativas, SDL Java/JNI, manifesto, ABI e assets.
4. Verificar dependências dinâmicas e comparar com as bibliotecas empacotadas.
5. Confirmar que o launcher abre sem exigir que os arquivos do jogo estejam selecionados.

### Etapa B — isolar o início do jogo

Adicionar marcadores com timestamp para: seleção/validação do diretório; abertura do arquivo e resolução do URI; criação do runtime; carregamento do módulo; inicialização de kernel/imports/memória; criação da janela/surface SDL/Vulkan; primeiro frame submetido e apresentado; áudio e input.

O primeiro marcador ausente após tocar em Iniciar delimita a camada da falha. Os logs devem indicar se a falha ocorreu antes ou depois da criação da surface.

### Etapa C — persistência dos logs

O NFSMW documenta gravação em arquivo privado do app porque algumas ROMs limitam o logcat. Para Resident Evil, implementar ou validar log persistente em diretório acessível pelo usuário, sem gravar dados privados do jogo. Registrar exceções JNI, erros SDL, falhas de bibliotecas, criação da surface e traps do runtime. Descarregar os dados em pontos críticos.

### Etapa D — verificar JNI e SDL

Comparar as versões SDL Java e SDL nativa incluídas no mesmo APK. Conferir nomes e assinaturas dos métodos JNI, classes empacotadas e ordem de inicialização. Não misturar versões do SDL nem assumir que compilar a biblioteca nativa garante compatibilidade com as classes Java.

### Etapa E — separar Vulkan da execução guest

Executar primeiro um teste mínimo de criação da surface e apresentação de um frame, sem carregar o jogo. Depois iniciar runtime e módulo recompilado. Assim será possível distinguir Activity/SDL/JNI, driver Vulkan/surface, carregamento XEX, runtime/kernel/imports e execução do código recompilado.

## 6. O que não deve ser copiado

- Endereços, manifests, stubs, imports e patches específicos do NFSMW.
- Renderer Vulkan/OpenGL ES nativo de NFS, feito para o fluxo gráfico desse jogo.
- Configurações de resolução, controles ou áudio sem validar as necessidades do Code Veronica.
- Resultados de desempenho de outro aparelho como se fossem medições no Motorola Edge 30 Pro.
- A suposição de que compilar o SDK prova que o jogo está pronto.

## 7. Próximos passos recomendados

1. Ler o workflow Android atual e confirmar a etapa em que recvx é ligado.
2. Auditar o APK produzido e suas dependências SDL/JNI/Vulkan.
3. Adicionar marcadores de inicialização e log persistente antes de solicitar novo teste no aparelho.
4. Gerar APK apenas após uma alteração diagnóstica ou funcional concreta e workflow concluído.
5. Após o teste, usar o primeiro marcador ausente e o crash correspondente para corrigir uma camada por vez.
6. Manter a identidade visual separada da integração técnica: o ícone/logo de Code Veronica solicitado deve entrar no pacote Android, mas não corrige a tela preta.

## 8. Limites e estado

Este documento é análise comparativa e planejamento. **Não altera código, workflow, manifesto, recursos visuais ou APK.** O marco de SDK Android ARM64 não comprova ainda um APK funcional do jogo. A tela preta do teste #19 continua sem causa confirmada neste relatório.

## 9. Fontes

- [NFSMW README](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/README.md)
- [tools/huecos.py](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/tools/huecos.py)
- [app/huecos.toml](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/app/huecos.toml)
- [app/overrides.toml](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/app/overrides.toml)
- [docs/02-codegen.md](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/docs/02-codegen.md)
- [docs/03-runtime.md](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/docs/03-runtime.md)
- [docs/android.md](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/docs/android.md)
- [docs/parches.md](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/docs/parches.md)
- [docs/pipeline-nativo.md](https://github.com/marcussilvacastrooutlok-afk/NFSMW-Recompiled-Mobile/blob/main/docs/pipeline-nativo.md)
