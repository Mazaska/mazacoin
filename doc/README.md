Mazacoin Core 0.13.0
=====================

Setup
---------------------
[Mazacoin Core](https://www.mazacoin.net/) is the original Mazacoin client and it builds the backbone of the network. However, it downloads and stores the entire history of Mazacoin transactions (which is nearly a GB); depending on the speed of your computer and network connection, the synchronization process can take a few hours.

Running
---------------------
The following are some helpful notes on how to run Mazacoin on your native platform.

### Unix

Unpack the files into a directory and run:

- `bin/mazacoin-qt` (GUI) or
- `bin/mazacoind` (headless)

### Windows

Unpack the files into a directory, and then run mazacoin-qt.exe.

### OS X

Drag Mazacoin-Core to your applications folder, and then run Mazacoin-Core.

### Need Help?

* Ask for help on [#mazacoin](http://webchat.freenode.net?channels=mazacoin) on Freenode. If you don't have an IRC client use [webchat here](http://webchat.freenode.net?channels=mazacoin).
* Ask for help in the [Mazacoin](https://discord.gg/TZWn8kZ) Discord server.
* Ask for help in the [Mazacoin](https://t.me/mazatribe) Telegram group.

Building
---------------------
The following are developer notes on how to build Mazacoin on your native platform. They are not complete guides, but include notes on the necessary libraries, compile flags, etc.

- [OS X Build Notes](build-osx.md)
- [Unix Build Notes](build-unix.md)
- [Windows Build Notes](build-windows.md)
- [OpenBSD Build Notes](build-openbsd.md)
- [Gitian Building Guide](gitian-building.md)

Development
---------------------
The Mazacoin repo's [root README](/README.md) contains relevant information on the development process and automated testing.

- [Developer Notes](developer-notes.md)
- [Multiwallet Qt Development](multiwallet-qt.md)
- [Release Notes](release-notes.md)
- [Release Process](release-process.md)
- [Translation Process](translation_process.md)
- [Translation Strings Policy](translation_strings_policy.md)
- [Unit Tests](unit-tests.md)
- [Unauthenticated REST Interface](REST-interface.md)
- [Shared Libraries](shared-libraries.md)
- [BIPS](bips.md)
- [Dnsseed Policy](dnsseed-policy.md)
- [Benchmarking](benchmarking.md)

### Resources
* Discuss on the [BitcoinTalk](https://bitcointalk.org/) forums, in the [Altcoin Discussion board](https://bitcointalk.org/index.php?board=67.0).
* Discuss project-specific development on #mazacoin-core-dev on Freenode. If you don't have an IRC client use [webchat here](http://webchat.freenode.net/?channels=mazacoin-core-dev).
* Discuss general Mazacoin development on #mazacoin-dev on Freenode. If you don't have an IRC client use [webchat here](http://webchat.freenode.net/?channels=mazacoin-dev).

### Miscellaneous
- [Assets Attribution](assets-attribution.md)
- [Files](files.md)
- [Tor Support](tor.md)
- [Init Scripts (systemd/upstart/openrc)](init.md)

License
---------------------
Distributed under the [MIT software license](http://www.opensource.org/licenses/mit-license.php).
This product includes software developed by the OpenSSL Project for use in the [OpenSSL Toolkit](https://www.openssl.org/). This product includes
cryptographic software written by Eric Young ([eay@cryptsoft.com](mailto:eay@cryptsoft.com)), and UPnP software written by Thomas Bernard.
