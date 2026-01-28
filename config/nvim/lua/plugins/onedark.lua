return {
  'olimorris/onedarkpro.nvim',
  priority = 1000,
  lazy = false,
  config = function()
    require('onedarkpro').setup {
      styles = { comments = 'italic' },
      options = { transparency = false },
      colors = {
        bg = '#101013',
        fg = '#fefefe',
        blue = '#33ccff',
        green = '#00ff99',
      },
    }
    vim.cmd 'colorscheme onedark_dark'
  end,
}
