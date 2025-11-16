-- lua/plugins/nightfox.lua
return {
  "EdenEast/nightfox.nvim",
  name = "nightfox",
  lazy = false, -- Load immediately at startup
  priority = 1000, -- Ensure colorscheme loads first
  config = function()
    require("nightfox").setup({
      options = {
        compile_path = vim.fn.stdpath("cache") .. "/nightfox",
        compile_file_suffix = "_compiled",
        transparent = false,
        terminal_colors = true,
        dim_inactive = false,
        module_default = true,
        colorblind = {
          enable = false,
          simulate_only = false,
          severity = {
            protan = 0,
            deutan = 0,
            tritan = 0,
          },
        },
        styles = {
          comments = "NONE",
          conditionals = "NONE",
          constants = "NONE",
          functions = "NONE",
          keywords = "NONE",
          numbers = "NONE",
          operators = "NONE",
          strings = "NONE",
          types = "NONE",
          variables = "NONE",
        },
        inverse = {
          match_paren = false,
          visual = false,
          search = false,
        },
        modules = {
          -- Enable/disable plugin support here if needed
          -- e.g., telescope = true, gitsigns = true, lualine = true
        },
      },
      -- Uncomment the section below to override palettes
      -- palettes = {
      --     all = {
      --         red = "#ff0000",
      --     },
      --     nightfox = {
      --         red = "#c94f6d",
      --     },
      --     dayfox = {
      --         blue = { base = "#4d688e", bright = "#4e75aa", dim = "#485e7d" },
      --     },
      --     nordfox = {
      --         bg1 = "#2e3440",
      --         sel0 = "#3e4a5b",
      --         sel1 = "#4f6074",
      --         comment = "#60728a",
      --     },
      -- },
      palettes = {},
      specs = {},
      groups = {},
    })

    -- Apply colorscheme after setup
    vim.cmd("colorscheme carbonfox")
  end,
}
