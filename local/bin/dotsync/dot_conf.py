# ────────────────────── CONFIG ──────────────────────
dots_name = "Polka"
secret_dots = "~/Lit/docs/base"
skip_patterns = [
    ".git/**",
    "__pycache__/**",
    ".DS_Store",
    "*.pyc",
]
individual_dirs = [
    "config/systemd/user",
    "config/nvim",
    "local/bin",
]
individual_items = [
    # ──────────────── TASK WARRIOR ────────────────
    {
        "src": f"{secret_dots}/task/taskchampion.sqlite3",
        "dest": "~/.config/task/taskchampion.sqlite3",
    },
    # ──────────────── ZSH HISTORY ─────────────────
    {
        "src": f"{secret_dots}/zsh_history",
        "dest": "~/.config/zsh/.zsh_history",
    },
    # ─────────────────── FONTS ───────────────────
    {
        "src": f"{secret_dots}/fonts/calibri.ttf",
        "dest": "~/.local/share/fonts/calibri.ttf",
    },
    {
        "src": f"{secret_dots}/fonts/calibrib.ttf",
        "dest": "~/.local/share/fonts/calibrib.ttf",
    },
    {
        "src": f"{secret_dots}/fonts/calibrii.ttf",
        "dest": "~/.local/share/fonts/calibrii.ttf",
    },
    {
        "src": f"{secret_dots}/fonts/calibril.ttf",
        "dest": "~/.local/share/fonts/calibril.ttf",
    },
    {
        "src": f"{secret_dots}/fonts/calibrili.ttf",
        "dest": "~/.local/share/fonts/calibrili.ttf",
    },
    {
        "src": f"{secret_dots}/fonts/calibriz.ttf",
        "dest": "~/.local/share/fonts/calibriz.ttf",
    },
    {
        "src": f"{secret_dots}/fonts/times.ttf",
        "dest": "~/.local/share/fonts/times.ttf",
    },
    {
        "src": f"{secret_dots}/fonts/timesbd.ttf",
        "dest": "~/.local/share/fonts/timesbd.ttf",
    },
    {
        "src": f"{secret_dots}/fonts/timesbi.ttf",
        "dest": "~/.local/share/fonts/timesbi.ttf",
    },
    {
        "src": f"{secret_dots}/fonts/timesi.ttf",
        "dest": "~/.local/share/fonts/timesi.ttf",
    },
]


