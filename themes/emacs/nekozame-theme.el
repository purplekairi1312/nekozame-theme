;;; nekozame-theme.el --- nekozame for doom emacs -*- lexical-binding: t; no-byte-compile: t; -*-
;;
;; Author: purplekairi1312
;;
;; soft violet-gray with pastel pink, baby blue, mint, lemon and lilac.
;; generated from palette.toml by generate.py; edit the palette there.
;;
;;; Code:

(require 'doom-themes)

(defgroup nekozame-theme nil
  "Options for the `nekozame' theme."
  :group 'doom-themes)

(defcustom nekozame-brighter-modeline nil
  "If non-nil, the modeline uses the orchid accent instead of plum."
  :group 'nekozame-theme
  :type 'boolean)

(defcustom nekozame-padded-modeline doom-themes-padded-modeline
  "If non-nil, adds a 4px padding to the mode-line.
Can be an integer to determine the exact padding."
  :group 'nekozame-theme
  :type '(choice integer boolean))

(def-doom-theme nekozame
  "Soft violet-gray with pastel pink, baby blue, mint, lemon and lilac."

  ;; name        default    256        16
  ((bg         '("#5a4f6e" "#3a3a3a" "black"))
   (fg         '("#ffffff" "#eeeeee" "brightwhite"))

   ;; Darker panels: sidebars, popups, the minibuffer
   (bg-alt     '("#4f4562" "#303030" "black"))
   (fg-alt     '("#e8def5" "#bcbcbc" "white"))

   ;; From darkest to lightest
   (base0      '("#3a3249" "#262626" "black"))
   (base1      '("#433a55" "#262626" "brightblack"))
   (base2      '("#4f4562" "#303030" "brightblack"))
   (base3      '("#685c7f" "#3a3a3a" "brightblack"))
   (base4      '("#7a6e90" "#4e4e4e" "brightblack"))
   (base5      '("#a094b8" "#767676" "brightblack"))
   (base6      '("#b3a7cb" "#878787" "brightblack"))
   (base7      '("#e8def5" "#bcbcbc" "brightblack"))
   (base8      '("#ffffff" "#ffffff" "white"))

   (grey       '("#d8cdec" "#af87af" "brightblack"))
   (red        '("#ffc0d2" "#ff87af" "red"))
   (orange     '("#ffd2b8" "#ffaf87" "brightred"))
   (green      '("#dcf8bc" "#afd7af" "green"))
   (teal       '("#c8f7dc" "#afd7af" "brightgreen"))
   (yellow     '("#fff1b0" "#ffd787" "yellow"))
   (blue       '("#b8e4ff" "#87d7ff" "brightblue"))
   (dark-blue  '("#a6d3f5" "#87afd7" "blue"))
   (magenta    '("#ffc0e5" "#ff87d7" "brightmagenta"))
   (pink       '("#ffd4ee" "#ffafd7" "magenta"))
   (violet     '("#e3ccff" "#af87ff" "magenta"))
   (lavender   '("#f1e6ff" "#d7afd7" "white"))
   (cyan       '("#b8f5f2" "#87d7d7" "brightcyan"))
   (dark-cyan  '("#8fd0cc" "#5f8787" "cyan"))
   (plum       '("#8a76a8" "#875f87" "magenta"))
   (bright-red '("#ffb3c8" "#ff5f87" "brightred"))
   (orchid     '("#ffc6ea" "#ff87d7" "brightmagenta"))
   (border     '("#ffd1ec" "#af87af" "magenta"))

   ;; Face categories
   (highlight      magenta)
   (vertical-bar   base1)
   (selection      plum)
   (builtin        pink)
   (comments       grey)
   (doc-comments   (doom-lighten grey 0.2))
   (constants      orange)
   (functions      blue)
   (keywords       magenta)
   (methods        cyan)
   (operators      lavender)
   (type           violet)
   (strings        teal)
   (variables      lavender)
   (numbers        yellow)
   (region         '("#7c6a9a" "#5f5f87" "brightblack"))
   (error          bright-red)
   (warning        yellow)
   (success        green)
   (vc-modified    blue)
   (vc-added       teal)
   (vc-deleted     red)

   ;; Custom categories
   (modeline-fg     fg)
   (modeline-fg-alt fg-alt)
   (modeline-bg
    (if nekozame-brighter-modeline
        (doom-darken magenta 0.45)
      base3))
   (modeline-bg-alt
    (if nekozame-brighter-modeline
        (doom-darken magenta 0.55)
      base2))
   (modeline-bg-inactive     bg-alt)
   (modeline-bg-inactive-alt bg-alt)
   (-modeline-pad
    (when nekozame-padded-modeline
      (if (integerp nekozame-padded-modeline) nekozame-padded-modeline 4))))

  ;;;; Base theme face overrides
  (((line-number &override) :foreground base5)
   ((line-number-current-line &override) :foreground pink :weight 'bold)
   ((font-lock-comment-face &override) :slant 'italic)
   ((font-lock-doc-face &override) :slant 'italic)
   ((font-lock-keyword-face &override) :weight 'bold)
   ((font-lock-function-name-face &override) :weight 'bold)
   (cursor :background magenta)
   (link :foreground orchid :underline t)
   (link-visited :foreground violet :underline t)
   (minibuffer-prompt :foreground magenta :weight 'bold)
   (fringe :background bg :foreground base5)
   (hl-line :background base3 :extend t)
   (show-paren-match :foreground base8 :background plum :weight 'bold)
   (isearch :background magenta :foreground base0 :weight 'bold)
   (lazy-highlight :background (doom-blend magenta bg 0.35) :foreground fg :weight 'bold)
   (mode-line
    :background modeline-bg :foreground modeline-fg
    :box (if -modeline-pad `(:line-width ,-modeline-pad :color ,modeline-bg)))
   (mode-line-inactive
    :background modeline-bg-inactive :foreground modeline-fg-alt
    :box (if -modeline-pad `(:line-width ,-modeline-pad :color ,modeline-bg-inactive)))
   (mode-line-emphasis :foreground pink)
   (mode-line-highlight :background plum :foreground base8)
   (tooltip :background bg-alt :foreground fg)
   (child-frame-border :background border)

   ;;;; doom-modeline
   (doom-modeline-bar :background magenta)
   (doom-modeline-bar-inactive :background modeline-bg-inactive)
   (doom-modeline-buffer-file :inherit 'mode-line-buffer-id :weight 'bold)
   (doom-modeline-buffer-path :inherit 'mode-line-emphasis :weight 'bold)
   (doom-modeline-buffer-project-root :foreground cyan :weight 'bold)
   (doom-modeline-project-dir :foreground cyan :weight 'bold)
   (doom-modeline-info :foreground teal :weight 'bold)
   ;;;; doom-dashboard
   (doom-dashboard-banner :foreground magenta)
   (doom-dashboard-menu-title :foreground pink)
   (doom-dashboard-menu-desc :foreground fg-alt)
   (doom-dashboard-footer-icon :foreground violet)
   (doom-dashboard-loaded :foreground grey)
   ;;;; vertico / orderless / marginalia
   (vertico-current :background plum :foreground base8 :extend t)
   (orderless-match-face-0 :foreground magenta :weight 'bold)
   (orderless-match-face-1 :foreground blue :weight 'bold)
   (orderless-match-face-2 :foreground yellow :weight 'bold)
   (orderless-match-face-3 :foreground teal :weight 'bold)
   (completions-common-part :foreground magenta :weight 'bold)
   (completions-first-difference :foreground pink)
   ;;;; corfu
   (corfu-default :background bg-alt :foreground fg)
   (corfu-current :background plum :foreground base8)
   (corfu-border :background border)
   ;;;; tab-bar / centaur-tabs
   (centaur-tabs-selected :background bg :foreground base8)
   (centaur-tabs-unselected :background bg-alt :foreground fg-alt)
   (centaur-tabs-selected-modified :background bg :foreground magenta)
   (centaur-tabs-unselected-modified :background bg-alt :foreground pink)
   (centaur-tabs-active-bar-face :background magenta)
   (centaur-tabs-modified-marker-selected :foreground magenta :background bg)
   (centaur-tabs-modified-marker-unselected :foreground pink :background bg-alt)
   ;;;; treemacs
   (treemacs-root-face :foreground magenta :weight 'bold :height 1.1)
   (treemacs-directory-face :foreground lavender)
   (treemacs-file-face :foreground fg)
   (treemacs-git-modified-face :foreground blue)
   (treemacs-git-added-face :foreground teal)
   (treemacs-git-untracked-face :foreground yellow)
   ;;;; rainbow-delimiters
   (rainbow-delimiters-depth-1-face :foreground magenta)
   (rainbow-delimiters-depth-2-face :foreground blue)
   (rainbow-delimiters-depth-3-face :foreground violet)
   (rainbow-delimiters-depth-4-face :foreground teal)
   (rainbow-delimiters-depth-5-face :foreground pink)
   (rainbow-delimiters-depth-6-face :foreground yellow)
   (rainbow-delimiters-depth-7-face :foreground cyan)
   (rainbow-delimiters-unmatched-face :foreground bright-red :weight 'bold)
   ;;;; magit
   (magit-section-heading :foreground magenta :weight 'bold)
   (magit-branch-local :foreground blue)
   (magit-branch-remote :foreground teal)
   (magit-hash :foreground grey)
   ;;;; org
   (org-level-1 :foreground magenta :weight 'bold :height 1.25)
   (org-level-2 :foreground blue :weight 'bold :height 1.1)
   (org-level-3 :foreground violet :weight 'bold)
   (org-level-4 :foreground teal :weight 'bold)
   (org-level-5 :foreground pink)
   (org-level-6 :foreground cyan)
   (org-level-7 :foreground yellow)
   (org-level-8 :foreground lavender)
   (org-document-title :foreground pink :weight 'bold :height 1.4)
   (org-block :background bg-alt :extend t)
   (org-block-begin-line :background bg-alt :foreground grey :slant 'italic :extend t)
   (org-code :foreground orange)
   (org-verbatim :foreground teal)
   (org-todo :foreground magenta :weight 'bold)
   (org-done :foreground grey :weight 'bold)
   ;;;; markdown
   (markdown-header-face :inherit 'bold :foreground magenta)
   (markdown-code-face :background bg-alt :extend t)
   (markdown-markup-face :foreground grey)
   (markdown-link-face :foreground orchid)
   (markdown-url-face :foreground violet)
   ;;;; hl-todo
   (hl-todo :foreground yellow :weight 'bold)
   ;;;; whitespace
   (whitespace-tab :background bg :foreground base4)
   ;;;; solaire-mode
   (solaire-default-face :background bg-alt)
   (solaire-hl-line-face :background base2 :extend t)
   (solaire-mode-line-face
    :inherit 'mode-line
    :background modeline-bg-alt
    :box (if -modeline-pad `(:line-width ,-modeline-pad :color ,modeline-bg-alt)))
   (solaire-mode-line-inactive-face
    :inherit 'mode-line-inactive
    :background modeline-bg-inactive-alt
    :box (if -modeline-pad `(:line-width ,-modeline-pad :color ,modeline-bg-inactive-alt))))

  ;;;; Base theme variable overrides
  ())

;;; nekozame-theme.el ends here
