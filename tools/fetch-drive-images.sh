#!/usr/bin/env bash
#
# Download A1 Lawn Care's photography from the client's shared Google Drive
# folder into assets/img/.
#
#   https://drive.google.com/drive/folders/1T1C1f4PuEdVM7r1dQ7ACiwBtlWEUJccK
#
# The files are already WebP and already sized for the web, so they are
# committed as-is. Run from anywhere:
#
#   bash tools/fetch-drive-images.sh
#
# Requires only curl. The folder must remain shared as "anyone with the link".

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$REPO_ROOT/assets/img"
mkdir -p "$DEST"

# <drive-file-id>  <destination filename>
MANIFEST=$(cat <<'EOF'
1-eAXBfc3Qo4PLxBN5JixKGBfRDckTviN  a1-lawn-care-logo.webp
1oU3e_m_KW3K_4tBEtO0hQKkn3R5zhr2j  ndis-registered-provider-logo.webp
1Zgk0zVjI_bqoNt3bB6EOMulszKs3jktK  gallery-01.webp
1t4_zGpSEoL_IQW2V_uOUt2kom_-iD4hZ  gallery-02.webp
1poTJ0dTb4P35ErmHyHiYrFNovdBqItKC  gallery-03.webp
1G4R-vxYzin4IqEPoBfVCbH5jKZQzYLoa  gallery-04.webp
1WRA3lCgxkE5uk8LgdBJj062V9IqkGK0f  gallery-05.webp
1gC54HHwqNbY-6ZWchBEbl_b9gngHU4kK  gallery-06.webp
1V-qkRyNGll035xScv9JUMhzQLjRne9sN  gallery-07.webp
1mH19IInCKXY04c1LZ_fZ2t8BfE26kLMy  gallery-08.webp
1quSIjoQdccHVKwtN1NXJV16ROhrB8IL7  about-a1-lawn-care.webp
1I1HRhwNyxFnaYFkagUMB0RKW3hJJZkcI  gardener-at-work.webp
EOF
)

fetch() {
  local id="$1" name="$2" out="$DEST/$2" tmp
  tmp="$(mktemp)"

  for url in \
    "https://drive.usercontent.google.com/download?id=${id}&export=download" \
    "https://drive.google.com/uc?export=download&id=${id}"
  do
    if curl -fsSL --max-time 60 -o "$tmp" "$url" 2>/dev/null; then
      # Reject Google's HTML interstitial / error pages.
      if head -c 4 "$tmp" | grep -q 'RIFF'; then
        mv "$tmp" "$out"
        printf '  ok    %-38s %s bytes\n' "$name" "$(wc -c < "$out" | tr -d ' ')"
        return 0
      fi
    fi
  done

  rm -f "$tmp"
  printf '  FAIL  %-38s (id %s)\n' "$name" "$id"
  return 1
}

echo "Fetching A1 Lawn Care images into assets/img/"
failed=0
while read -r id name; do
  [ -z "${id:-}" ] && continue
  fetch "$id" "$name" || failed=$((failed + 1))
done <<< "$MANIFEST"

echo
if [ "$failed" -gt 0 ]; then
  echo "$failed file(s) could not be downloaded."
  echo "Check that the Drive folder is still shared as 'anyone with the link'."
  exit 1
fi
echo "All images downloaded."
