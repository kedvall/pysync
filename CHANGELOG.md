# CHANGELOG


## v0.4.0 (2025-03-31)

### Features

- **support-package-extras**: Support package extras; Bump min Python version down to 3.11
  ([`647a011`](https://github.com/kedvall/pysync/commit/647a011cad40608c50240e7480dc754deb737eae))


## v0.3.7 (2025-03-17)

### Bug Fixes

- **cleanup**: Clean up unused docs and .envrc
  ([`60af802`](https://github.com/kedvall/pysync/commit/60af802400064f41c6ef65aa9b490105ea57b0f3))


## v0.3.6 (2025-03-17)

### Bug Fixes

- **release-as-standalone**: Release as standalone (vs onefile)
  ([`4206413`](https://github.com/kedvall/pysync/commit/420641364ead2d7ef66da633035bbcce2014b3db))

- **revert-standalone**: Revert standalone release; Fix lagging version
  ([`7d1ec04`](https://github.com/kedvall/pysync/commit/7d1ec044de0f237a9ec5c29ca7346e0535c1b1e1))

Revert standalone


## v0.3.5 (2025-03-17)

### Bug Fixes

- **fix-outdated-version**: Fix outdated executable version
  ([`a7ca6dd`](https://github.com/kedvall/pysync/commit/a7ca6dd406f7169f8dd6880b89572746befa8d84))

- **fix-sed**: Fix sed command
  ([`98a19b2`](https://github.com/kedvall/pysync/commit/98a19b21f85d8772c684f852343c4e4ff81ed284))

- **fix-sed-env-var**: Fix sed env var
  ([`087edbd`](https://github.com/kedvall/pysync/commit/087edbd511c27d5b785c15910f16625ecfa5c4e0))

- **use-python-update-ver**: Use python to update release version in executable
  ([`2b39f88`](https://github.com/kedvall/pysync/commit/2b39f885b099634fea7827c60cbc16a343147468))


## v0.3.4 (2025-03-17)

### Bug Fixes

- **fix-homebrew-release-url**: Fix homebrew release url; Fix uv lock sync on release
  ([`bfc7f37`](https://github.com/kedvall/pysync/commit/bfc7f37b953ddd7861bacc748db505b5e1c9836a))


## v0.3.3 (2025-03-17)

### Bug Fixes

- **fix-homebrew-release-version**: Fix Homebrew release version
  ([`c9d1ca5`](https://github.com/kedvall/pysync/commit/c9d1ca5816bf3720be076d30cff831126fe6b763))

Fix release version


## v0.3.2 (2025-03-17)

### Bug Fixes

- **update-readme**: Update readme
  ([`bd424ea`](https://github.com/kedvall/pysync/commit/bd424eafa07d1068156387fb01b9ccaffd5937a9))


## v0.3.1 (2025-03-17)

### Bug Fixes

- **alternative-ccache-disable**: Try alternative method of disabling ccache download
  ([`09cc44d`](https://github.com/kedvall/pysync/commit/09cc44df9dc90152418cddd66112768a0bae3b80))

- **fix-ccache-disable-download**: Fix ccache null pipe
  ([`b7bd135`](https://github.com/kedvall/pysync/commit/b7bd135ba17d37c4538ff439c870d850987514fc))

Fix cchace dev/null pipe

- **fix-formulae-release**: Fix Homebrew formulae release; Disable ccache download
  ([`0d8e33c`](https://github.com/kedvall/pysync/commit/0d8e33c3427814d09aca6851692ec823e8db030d))


## v0.3.0 (2025-03-17)

### Features

- **support-version-arg**: Support --version arg and Homebrew formulae
  ([`012c380`](https://github.com/kedvall/pysync/commit/012c380dc6d77644da255a3b26be86650cc6e4c6))

Support version arg; Support Homebrew formulae


## v0.2.2 (2025-03-17)

### Bug Fixes

- **fix-packaging**: Fix packaging
  ([`28ce899`](https://github.com/kedvall/pysync/commit/28ce899054aaf10caf716bb06f6665e01a024d2f))

- **package-as-tar**: Release as .tar.gz
  ([`4592c04`](https://github.com/kedvall/pysync/commit/4592c04d26a0f7224bf32b41ae983327a745d910))

Package release as .tar.gz


## v0.2.1 (2025-03-14)

### Bug Fixes

- **write-readme**: Fix re-locking print and write a readme
  ([`a5e4aa4`](https://github.com/kedvall/pysync/commit/a5e4aa45287f06eb748e16f93a3893e755191090))

Write readme


## v0.2.0 (2025-03-14)

### Features

- **fix-initial-uv-arg**: Support uv arg passthrough with implicit workdir
  ([`1b2326b`](https://github.com/kedvall/pysync/commit/1b2326b33208cae7c0c404a89dc722401e65d9b9))

Fix initial uv arg


## v0.1.20 (2025-03-14)

### Bug Fixes

- **disable-download-prompt**: Disable ccache download prompt and other minor fixes
  ([`88df1c6`](https://github.com/kedvall/pysync/commit/88df1c637f42274715bfffb4bd14bd1f8c366342))

Disable ccache download prompt

- **fix-nul-redirect**: Remove null redirect and enable ccache download
  ([`c6da106`](https://github.com/kedvall/pysync/commit/c6da106295eeacfb0d58a22486b29eb98cc422cc))

- **fix-tolower**: Fix to-lower for os
  ([`eeea664`](https://github.com/kedvall/pysync/commit/eeea6642bcb38b6dbee993a330291b640f749afb))

Fix to-lower


## v0.1.19 (2025-03-13)

### Bug Fixes

- **fix-artifact-names**: Fix broken artifact names
  ([`b64588b`](https://github.com/kedvall/pysync/commit/b64588b7a96c302745263d698198b910e19b8e5c))

Fix artifact names


## v0.1.18 (2025-03-13)

### Bug Fixes

- **fix-ci-version**: Fix version in CI
  ([`a25d02f`](https://github.com/kedvall/pysync/commit/a25d02f9a3a46f4294d29bdd27de8bb64a4c41da))

Fix semantic version; Assume yes for Nuitka downlaods

- **fix-env-var-fix**: Fix partial env var name change
  ([`a54430f`](https://github.com/kedvall/pysync/commit/a54430f311b5e36312ac1c2d9064f04a1e672fdc))

- **revert-anti-bloat-removal**: Enable anti-bloat to fix import error in CI
  ([`21060cc`](https://github.com/kedvall/pysync/commit/21060cc675008b7b0118707981024f029c7a5769))

- **use-nuitka**: Use Nuitka for building releases
  ([`9f5b1ea`](https://github.com/kedvall/pysync/commit/9f5b1ea910945f75a1f38dc17983001456efdd9f))


## v0.1.17 (2025-03-12)

### Bug Fixes

- **fix-updated-list**: Fix updated dependency list
  ([`4fe41de`](https://github.com/kedvall/pysync/commit/4fe41de0244ccd0eec847dc3247e34b5f9d698d1))

Fix updated list


## v0.1.16 (2025-03-12)

### Bug Fixes

- **fix-pyinstaller**: Fix pyinstaller
  ([`ba4e4c0`](https://github.com/kedvall/pysync/commit/ba4e4c0c419be7fdad0e2a48fe133b036cde77bf))

Fix pyinstaller cmd

- **use-uv-in-release**: Use uv in release
  ([`92023f2`](https://github.com/kedvall/pysync/commit/92023f2836c7c0f6e9222aaace7cebb515d455c2))

Use uv to set up and run executable build; Fix GH_TOKEN env var


## v0.1.15 (2025-03-12)

### Bug Fixes

- **fix-multiline-run**: Fix multiline run
  ([`0938cb7`](https://github.com/kedvall/pysync/commit/0938cb7a8af2417ba60c3c23a7a9ff6c21206b2c))

Fix multi-line run

- **release-on-merge**: Release on merge
  ([`5dd454f`](https://github.com/kedvall/pysync/commit/5dd454ffbe8101d5551b357e38f3ac6e55a21579))

- **test-release**: Test release
  ([`7b5b001`](https://github.com/kedvall/pysync/commit/7b5b001867656e8816e0daf0edc1022d26ae9e45))

fix(test-release): Test release


## v0.1.14 (2025-03-12)


## v0.1.13 (2025-03-12)


## v0.1.12 (2025-03-12)


## v0.1.11 (2025-03-12)


## v0.1.10 (2025-03-12)


## v0.1.9 (2025-03-12)


## v0.1.8 (2025-03-12)


## v0.1.7 (2025-03-12)


## v0.1.6 (2025-03-12)


## v0.1.5 (2025-03-12)


## v0.1.4 (2025-03-12)


## v0.1.3 (2025-03-12)


## v0.1.2 (2025-03-12)


## v0.1.1 (2025-03-12)


## v0.1.0 (2025-03-12)
