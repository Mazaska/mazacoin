Release Process
====================

Before every release candidate:

* Update translations (ping kuwanlelenta on IRC) see [translation_process.md](https://github.com/mazaska/mazacoin/blob/master/doc/translation_process.gmd#synchronising-translations).

Before every minor and major release:

* Update [bips.md](bips.md) to account for changes since the last release.
* Update version in sources (see below)
* Write release notes (see below)

Before every major release:

* Update hardcoded [seeds](/contrib/seeds/README.md), see [this pull request](https://github.com/bitcoin/bitcoin/pull/7415) for an example.

### First time / New builders

Check out the source code in the following directory hierarchy.

    cd /path/to/your/toplevel/build
    git clone https://github.com/mazaska/gitian.sigs.git
    git clone https://github.com/mazaska/mazacoin-detached-sigs.git
    git clone https://github.com/devrandom/gitian-builder.git
    git clone https://github.com/mazaska/mazacoin.git

### Mazacoin maintainers/release engineers, update version in sources

Update the following:

- `configure.ac`:
    - `_CLIENT_VERSION_MAJOR`
    - `_CLIENT_VERSION_MINOR`
    - `_CLIENT_VERSION_REVISION`
    - Don't forget to set `_CLIENT_VERSION_IS_RELEASE` to `true`
- `src/clientversion.h`: (this mirrors `configure.ac`)
    - `CLIENT_VERSION_MAJOR`
    - `CLIENT_VERSION_MINOR`
    - `CLIENT_VERSION_REVISION`
    - Don't forget to set `CLIENT_VERSION_IS_RELEASE` to `true`
- `doc/README.md` and `doc/README_windows.txt`
- `doc/Doxyfile`: `PROJECT_NUMBER` contains the full version
- `contrib/gitian-descriptors/*.yml`: usually one'd want to do this on master after branching off the release - but be sure to at least do it before a new major release

Write release notes. git shortlog helps a lot, for example:

    git shortlog --no-merges v(current version, e.g. 0.8.8)..v(new version, e.g. 0.13.0)

(or ping @kuwanlelenta on IRC, he has specific tooling to generate the list of merged pulls
and sort them into categories based on labels)

Generate list of authors:

    git log --format='%aN' "$*" | sort -ui | sed -e 's/^/- /'

Tag version (or release candidate) in git

    git tag -s v(new version, e.g. 0.13.0)

### Setup and perform Gitian builds

Setup Gitian descriptors:

    pushd ./mazacoin
    export SIGNER=(your Gitian key, ie kuwanlelenta)
    export VERSION=(new version, e.g. 0.13.0)
    git fetch
    git checkout v${VERSION}
    popd

Ensure your gitian.sigs are up-to-date if you wish to gverify your builds against other Gitian signatures.

    pushd ./gitian.sigs
    git pull
    popd

Ensure gitian-builder is up-to-date:

    pushd ./gitian-builder
    git pull
    popd

### Fetch and create inputs: (first time, or when dependency versions change)

    pushd ./gitian-builder
    mkdir -p inputs
    wget -P inputs https://bitcoincore.org/cfields/osslsigncode-Backports-to-1.7.1.patch
    wget -P inputs http://downloads.sourceforge.net/project/osslsigncode/osslsigncode/osslsigncode-1.7.1.tar.gz
    popd

Create the OS X SDK tarball, see the [OS X readme](README_osx.md) for details, and copy it into the inputs directory.

### Optional: Seed the Gitian sources cache and offline git repositories

By default, Gitian will fetch source files as needed. To cache them ahead of time:

    pushd ./gitian-builder
    make -C ../mazacoin/depends download SOURCES_PATH=`pwd`/cache/common
    popd

Only missing files will be fetched, so this is safe to re-run for each build.

NOTE: Offline builds must use the --url flag to ensure Gitian fetches only from local URLs. For example:

    pushd ./gitian-builder
    ./bin/gbuild --url mazacoin=/path/to/mazacoin,signature=/path/to/sigs {rest of arguments}
    popd

The gbuild invocations below <b>DO NOT DO THIS</b> by default.

### Build and sign Mazacoin Core for Linux, Windows, and OS X:

    pushd ./gitian-builder
    ./bin/gbuild --memory 3000 --commit mazacoin=v${VERSION} ../mazacoin/contrib/gitian-descriptors/gitian-linux.yml
    ./bin/gsign --signer $SIGNER --release ${VERSION}-linux --destination ../gitian.sigs/ ../mazacoin/contrib/gitian-descriptors/gitian-linux.yml
    mv build/out/mazacoin-*.tar.gz build/out/src/mazacoin-*.tar.gz ../

    ./bin/gbuild --memory 3000 --commit mazacoin=v${VERSION} ../mazacoin/contrib/gitian-descriptors/gitian-win.yml
    ./bin/gsign --signer $SIGNER --release ${VERSION}-win-unsigned --destination ../gitian.sigs/ ../mazacoin/contrib/gitian-descriptors/gitian-win.yml
    mv build/out/mazacoin-*-win-unsigned.tar.gz inputs/mazacoin-win-unsigned.tar.gz
    mv build/out/mazacoin-*.zip build/out/mazacoin-*.exe ../

    ./bin/gbuild --memory 3000 --commit mazacoin=v${VERSION} ../mazacoin/contrib/gitian-descriptors/gitian-osx.yml
    ./bin/gsign --signer $SIGNER --release ${VERSION}-osx-unsigned --destination ../gitian.sigs/ ../mazacoin/contrib/gitian-descriptors/gitian-osx.yml
    mv build/out/mazacoin-*-osx-unsigned.tar.gz inputs/mazacoin-osx-unsigned.tar.gz
    mv build/out/mazacoin-*.tar.gz build/out/mazacoin-*.dmg ../
    popd

Build output expected:

  1. source tarball (`mazacoin-${VERSION}.tar.gz`)
  2. linux 32-bit and 64-bit dist tarballs (`mazacoin-${VERSION}-linux[32|64].tar.gz`)
  3. windows 32-bit and 64-bit unsigned installers and dist zips (`mazacoin-${VERSION}-win[32|64]-setup-unsigned.exe`, `mazacoin-${VERSION}-win[32|64].zip`)
  4. OS X unsigned installer and dist tarball (`mazacoin-${VERSION}-osx-unsigned.dmg`, `mazacoin-${VERSION}-osx64.tar.gz`)
  5. Gitian signatures (in `gitian.sigs/${VERSION}-<linux|{win,osx}-unsigned>/(your Gitian key)/`)

### Verify other gitian builders signatures to your own. (Optional)

Add other gitian builders keys to your gpg keyring

    gpg --import mazacoin/contrib/gitian-keys/*.pgp

Verify the signatures

    pushd ./gitian-builder
    ./bin/gverify -v -d ../gitian.sigs/ -r ${VERSION}-linux ../mazacoin/contrib/gitian-descriptors/gitian-linux.yml
    ./bin/gverify -v -d ../gitian.sigs/ -r ${VERSION}-win-unsigned ../mazacoin/contrib/gitian-descriptors/gitian-win.yml
    ./bin/gverify -v -d ../gitian.sigs/ -r ${VERSION}-osx-unsigned ../mazacoin/contrib/gitian-descriptors/gitian-osx.yml
    popd

### Next steps:

Commit your signature to gitian.sigs:

    pushd gitian.sigs
    git add ${VERSION}-linux/${SIGNER}
    git add ${VERSION}-win-unsigned/${SIGNER}
    git add ${VERSION}-osx-unsigned/${SIGNER}
    git commit -a
    git push  # Assuming you can push to the gitian.sigs tree
    popd

Wait for Windows/OS X detached signatures:

- Once the Windows/OS X builds each have 3 matching signatures, they will be signed with their respective release keys.
- Detached signatures will then be committed to the [mazacoin-detached-sigs](https://github.com/mazaska/mazacoin-detached-sigs) repository, which can be combined with the unsigned apps to create signed binaries.

Create (and optionally verify) the signed OS X binary:

    pushd ./gitian-builder
    ./bin/gbuild -i --commit signature=v${VERSION} ../mazacoin/contrib/gitian-descriptors/gitian-osx-signer.yml
    ./bin/gsign --signer $SIGNER --release ${VERSION}-osx-signed --destination ../gitian.sigs/ ../mazacoin/contrib/gitian-descriptors/gitian-osx-signer.yml
    ./bin/gverify -v -d ../gitian.sigs/ -r ${VERSION}-osx-signed ../mazacoin/contrib/gitian-descriptors/gitian-osx-signer.yml
    mv build/out/mazacoin-osx-signed.dmg ../mazacoin-${VERSION}-osx.dmg
    popd

Create (and optionally verify) the signed Windows binaries:

    pushd ./gitian-builder
    ./bin/gbuild -i --commit signature=v${VERSION} ../mazacoin/contrib/gitian-descriptors/gitian-win-signer.yml
    ./bin/gsign --signer $SIGNER --release ${VERSION}-win-signed --destination ../gitian.sigs/ ../mazacoin/contrib/gitian-descriptors/gitian-win-signer.yml
    ./bin/gverify -v -d ../gitian.sigs/ -r ${VERSION}-win-signed ../mazacoin/contrib/gitian-descriptors/gitian-win-signer.yml
    mv build/out/mazacoin-*win64-setup.exe ../mazacoin-${VERSION}-win64-setup.exe
    mv build/out/mazacoin-*win32-setup.exe ../mazacoin-${VERSION}-win32-setup.exe
    popd

Commit your signature for the signed OS X/Windows binaries:

    pushd gitian.sigs
    git add ${VERSION}-osx-signed/${SIGNER}
    git add ${VERSION}-win-signed/${SIGNER}
    git commit -a
    git push  # Assuming you can push to the gitian.sigs tree
    popd

### After 3 or more people have gitian-built and their results match:

- Create `SHA256SUMS.asc` for the builds, and GPG-sign it:

```bash
sha256sum * > SHA256SUMS
```

The list of files should be:
```
mazacoin-${VERSION}-aarch64-linux-gnu.tar.gz
mazacoin-${VERSION}-arm-linux-gnueabihf.tar.gz
mazacoin-${VERSION}-i686-pc-linux-gnu.tar.gz
mazacoin-${VERSION}-x86_64-linux-gnu.tar.gz
mazacoin-${VERSION}-osx64.tar.gz
mazacoin-${VERSION}-osx.dmg
mazacoin-${VERSION}.tar.gz
mazacoin-${VERSION}-win32-setup.exe
mazacoin-${VERSION}-win32.zip
mazacoin-${VERSION}-win64-setup.exe
mazacoin-${VERSION}-win64.zip
```
The `*-debug*` files generated by the gitian build contain debug symbols
for troubleshooting by developers. It is assumed that anyone that is interested
in debugging can run gitian to generate the files for themselves. To avoid
end-user confusion about which file to pick, as well as save storage
space *do not upload these to the mazacoin.net server, nor put them in the torrent*.

- GPG-sign it, delete the unsigned file:
```
gpg --digest-algo sha256 --clearsign SHA256SUMS # outputs SHA256SUMS.asc
rm SHA256SUMS
```
(the digest algorithm is forced to sha256 to avoid confusion of the `Hash:` header that GPG adds with the SHA256 used for the files)
Note: check that SHA256SUMS itself doesn't end up in SHA256SUMS, which is a spurious/nonsensical entry.

- Upload zips and installers, as well as `SHA256SUMS.asc` from last step, to the mazacoin.net server
  into `/var/www/bin/mazacoin-core-${VERSION}`

- A `.torrent` will appear in the directory after a few minutes. Optionally help seed this torrent. To get the `magnet:` URI use:
```bash
transmission-show -m <torrent file>
```
Insert the magnet URI into the announcement sent to mailing lists. This permits
people without access to `mazacoin.net` to download the binary distribution.

- Announce the release:

  - mazacoin-dev mailing list

  - mazacoin.net blog post

  - Update title of #mazacoin on Freenode IRC

  - Optionally twitter, reddit /r/Mazacoin, ... but this will usually sort out itself

  - Celebrate
