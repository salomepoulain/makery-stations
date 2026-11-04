#!/usr/bin/env python3
"""Merge pantry settings into your VS Code user settings and install the extensions.

Usage:  python3 install.py                 # style + functionality + addons
        python3 install.py style functionality

Pantry keys overwrite existing keys. Your other settings are kept at the bottom.
The old settings.json is backed up next to it first.
With the style pack, the fonts in fonts/ are installed for the current user
(macOS, Windows, Linux).
"""
import json, os, re, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKS = sys.argv[1:] or ["style", "functionality", "addons"]


def strip_jsonc(text):
    """Remove // and /* */ comments outside strings, and trailing commas."""
    out, i, in_str = [], 0, False
    while i < len(text):
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\":
                out.append(text[i + 1]); i += 2; continue
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True; out.append(c)
        elif text.startswith("//", i):
            i = text.find("\n", i); i = len(text) if i < 0 else i; continue
        elif text.startswith("/*", i):
            i = text.find("*/", i) + 2; continue
        else:
            out.append(c)
        i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def load(path):
    return json.loads(strip_jsonc(path.read_text())) if path.exists() else {}


def body(path):
    """The text between the outer braces, so the MARK comments survive."""
    text = path.read_text()
    return text[text.index("{") + 1 : text.rindex("}")].strip().rstrip(",")


def user_settings_path():
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/Code/User/settings.json"
    if os.name == "nt":
        return Path(os.environ["APPDATA"]) / "Code/User/settings.json"
    return Path.home() / ".config/Code/User/settings.json"


def merge(packs, existing):
    pantry_keys, parts = set(), []
    for pack in packs:
        f = HERE / pack / "settings.json"
        pantry_keys |= set(load(f))
        parts.append(f"    // ===== {pack} =====\n    {body(f)}")
    rest = {k: v for k, v in existing.items() if k not in pantry_keys}
    if rest:
        dumped = json.dumps(rest, indent=4, ensure_ascii=False)
        parts.append("    // ===== your own settings =====\n    " + dumped[1:-1].strip())
    return "{\n" + ",\n\n".join(parts) + "\n}\n"


def install_fonts():
    """Per-user install, no admin needed. Skips fonts that are already there."""
    fonts = sorted((HERE / "fonts").glob("*.ttf"))
    if sys.platform == "darwin":
        dest = Path.home() / "Library/Fonts"
    elif os.name == "nt":
        dest = Path(os.environ["LOCALAPPDATA"]) / "Microsoft/Windows/Fonts"
    else:
        dest = Path.home() / ".local/share/fonts"
    dest.mkdir(parents=True, exist_ok=True)
    new = [f for f in fonts if not (dest / f.name).exists()]
    for f in new:
        shutil.copy2(f, dest / f.name)
        if os.name == "nt":  # Windows only sees per-user fonts that are in the registry
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows NT\CurrentVersion\Fonts", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, f"{f.stem} (TrueType)", 0, winreg.REG_SZ, str(dest / f.name))
            winreg.CloseKey(key)
    if new and sys.platform.startswith("linux") and shutil.which("fc-cache"):
        subprocess.run(["fc-cache", "-f", str(dest)], check=False)
    print(f"fonts: {len(new)} new, {len(fonts) - len(new)} already installed ({dest})")


def find_code():
    mac = "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
    return shutil.which("code") or (mac if Path(mac).exists() else None)


def main():
    target = user_settings_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        backup = target.with_name(f"settings.json.bak-{time.strftime('%Y%m%d-%H%M%S')}")
        shutil.copy2(target, backup)
        print(f"backup: {backup}")
    target.write_text(merge(PACKS, load(target)))
    print(f"settings: {target}")

    if "style" in PACKS:
        install_fonts()

    code = find_code()
    if not code:
        sys.exit("'code' not found. Install the extensions from */extensions.json by hand.")
    for pack in PACKS:
        for ext in load(HERE / pack / "extensions.json").get("recommendations", []):
            subprocess.run([code, "--install-extension", ext], check=False)


if __name__ == "__main__":
    main()
