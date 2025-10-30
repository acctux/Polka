-- bootstrap lazy.nvim, LazyVim and your plugins
require("config.lazy")
require("onedarkpro").setup({
  themes = {
    onedark_dark = "~/.config/nvim/lua/plugins/colors/mine.lua",
  },
  options = {
    transparency = true,
    lualine_transparency = true,
  },
})

-- ~/.config/nvim/colors/vaporwave.lua
require("onedarkpro.config").set_theme("my_dark")
require("onedarkpro").load()
