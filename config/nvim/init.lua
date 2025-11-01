-- bootstrap lazy.nvim, LazyVim and your plugins
require("config.lazy")
require("onedarkpro").setup({
  themes = {
    onedark_dark = "~/.config/nvim/lua/plugins/colors/mine.lua",
  },
})
