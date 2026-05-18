#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <version>"
  echo "Example: $0 0.1.0"
  exit 1
fi

version="$1"
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
name="cloaken-${version}"
out_dir="${repo_root}/dist"
archive="${out_dir}/${name}.tar.gz"

mkdir -p "${out_dir}"

# Create release archive while excluding local git metadata and artifacts.
tar \
  --exclude='.git' \
  --exclude='dist' \
  -czf "${archive}" \
  -C "${repo_root}" \
  .

sha_value="$(shasum -a 256 "${archive}" | awk '{print $1}')"

cat <<EOF
Archive: ${archive}
SHA256:  ${sha_value}

Update Formula/cloaken.rb:
- url "https://github.com/YOUR_GITHUB_USERNAME/cloaken/archive/refs/tags/v${version}.tar.gz"
- sha256 "${sha_value}"
- version "${version}"
EOF
