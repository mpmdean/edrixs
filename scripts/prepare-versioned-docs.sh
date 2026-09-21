#!/bin/bash

set -euo pipefail

if [[ "$#" -ne 6 ]]; then
    echo "Usage: $0 HTML_DIR EXISTING_SITE OUTPUT_DIR VERSION MAKE_STABLE TOOLING_ROOT" >&2
    exit 2
fi

html_dir="$1"
existing_site="$2"
output_dir="$3"
docs_version="$4"
make_stable="$5"
tooling_root="$6"

if [[ ! -d "${html_dir}" || ! -f "${html_dir}/index.html" ]]; then
    echo "Documentation HTML is missing from ${html_dir}" >&2
    exit 1
fi
if [[ ! "${docs_version}" =~ ^(dev|[0-9][0-9A-Za-z._-]*)$ ]]; then
    echo "Invalid documentation version: ${docs_version}" >&2
    exit 1
fi
if [[ "${make_stable}" != "true" && "${make_stable}" != "false" ]]; then
    echo "MAKE_STABLE must be true or false" >&2
    exit 1
fi

mkdir -p "${output_dir}"
if [[ -d "${existing_site}" ]]; then
    rsync -a --exclude .git "${existing_site}/" "${output_dir}/"
fi

version_dir="${output_dir}/${docs_version}"
mkdir -p "${version_dir}"
rsync -a --delete "${html_dir}/" "${version_dir}/"

python3 "${tooling_root}/scripts/inject-docs-version.py" \
    "${version_dir}" "${docs_version}"

mkdir -p "${output_dir}/_versioning"
cp "${tooling_root}/docs/source/_static/version-switcher.css" \
    "${output_dir}/_versioning/version-switcher.css"
cp "${tooling_root}/docs/source/_static/version-switcher.js" \
    "${output_dir}/_versioning/version-switcher.js"

if [[ "${make_stable}" == "true" ]]; then
    stable_dir="${output_dir}/stable"
    mkdir -p "${stable_dir}"
    rsync -a --delete "${version_dir}/" "${stable_dir}/"
    printf '%s\n' "${docs_version}" > "${output_dir}/stable-version.txt"
fi

if [[ -f "${output_dir}/stable/index.html" ]]; then
    cp "${tooling_root}/docs/versioned-index.html" "${output_dir}/index.html"
fi

manifest="${output_dir}/versions.json"
stable_version=""
if [[ -f "${output_dir}/stable-version.txt" ]]; then
    stable_version="$(<"${output_dir}/stable-version.txt")"
fi

{
    echo '{'
    echo '  "versions": ['
    separator=""
    if [[ -d "${output_dir}/stable" ]]; then
        printf '%s    {"name": "stable", "title": "stable (%s)", "url": "stable/"}' \
            "${separator}" "${stable_version:-latest}"
        separator=",\n"
    fi
    if [[ -d "${output_dir}/dev" ]]; then
        printf '%b    {"name": "dev", "title": "development", "url": "dev/"}' \
            "${separator}"
        separator=",\n"
    fi
    while IFS= read -r published_version; do
        printf '%b    {"name": "%s", "title": "%s", "url": "%s/"}' \
            "${separator}" "${published_version}" "${published_version}" "${published_version}"
        separator=",\n"
    done < <(
        find "${output_dir}" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; \
            | grep -E '^[0-9][0-9A-Za-z._-]*$' \
            | sort -Vr || true
    )
    echo
    echo '  ]'
    echo '}'
} > "${manifest}"
