vim.g.mapleader = ' '
vim.g.maplocalleader = ' '
vim.g.have_nerd_font = true
vim.g.lazyvim_python_lsp = 'ty'
vim.g.lazyvim_python_ruff = 'ruff'
vim.o.cmdheight = 0
vim.o.number = true
vim.o.relativenumber = true
vim.o.cursorline = true
vim.o.mouse = 'a'
vim.o.showmode = false
vim.o.ignorecase = true
vim.o.wrap = false
vim.o.smartcase = true
vim.o.undofile = true
vim.o.confirm = true
vim.o.expandtab = true
vim.o.smartindent = true
vim.o.smoothscroll = true
vim.o.shiftround = true
vim.o.shiftwidth = 2
vim.o.grepprg = 'rg --vimgrep'
vim.o.scrolloff = 4
vim.o.sidescrolloff = 8
vim.o.inccommand = 'nosplit'
vim.o.tabstop = 2
vim.o.softtabstop = 2
vim.o.clipboard = 'unnamedplus'
vim.o.breakindent = true
vim.o.signcolumn = 'yes'
vim.o.updatetime = 250
vim.o.timeoutlen = 300
vim.o.splitright = true
vim.o.splitbelow = true
vim.o.list = true
vim.treesitter.language.register('xml', { 'svg', 'xslt' })
vim.keymap.set({ 'n', 'v' }, '<ScrollWheelLeft>', 'zh', { silent = true })
vim.keymap.set({ 'n', 'v' }, '<ScrollWheelRight>', 'zl', { silent = true })
vim.keymap.set('n', '<Esc>', '<cmd>nohlsearch<CR>')
vim.keymap.set('n', '<leader>q', vim.diagnostic.setqflist, { desc = 'Open diagnostic [Q]uickfix list' })
vim.keymap.set('t', '<Esc><Esc>', '<C-\\><C-n>', { desc = 'Exit terminal mode' })
vim.keymap.set('n', '<C-h>', '<C-w><C-h>', { desc = 'Move focus to the left window' })
vim.keymap.set('n', '<C-l>', '<C-w><C-l>', { desc = 'Move focus to the right window' })
vim.keymap.set('n', '<C-j>', '<C-w><C-j>', { desc = 'Move focus to the lower window' })
vim.keymap.set('n', '<C-k>', '<C-w><C-k>', { desc = 'Move focus to the upper window' })
vim.keymap.set({ 'n', 'v' }, '<C-s>', '<cmd>w<cr>', {
  desc = 'Save file',
})
vim.keymap.set('i', '<C-s>', '<Esc><cmd>w<cr>a', {
  desc = 'Save file',
})
vim.api.nvim_create_autocmd('TextYankPost', {
  desc = 'Highlight when yanking (copying) text',
  group = vim.api.nvim_create_augroup('highlight-yank', { clear = true }),
  callback = function()
    vim.hl.on_yank()
  end,
})
local lazypath = vim.fn.stdpath 'data' .. '/lazy/lazy.nvim'
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  local lazyrepo = 'https://github.com/folke/lazy.nvim.git'
  local out = vim.fn.system { 'git', 'clone', '--filter=blob:none', '--branch=stable', lazyrepo, lazypath }
  if vim.v.shell_error ~= 0 then
    error('Error cloning lazy.nvim:\n' .. out)
  end
end
---@type vim.Option
local rtp = vim.opt.rtp
rtp:prepend(lazypath)
require('lazy').setup {
  require 'plugins.whichkey',
  require 'plugins.conform',
  require 'plugins.treesitter',
  require 'plugins.onedark',
  require 'plugins.snacks',
  require 'plugins.blinkcmp',
  require 'plugins.mini',
  require 'plugins.lualine',
  require 'plugins.highlight-colors',
  require 'plugins.todo',
}
vim.lsp.config('*', {
  capabilities = {
    textDocument = {
      semanticTokens = {
        multilineTokenSupport = true,
      }
    }
  },
  root_markers = { '.git' },
})
vim.lsp.enable('lua_ls')
vim.lsp.enable('ty')
vim.lsp.enable('ruff')
-- The line beneath this is called `modeline`. See `:help modeline`
-- vim: ts=2 sts=2 sw=2 et
