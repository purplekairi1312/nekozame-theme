# nekozame-theme

Soft violet-gray with pastel pink, baby blue, mint, lemon and lilac. The theme of [nekozame os](https://github.com/purplekairi1312/nekozame-os).

<!-- palette -->
| | Name | Hex | Used for |
|---|---|---|---|
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/bg.png" width="20" height="20" alt=""> | Crowning | `#5a4f6e` | background |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/panel.png" width="20" height="20" alt=""> | Roman Purple | `#4f4562` | sidebars, popups, title bars |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/deep.png" width="20" height="20" alt=""> | Purple Velvet | `#433a55` | borders, terminal black, text on pink |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/raised.png" width="20" height="20" alt=""> | Napa Winery | `#685c7f` | raised elements, inactive tabs |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/selection.png" width="20" height="20" alt=""> | Grape Parfait | `#8a76a8` | selected items |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/region.png" width="20" height="20" alt=""> | Queen’s | `#7c6a9a` | selected text in editors |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/linenum.png" width="20" height="20" alt=""> | Lush Mauve | `#a094b8` | line numbers |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/dim.png" width="20" height="20" alt=""> | Wisteria-Wise | `#b3a7cb` | disabled and inactive text |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/fg.png" width="20" height="20" alt=""> | White | `#ffffff` | text |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/pinktext.png" width="20" height="20" alt=""> | Sweet Sachet | `#ffd9ef` | pink text (terminals) |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/muted.png" width="20" height="20" alt=""> | Lingering Lilac | `#e8def5` | secondary text |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/comment.png" width="20" height="20" alt=""> | Italian Fitch | `#d8cdec` | code comments |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/lavender.png" width="20" height="20" alt=""> | Minute Mauve | `#f1e6ff` | operators, variables |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/orchid.png" width="20" height="20" alt=""> | Pretty in Pink | `#ffc0e5` | main accent: cursor, focus, titles |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/pink.png" width="20" height="20" alt=""> | Little Smile | `#ffd4ee` | soft accent, headings |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/rose.png" width="20" height="20" alt=""> | Garden Glory | `#ffc0d2` | warm accent |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/link.png" width="20" height="20" alt=""> | Rosy Maple Moth | `#ffc6ea` | links |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/error.png" width="20" height="20" alt=""> | Baby Pink | `#ffb3c8` | errors |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/border.png" width="20" height="20" alt=""> | Classic Rose | `#ffd1ec` | focused borders, dividers |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/violet.png" width="20" height="20" alt=""> | Lens Flare Pink | `#e3ccff` | keywords |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/blue.png" width="20" height="20" alt=""> | Arctic Paradise | `#b8e4ff` | functions, info |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/cyan.png" width="20" height="20" alt=""> | Ice Citadel | `#b8f5f2` | types, special |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/mint.png" width="20" height="20" alt=""> | Out of Blue | `#c8f7dc` | strings, success |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/green.png" width="20" height="20" alt=""> | Chicon | `#dcf8bc` | additions |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/butter.png" width="20" height="20" alt=""> | Thunderbolt | `#fff1b0` | warnings, numbers |
| <img src="https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets/peach.png" width="20" height="20" alt=""> | Peachy Bon-Bon | `#ffd2b8` | constants |
<!-- /palette -->

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

Edit [`palette.toml`](palette.toml), run `./name-colors.py` if you changed a hex (it names the color), then `./generate.py`. Every theme in `themes/` is rebuilt from [`templates/`](templates), so they all stay the same. Bitwig's file is the exception: its shades are tuned by hand.

## License

[CC BY-NC-SA 4.0](LICENSE).
