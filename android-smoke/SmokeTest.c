#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>

int main(int argc, char **argv) {
    (void)argc;
    (void)argv;

    SDL_SetAppMetadata("Resident Evil Code Veronica X Android Test",
                       "0.1.0", "com.rexglue.recvx.smoketest");

    if (!SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS)) {
        SDL_LogError(SDL_LOG_CATEGORY_APPLICATION,
                     "RECVX_SMOKE: SDL_Init failed: %s", SDL_GetError());
        return 10;
    }

    SDL_Window *window = SDL_CreateWindow(
        "Resident Evil Code Veronica X - Android Test",
        0, 0, SDL_WINDOW_FULLSCREEN);
    if (!window) {
        SDL_LogError(SDL_LOG_CATEGORY_APPLICATION,
                     "RECVX_SMOKE: SDL_CreateWindow failed: %s", SDL_GetError());
        SDL_Quit();
        return 11;
    }

    SDL_Renderer *renderer = SDL_CreateRenderer(window, NULL);
    if (!renderer) {
        SDL_LogError(SDL_LOG_CATEGORY_APPLICATION,
                     "RECVX_SMOKE: SDL_CreateRenderer failed: %s", SDL_GetError());
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 12;
    }

    SDL_Log("RECVX_SMOKE: SDL 3 initialized; window and renderer are ready.");
    bool running = true;
    Uint64 start = SDL_GetTicks();

    while (running) {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_EVENT_QUIT ||
                event.type == SDL_EVENT_TERMINATING) {
                running = false;
            }
        }

        Uint64 phase = ((SDL_GetTicks() - start) / 1200) % 3;
        if (phase == 0) {
            SDL_SetRenderDrawColor(renderer, 28, 10, 18, 255);
        } else if (phase == 1) {
            SDL_SetRenderDrawColor(renderer, 18, 34, 48, 255);
        } else {
            SDL_SetRenderDrawColor(renderer, 38, 28, 12, 255);
        }
        SDL_RenderClear(renderer);
        SDL_RenderPresent(renderer);
        SDL_Delay(16);
    }

    SDL_Log("RECVX_SMOKE: shutting down cleanly.");
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
