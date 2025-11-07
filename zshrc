# ~/.zshrc
eval "$(starship init zsh)"
eval "$(zoxide init --cmd cd zsh)"
eval "$(mcfly init zsh)"
eval "$(direnv hook zsh)"
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Ignore commands that start with spaces and duplicates.

HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt HIST_IGNORE_SPACE        # Ignore commands that start with a space
setopt HIST_IGNORE_DUPS         # Ignore duplicate commands in a row
setopt HIST_SAVE_NO_DUPS        # Don't write duplicate entries to history file
setopt HIST_EXPIRE_DUPS_FIRST   # Expire duplicate entries before unique ones
setopt HIST_FIND_NO_DUPS        # Ignore duplicates when searching with up-arrow
setopt HIST_REDUCE_BLANKS       # Remove extra spaces
setopt SHARE_HISTORY            # Share history across terminals *carefully*
setopt INC_APPEND_HISTORY       # Append (not overwrite) after each command
setopt APPEND_HISTORY           # Safer append mode (legacy, still useful)

setopt autocd extendedglob
setopt correct
setopt interactivecomments

export HISTIGNORE="&:[bf]g:c:clear:history:exit:q:pwd:* --help"

source /usr/share/zsh/plugins/zsh-autocomplete/zsh-autocomplete.plugin.zsh
source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source /usr/share/fzf/key-bindings.zsh

fvim() {
  local search_dirs=("${@:-.}")
  local selection

  # Use null-delimited output for filename safety
  selection=$(fd --hidden --type f . \
  | fzf --multi --preview 'bat --style=numbers --color=always --line-range=:100 {}' --height=40% \
  | xargs -r nvim) || return 1

  # Exit if nothing selected
  [[ -z "$selection" ]] && return 1

  # Convert nulls to newlines
  local -a files=()
  while IFS= read -r -d '' f; do
    files+=("$f")
  done < <(printf '%s' "$selection")

  # Detect if any file is under /etc or /usr
  local need_root=false
  for f in "${files[@]}"; do
    if [[ "$f" == /etc/* || "$f" == /usr/* ]]; then
      need_root=true
      break
    fi
  done

# pkgfile "command not found" handler
source /usr/share/doc/pkgfile/command-not-found.zsh

alias ls='eza -a --icons=always'
alias ll='eza -al --icons=always'
alias lt='eza -a --tree --level=1 --icons=always'
alias shutdown='systemctl poweroff'
alias grep='grep --color=auto'
alias mkdir='mkdir -pv'

alias cx='chmod +x'
alias lg='lazygit'
alias cpnames="/home/nick/Lit/scripts/cpfilenames/copyfilenames.sh"
alias loggy='sudo systemctl restart logid'
alias dotsync='/home/nick/.local/bin/dotsync/dotsync.py'
