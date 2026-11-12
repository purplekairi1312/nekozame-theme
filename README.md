# nekozame-theme

Soft lavender with pastel pink, baby blue, mint, lemon and lilac. The theme of [nekozame os](https://github.com/purplekairi1312/nekozame-os).

| | | | |
|---|---|---|---|
| bg `#5a4f6e` | panel `#4f4562` | text `#ffffff` | pink text `#ffd9ef` |
| orchid `#ffc0e5` | pink `#ffd4ee` | baby blue `#b8e4ff` | cyan `#b8f5f2` |
| mint `#c8f7dc` | lemon `#fff1b0` | lilac `#e3ccff` | peach `#ffd2b8` |

All of it is in [`palette.toml`](palette.toml).

## Install

Everything is in [`themes/`](themes).

| App | File | Where |
|---|---|---|
| Doom Emacs | `emacs/nekozame-theme.el` | `~/.config/doom/themes/`, then `(setq doom-theme 'nekozame)` |
| Ghostty | `ghostty/nekozame` | `~/.config/ghostty/themes/`, then `theme = nekozame` |
| KDE Plasma | `kde/nekozame.colors` | `~/.local/share/color-schemes/`, then System Settings → Colors |
| Konsole | `konsole/nekozame.colorscheme` | `~/.local/share/konsole/` |
| VS Code | `vscode/` | copy the folder to `~/.vscode/extensions/purplekairi1312.nekozame-1.0.0` |
| btop | `btop/nekozame.theme` | `~/.config/btop/themes/`, then `color_theme = "nekozame"` |
| Starship | `starship/starship.toml` | `~/.config/starship.toml` (a full prompt config) |
| Zen Browser | `zen/userChrome.css` | `chrome/` in your profile, with `toolkit.legacyUserProfileCustomizations.stylesheets` on |
| Discord | `discord/nekozame.theme.css` | Vencord's themes folder |
| Bitwig Studio | `bitwig/nekozame_bitwig_6.1.4.bte` | load it with the [Bitwig Theme Editor](https://github.com/Berikai/bitwig-theme-editor) |
| Krita, GIMP, Aseprite | `palettes/nekozame.gpl` | the app's palettes folder |

## Changing colors

Edit [`palette.toml`](palette.toml), then run `./generate.py`. Every theme in `themes/` is rebuilt from [`templates/`](templates), so they all stay the same. Bitwig's file is the exception: its shades are tuned by hand.

## License

[CC BY-NC-SA 4.0](LICENSE).
