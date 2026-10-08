set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
make check
