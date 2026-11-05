# An lsd look-alike in plain shell and awk, for a server where lsd isn't
# installed and you may not install it. Works in bash and zsh.
#
#   ls          folders first, then files; hidden files left out
#   ls -a       the same, then a dotted line, then the hidden files
#   ls <dir>    the same for another folder
#   anything else (ls -l, ls *.py, two folders) goes to the normal ls
#
# Columns like `lsd --blocks permission,size,date,name --icon=always`.
# Icons need a Nerd Font in the terminal; the VS Code pantry's style settings
# already fall back to MesloLGM Nerd Font Mono. Needs GNU find (Linux).

unalias ls 2>/dev/null

# Turns lines of type, name, mode, size, epoch, date, link target (tab
# separated, folders first) into lsd-style rows.
_LSD_AWK='
BEGIN {
    FS = "\t"
    split("B KB MB GB TB", unit, " ")
    dots = "\033[38;5;240m··············································\033[0m"
        e["py"] = ""
        e["pyi"] = ""
        e["ipynb"] = ""
        e["sh"] = ""
        e["bash"] = ""
        e["zsh"] = ""
        e["md"] = ""
        e["txt"] = ""
        e["rst"] = ""
        e["tex"] = ""
        e["bib"] = ""
        e["pdf"] = ""
        e["json"] = ""
        e["jsonc"] = ""
        e["yml"] = ""
        e["yaml"] = ""
        e["toml"] = ""
        e["ini"] = ""
        e["cfg"] = ""
        e["conf"] = ""
        e["env"] = ""
        e["csv"] = ""
        e["tsv"] = ""
        e["xlsx"] = ""
        e["parquet"] = ""
        e["db"] = ""
        e["sqlite"] = ""
        e["sql"] = ""
        e["h5"] = ""
        e["npy"] = ""
        e["pkl"] = ""
        e["js"] = ""
        e["ts"] = ""
        e["html"] = ""
        e["css"] = ""
        e["c"] = ""
        e["h"] = ""
        e["cpp"] = ""
        e["rs"] = ""
        e["go"] = ""
        e["java"] = ""
        e["r"] = ""
        e["jl"] = ""
        e["png"] = ""
        e["jpg"] = ""
        e["jpeg"] = ""
        e["gif"] = ""
        e["svg"] = ""
        e["webp"] = ""
        e["zip"] = ""
        e["tar"] = ""
        e["gz"] = ""
        e["tgz"] = ""
        e["bz2"] = ""
        e["xz"] = ""
        e["7z"] = ""
        e["log"] = ""
        e["lock"] = ""
        e["ttf"] = ""
        e["otf"] = ""
        e["vsix"] = ""
        e["mk"] = ""
        n["makefile"] = ""
        n["dockerfile"] = ""
        n[".gitignore"] = ""
        n[".gitattributes"] = ""
        n[".git"] = ""
        n["license"] = ""
        n["readme.md"] = ""
        n[".editorconfig"] = ""
        n[".env"] = ""
}
function c(code, s) { return "\033[38;5;" code "m" s "\033[0m" }
function perm(m,    out, i, ch, t) {
    t = substr(m, 1, 1)
    if (t == "d") out = "\033[1m" c(6, "d")
    else if (t == "l") out = c(13, "l")
    else out = c(245, ".")
    for (i = 2; i <= 10; i++) {
        ch = substr(m, i, 1)
        if (ch == "r") out = out c(3, ch)
        else if (ch == "w") out = out c(1, ch)
        else if (ch == "x" || ch == "s" || ch == "t") out = out c(2, ch)
        else if (ch == "-") out = out c(245, ch)
        else out = out c(5, ch)
    }
    return out
}
function icon(name, type,    lower, k) {
    if (type == "d") return "\357\201\273"
    lower = tolower(name)
    if (lower in n) return n[lower]
    k = lower
    if (sub(/.*\./, "", k) && (k in e)) return e[k]
    return "\357\205\233"
}
{
    hidden = (substr($2, 1, 1) == ".")
    i = hidden ? ++nh : ++nv
    s = $4 + 0; u = 1
    while (s >= 1024 && u < 5) { s /= 1024; u++ }
    num = (u == 1 || s >= 10) ? sprintf("%d", s) : sprintf("%.1f", s)
    scol = ($4 < 1048576) ? 229 : ($4 < 1073741824 ? 216 : 172)
    age = now - $5
    dcol = (age < 3600) ? 40 : (age < 86400 ? 42 : 36)
    split($6, d, " ")
    date = sprintf("%s %s %2d %s %s", d[1], d[2], d[3] + 0, substr(d[4], 1, 8), d[5])
    name = icon($2, $1) " " $2
    if ($1 == "d") name = "\033[1m" c(6, name)
    else if ($1 == "l") name = c(13, name) c(245, " ⇒ ") $7
    else if (substr($3, 4, 1) == "x") name = c(2, name)
    row = perm($3) "\t" num "\t" scol "\t" unit[u] "\t" c(dcol, date) "\t" name
    if (length(num) > w) w = length(num)
    if (length(unit[u]) > uw) uw = length(unit[u])
    if (hidden) h[i] = row; else v[i] = row
}
function spaces(k,    s) { s = ""; while (k-- > 0) s = s " "; return s }
function out(row,    f) {
    split(row, f, "\t")
    print f[1] "  " spaces(w - length(f[2])) c(f[3], f[2]) " " c(f[3], f[4]) spaces(uw - length(f[4])) "  " f[5] "  " f[6]
}
END {
    for (i = 1; i <= nv; i++) out(v[i])
    if (all && nh) { if (nv) print dots; for (i = 1; i <= nh; i++) out(h[i]) }
}'

ls() {
    local all=0 dir=.
    if [ "$1" = "-a" ]; then all=1; shift; fi
    if [ $# -gt 1 ] || [ "${1#-}" != "$1" ] || { [ $# -eq 1 ] && [ ! -d "$1" ]; } \
        || ! find . -maxdepth 0 -printf '' 2>/dev/null; then
        if [ "$all" = 1 ]; then command ls --color=auto -a "$@"; else command ls --color=auto "$@"; fi
        return
    fi
    [ $# -eq 1 ] && dir=$1
    find "$dir" -mindepth 1 -maxdepth 1 \
        -printf '%y\t%f\t%M\t%s\t%T@\t%Ta %Tb %Td %TH:%TM:%TS %TY\t%l\n' 2>/dev/null \
        | awk 'BEGIN { FS = OFS = "\t" } { print ($1 == "d" ? 0 : 1), $0 }' \
        | LC_ALL=C sort -t "$(printf '\t')" -k1,1 -k3,3f \
        | cut -f2- \
        | awk -v all="$all" -v now="$(date +%s)" "$_LSD_AWK"
}
