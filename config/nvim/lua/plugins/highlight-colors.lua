return {
  'brenoprata10/nvim-highlight-colors',
  version = '*',
  event = 'VeryLazy',
  opts = {
    -- Colors: "background", "foreground", or "virtual"
    render = 'background',
    enable_named_colors = false,
    enable_tailwind = false,
    -- symbols for virtual text (if render = "virtual")
    virtual_symbol = '■',
    virtual_symbol_prefix = '',
    virtual_symbol_suffix = ' ',
    -- exclusions
    exclude_filetypes = {},
    exclude_buftypes = {},
    exclude_buffer = function(bufnr) end,
  },
}
