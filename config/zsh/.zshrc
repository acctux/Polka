# ~/.zshrc
eval "$(starship init zsh)"
eval "$(zoxide init --cmd cd zsh)"
eval "$(mcfly init zsh)"
# eval "$(direnv hook zsh)"
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# better sudo expansion
alias sudo='sudo '

# Ignore commands that start with spaces and duplicates.

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

alias ls='eza -a --icons=always'
alias ll='eza -al --icons=always'
alias lt='eza -a --tree --level=1 --icons=always'
alias shutdown='systemctl poweroff'
alias grep='grep --color=auto'
alias mkdir='mkdir -pv'
alias cx='chmod +x'
alias cmatrix='cmatrix -a -C blue'
alias lg='lazygit'
alias cpnames="/home/nick/Lit/scripts/cpfilenames/copyfilenames.sh"
alias loggy='sudo systemctl restart logid'
alias dotsync='/home/nick/.local/bin/dotsync/dotsync.py'


gitfuzzy() {
  if ! git rev-parse --is-inside-work-tree &>/dev/null; then
    echo "Not inside a Git repository."
    return 1
  fi
  echo -n "Search: "
  read search_term
  [[ -z "$search_term" ]] && return 0
  local selection
  selection=$(git log --all --pretty=format:"%h %s" \
    | fzf --ansi \
          --prompt="Search commits: " \
          --preview "git show --color=always {1} | rg --color=always --context 5 '$search_term'" \
          --preview-window=up:50%:wrap)
  [[ -n "$selection" ]] && git show --color=always "${selection%% *}" | delta
}




