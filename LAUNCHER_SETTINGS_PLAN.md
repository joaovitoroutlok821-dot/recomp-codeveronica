# Resident Evil Code: Veronica X HD — Android launcher settings

This document tracks the requested launcher redesign for the Android ARM64 build. The known-good game launch path from Workflow #26 must remain intact while the launcher is replaced.

## Visual target
- Use the user-approved 16:9 launcher/settings artwork (Claire and Steve, blue-black background, red illuminated borders and controls) as the visual reference.
- Do not use the artwork as the only UI. Buttons, tabs, selectors, sliders and toggles must be real Android controls layered in a responsive layout.
- Use landscape for the launcher and game where required by the title; verify existing SDL orientation before changing the game activity.
- Keep the game title, logo and red/black identity. Do not show SDL sample/demo text or controls.

## Launcher navigation
- Iniciar Jogo: retain Workflow #26 behavior. If the private game copy is already prepared, launch GameSDLActivity with the same game-root argument. Otherwise open SAF folder selection and copy/validate Default.xex before launch.
- Configurações: open settings with tabs for Gráficos, Desempenho, Controles and Áudio.
- Controles: expose physical-controller status, touch-control visibility policy, layout editor, size and opacity.
- Salvar / Carregar: reserve for actual supported save-state functionality; do not present a nonfunctional button as working.
- Informações and Sair: implement as real actions.

## Requested graphics controls
- Output resolution: 720p, 900p, 1080p (only modes supported by the Android display/surface).
- Render scale: native / lower scales only where the renderer supports them.
- Image quality: economy, balanced, high.
- Image filter: bilinear, CAS, FSR; only expose filters compiled and available on this Android build.
- FSR mode: Quality, Balanced, Performance; only when FSR is integrated and initialized.
- CAS sharpness slider; only when CAS is integrated.
- Anti-aliasing: only modes actually implemented by the current renderer.
- Particle/effect quality: only if the game/runtime exposes a working control.
- Aspect ratio: automatic / preserve aspect ratio, only if supported.

## Requested performance controls
- FPS cap: 30, 45, 60, restricted to supported frame pacing modes.
- V-Sync: enabled/disabled only if the presenter exposes a reliable setting.
- FPS counter: show/hide; use the existing presented-FPS JNI path.
- Shader cache: enable/disable only if a real cache setting exists.
- Reduce heavy effects: map to a verified game/runtime setting; do not silently fake it.

## Requested controller controls
- Physical Bluetooth/gamepad input must work alongside the virtual touch gamepad.
- Auto touch visibility: hide touch overlay only after a physical controller is detected and confirmed to deliver input; show it again after disconnect/idle policy.
- Manual policies: Automatic / Always show / Always hide.
- Layout editor: drag each touch control; adjust size and opacity; save positions in app preferences; restore defaults.
- Editing mode must not send game button presses.
- Do not treat the virtual touch gamepad as a physical controller when deciding whether to hide the overlay.

## Audio controls
- Master/music/effects sliders only if there are real runtime/game audio controls. Persist settings only after a verified mapping exists.

## Persistence and application
- Persist user selections in app-private SharedPreferences (or a versioned app-private settings file).
- Clearly mark settings that require restarting the game.
- Provide Apply and Restore defaults actions.
- Pass settings into the runtime only through verified ReXGlue/game cvars or documented Android hooks. A saved UI value alone is not a functional setting.
- Keep unsupported controls disabled with a short explanation until implementation is complete.

## Verification gates before producing the next user-test APK
1. Launcher artwork and layout are legible in landscape on the Motorola Edge 30 Pro.
2. Start button still opens the already-prepared game from Workflow #26.
3. SAF selection/copy and XEX2 validation still work for a first launch.
4. Preferences survive force-close and relaunch.
5. Each enabled option changes real runtime/game behavior; unsupported options remain disabled.
6. Bluetooth controller is enumerated by Android, reaches SDL/ReXGlue, and controls the game.
7. Automatic touch hiding occurs only after physical-controller input is confirmed; touch controls return after disconnect.
8. Touch layout changes persist, and editor mode does not send game input.
9. APK package/ABI/signature checks pass and private game files are not included in the APK or public artifacts.

## Current known baseline
- Workflow #26 opens the game successfully on the user's phone.
- The installer now generates a separate native `GameSettingsActivity` with Gráficos, Desempenho, Controles and Áudio sections, a 720p/1080p output-mode selector (1080p default), FPS-counter toggle, and touch-overlay policy selector. The setup screen opens this settings page without changing the existing SAF copy/launch path.
- The selected output mode is passed to ReXGlue as `window_width` / `window_height`; the current image effect is explicitly `bilinear`. The FPS preference controls the on-screen readout. Automatic touch mode hides the overlay only after a physical key/joystick event is received and restores it after controller removal.
- The new settings screen is an initial functional implementation, not yet a pixel-matched recreation of the approved red/black artwork. FSR/CAS, render scaling, AA, FPS cap, V-Sync, shader cache, effects and audio controls remain unavailable/disabled because the Android runtime does not yet expose verified working hooks for them.
- Touch overlay code exists, but the user's prior test reported that only on-screen controls worked; Bluetooth was not working.
- The presented-FPS JNI path exists in the game activity, but it must be revalidated in the actual next APK.
- FSR/CAS, resolution scaling, AA, shader cache, heavy-effect controls and audio sliders must not be claimed as working until mapped to real Android runtime/game settings.

## Verified ReXGlue option mapping (SDK source inspection)

The pinned ReXGlue SDK declares these presenter cvars:
- present_effect: bilinear, cas, fsr, fsr2, fsr3 only when RE​​X_HAS_FIDELITYFX_SDK is compiled; otherwise bilinear is the only allowed value.
- present_cas_additional_sharpness: CAS sharpness, only with FidelityFX SDK support.
- present_fsr_quality_mode: auto, nativeaa, quality, balanced, performance, ultra_performance, only with FidelityFX SDK support.
- present_fsr_max_upsampling_passes and present_fsr_sharpness_reduction: FSR tuning, only with FidelityFX SDK support.
- present_letterbox, present_safe_area_x/y, present_dither, present_allow_overscan_cutoff.
- window_width, window_height, fullscreen and resolution are declared by the SDK; actual Android surface behavior still needs device validation.
- Vulkan exposes allow-present-mode switches (immediate, mailbox, FIFO relaxed); these are not equivalent to a user-selectable exact FPS cap.

The current private Android workflow explicitly passes -DREXGLUE_ENABLE_FIDELITYFX=OFF. Therefore this APK configuration cannot honestly offer CAS/FSR yet: the current presenter is limited to bilinear. The shader source files being present in the SDK does not mean the FidelityFX SDK/runtime is enabled in this Android build.

No FPS-cap, shader-cache, particle-quality, reduced-effects, anti-aliasing or game-audio cvar was found in the inspected SDK flags/presenter sources. These controls must remain disabled or be implemented through verified game-specific hooks. The already-added presented-FPS counter is a readout, not a frame limiter.


## Correções após avaliação do APK #28 — 2026-11-08

- O usuário confirmou que o APK #28 ainda não corresponde à referência visual aprovada.
- Commit `d390337051baa069ddd1757304c7ab8e4eecf313`: o instalador agora copia a arte fornecida também como `drawable/recvx_icon.png`, usa essa imagem diretamente no cabeçalho da tela inicial e atualiza os XMLs de ícone adaptativo do Android 8+ para não deixar os recursos adaptativos SDL sobreporem os PNGs.
- Commit `ee9c0f14fac43c4578090920cd51e64038e97dc3`: ajustes de espaçamento, hierarquia tipográfica e seletores escuros na tela de configurações, aproximando a apresentação da identidade vermelha/preta da referência.
- Estes commits ainda precisam passar pelo smoke test Android e por uma compilação privada completa antes de gerar APK para o usuário.
- O editor de controles táteis com arrastar/soltar, persistência de posições e tamanho/opacidade continua pendente; não apresentar como implementado.
- O funcionamento do controle Bluetooth continua pendente de confirmação no aparelho. O modo automático de ocultação deve continuar condicionado à entrada física confirmada, e nunca apenas à enumeração do gamepad virtual.
- Os controles de renderização, FSR/CAS, limite de FPS, V-Sync, cache, efeitos e áudio só devem ser habilitados após integração com hooks reais do runtime.
