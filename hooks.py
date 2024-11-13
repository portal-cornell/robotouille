from PyInstaller.utils.hooks import collect_submodules

# Collect all submodules from package A
hiddenimports = collect_submodules('robotouille')
print(hiddenimports)