
# Old
# export NQX_ROOT="/mnt/beegfs/project/ndqm/shared_utilities/nqx"
# export NQX_EXE="$NQX_ROOT/bin/nqx_exe"

__nqx_exe() (
    "$NQX_EXE" "$@"
)

__nqx_hashr() {
    if [ -n "${ZSH_VERSION:+x}" ]; then
        \rehash
    elif [ -n "${POSH_VERSION:+x}" ]; then
        :  # pass
    else
        \hash -r
    fi
}

__nqx_activate() {
    if [ -n "${CONDA_PS1_BACKUP:+x}" ]; then
        # Handle transition from shell activated with conda <= 4.3 to a subsequent activation
        # after conda updated to >= 4.4. See issue #6173.
        PS1="$CONDA_PS1_BACKUP"
        \unset CONDA_PS1_BACKUP
    fi
    \local ask_nqx
    ask_nqx="$(PS1="${PS1:-}" __nqx_exe "$@")" || \return
    \eval "$ask_nqx"
    __nqx_hashr
}

__nqx_reactivate() {
    \local ask_nqx
    ask_nqx="$(PS1="${PS1:-}" __nqx_exe reactivate)" || \return
    \eval "$ask_nqx"
    __nqx_hashr
}

nqx() {
    \local cmd="${1-__missing__}"
    case "$cmd" in
        activate|deactivate)
            __nqx_activate "$@"
            ;;
        install|update|upgrade|remove|uninstall)
            __nqx_exe "$@" || \return
            __nqx_reactivate
            ;;
        *)
            __nqx_exe "$@"
            ;;
    esac
}

if [ -z "${NQX_SHLVL+x}" ]; then
    \export NQX_SHLVL=0

    # We're not allowing PS1 to be unbound. It must at least be set.
    # However, we're not exporting it, which can cause problems when starting a second shell
    # via a first shell (i.e. starting zsh from bash).
    if [ -z "${PS1+x}" ]; then
        PS1=
    fi
fi
