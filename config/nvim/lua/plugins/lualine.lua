return {
  {
    "nvim-lualine/lualine.nvim",
    event = "VeryLazy",
    init = function()
      vim.g.lualine_laststatus = vim.o.laststatus
      if vim.fn.argc(-1) > 0 then
        vim.o.statusline = " " -- empty statusline until lualine loads
      else
        vim.o.laststatus = 0 -- hide statusline on dashboard / starter
      end
    end,
    opts = function()
      vim.o.laststatus = vim.g.lualine_laststatus
      local colors = {
        blue = "#0077FF",
        cyan = "#00ff99",
        black = "#1b1c21",
        white = "#F4F5F6",
        red = "#ff3232",
        violet = "#33ccff",
        grey = "#191a1f",
        green = "#828385",
      }
      local bubbles_theme = {
        normal = {
          a = { fg = colors.black, bg = colors.violet },
          b = { fg = colors.white, bg = colors.grey },
          c = { fg = colors.white },
        },
        insert = { a = { fg = colors.black, bg = colors.blue } },
        visual = { a = { fg = colors.black, bg = colors.cyan } },
        replace = { a = { fg = colors.black, bg = colors.red } },
        inactive = {
          a = { fg = colors.white, bg = colors.black },
          b = { fg = colors.white, bg = colors.black },
          c = { fg = colors.white },
        },
      }
      return {
        options = {
          theme = bubbles_theme,
          globalstatus = vim.o.laststatus == 3,
          component_separators = "",
          section_separators = { left = "", right = "" },

          disabled_filetypes = {
            statusline = {
              "dashboard",
              "alpha",
              "ministarter",
              "snacks_dashboard",
            },
          },
        },
        sections = {
          lualine_a = {
            { "mode", separator = { left = "" }, right_padding = 2 },
          },
          lualine_b = {
            {
              "buffers",
              show_filename_only = true,
              hide_filename_extension = true,
              show_modified_status = true,
              max_length = vim.o.columns * 2 / 3,
              filetype_names = {
                TelescopePrompt = "Telescope",
                dashboard = "Dashboard",
                packer = "Packer",
                fzf = "FZF",
                alpha = "Alpha",
              },
              buffers_color = {
                active = { fg = colors.cyan },
                inactive = { fg = colors.green },
              },
              symbols = {
                modified = " ●",
                alternate_file = "#",
                directory = "",
              },
            },
          },
          lualine_c = { "%=" },
          lualine_x = {},
          lualine_y = { "branch", "filetype" },
          lualine_z = {
            { "filename", separator = { right = "" }, left_padding = 2 },
          },
        },
        inactive_sections = {
          lualine_a = {},
          lualine_b = {},
          lualine_c = {},
          lualine_x = {},
          lualine_y = {},
          lualine_z = { "filename" },
        },
        extensions = { "neo-tree", "lazy", "fzf" },
      }
    end,
  },
}
