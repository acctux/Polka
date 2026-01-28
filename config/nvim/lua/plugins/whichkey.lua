return {
  'folke/which-key.nvim',
  event = 'VimEnter', -- Sets the loading event to 'VimEnter'
  opts = {
    -- delay between pressing key and opening which-key (milliseconds)
    delay = 0,
    icons = {
      mappings = vim.g.have_nerd_font,
      keys = vim.g.have_nerd_font and {},
    },
    -- Document existing key chains
    spec = {
      { '<leader>f', group = '[F]ind' },
      { '<leader>t', group = '[T]oggle' },
      { '<leader>h', group = 'Git [H]unk', mode = { 'n', 'v' } },
    },
  },
}
