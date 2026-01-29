return {
  "neovim/nvim-lspconfig",
  ---@class PluginLspOpts
  opts = {
    ---@type lspconfig.options
    servers = {
      ty = {},  -- pyright LSP server setup
      ruff = {},
    },
  },
}

