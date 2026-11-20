#!/bin/bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

helper_dir="$tmp/SetupHelper/HelperResources"
mock_bin="$tmp/bin"
mkdir -p "$helper_dir" "$mock_bin"

# Replace only the absolute SetupHelper include path in a temporary copy.
sed "s#source \"/data/SetupHelper/HelperResources/IncludeHelpers\"#source \"$helper_dir/IncludeHelpers\"#" \
    "$repo_root/setup" > "$tmp/setup"
chmod +x "$tmp/setup"

cat > "$helper_dir/IncludeHelpers" <<'MOCK'
scriptAction="${MOCK_ACTION:-INSTALL}"
EXIT_SUCCESS=0
EXIT_ERROR=1
installFailed=false
installPreChecks=true

standardActionPrompt() {
    echo "PROMPT_CALLED"
    scriptAction="${MOCK_PROMPT_ACTION:-INSTALL}"
}

setInstallFailed() {
    installFailed=true
    echo "PREFLIGHT_FAILURE: installPreChecks=$installPreChecks reason=$*"
}

logMessage() {
    echo "LOG: $*"
}

endScript() {
    echo "ENDSCRIPT: action=$scriptAction args=$*"
    if $installFailed; then
        exit 1
    fi
    exit 0
}
MOCK

cat > "$mock_bin/python3" <<'MOCK'
#!/bin/sh
exit "${MOCK_PYTHON_EXIT:-0}"
MOCK
cat > "$mock_bin/multilog" <<'MOCK'
#!/bin/sh
exit 0
MOCK
chmod +x "$mock_bin/python3" "$mock_bin/multilog"

# 1. Successful install reaches SetupHelper's service installation action.
success_output="$(PATH="$mock_bin:$PATH" MOCK_ACTION=INSTALL MOCK_PYTHON_EXIT=0 bash "$tmp/setup")"
grep -q "ENDSCRIPT: action=INSTALL args=INSTALL_SERVICES" <<< "$success_output"

# 2. Failed preflight leaves installPreChecks=true and reports failure.
set +e
failure_output="$(PATH="$mock_bin:$PATH" MOCK_ACTION=INSTALL MOCK_PYTHON_EXIT=1 bash "$tmp/setup" 2>&1)"
failure_status=$?
set -e
test "$failure_status" -ne 0
grep -q "PREFLIGHT_FAILURE: installPreChecks=true" <<< "$failure_output"
grep -q "ENDSCRIPT: action=INSTALL args=INSTALL_SERVICES" <<< "$failure_output"

# 3. Uninstall skips install-only preflight and reaches SetupHelper cleanup.
uninstall_output="$(PATH="$mock_bin:$PATH" MOCK_ACTION=UNINSTALL bash "$tmp/setup")"
grep -q "ENDSCRIPT: action=UNINSTALL args=INSTALL_SERVICES" <<< "$uninstall_output"

# 4. PackageManager CHECK exits without prompting or attempting installation.
check_output="$(PATH="$mock_bin:$PATH" MOCK_ACTION=CHECK bash "$tmp/setup")"
if grep -q "ENDSCRIPT\|PROMPT_CALLED" <<< "$check_output"; then
    echo "CHECK unexpectedly entered install/uninstall flow" >&2
    exit 1
fi

# 5. Interactive prompt is used only when SetupHelper has not selected an action.
prompt_output="$(PATH="$mock_bin:$PATH" MOCK_ACTION=NONE MOCK_PROMPT_ACTION=UNINSTALL bash "$tmp/setup")"
grep -q "PROMPT_CALLED" <<< "$prompt_output"
grep -q "ENDSCRIPT: action=UNINSTALL args=INSTALL_SERVICES" <<< "$prompt_output"

echo "SetupHelper mocked control-flow tests passed (install, preflight failure, uninstall, CHECK, interactive prompt)."
