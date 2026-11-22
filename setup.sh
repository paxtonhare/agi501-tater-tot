#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
mkdir -p .deps
cd .deps
export LC_ALL=C.UTF-8

checkout() {
    local name=$1 url=$2 revision=$3
    if [[ ! -d $name ]]; then git clone "$url" "$name"; fi
    git -C "$name" checkout --detach "$revision"
}
checkout PeTTa https://github.com/trueagi-io/PeTTa 429e22916630ea6fd1f24a3d45869f0082a85852
checkout MetaMo https://github.com/iCog-Labs-Dev/MetaMo bf97e50a68aa5059457092dfbe70699b7dd1dbe2

version=9.3.36
archive=swipl-$version.tar.gz
if [[ ! -f $archive ]]; then
    curl -fsSL "https://www.swi-prolog.org/download/devel/src/$archive" -o "$archive.tmp"
    mv "$archive.tmp" "$archive"
fi
printf '%s  %s\n' 7a7ed88e3380e176eb19d219e59fa7faaa10ff34b62227741d0aab58ec6b710f "$archive" | sha256sum --check
if [[ ! -d swipl-$version ]]; then tar xzf "$archive"; fi
cmake -S "swipl-$version" -B swi-build -G Ninja \
    -DCMAKE_INSTALL_PREFIX="$PWD/swi" -DINSTALL_DOCUMENTATION=OFF \
    -DSWIPL_PACKAGES=OFF '-DSWIPL_PACKAGE_LIST=swipy;clib;pcre' \
    -DPython3_EXECUTABLE=/usr/bin/python3
cmake --build swi-build --parallel "${JOBS:-4}"
cmake --install swi-build
swi/bin/swipl -q -g 'use_module(library(janus)),py_call(numpy:zeros(1),_),halt'
