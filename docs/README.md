# Building the EDRIXS documentation

The documentation imports the compiled `edrixs.fedrixs` extension. Install the
package and documentation dependencies before running Sphinx:

```bash
python -m pip install -r requirements-dev.txt
python -m pip install .
bash scripts/build-docs.sh
```

The HTML output is written to `docs/build/html`. To preview it locally, run:

```bash
python -m http.server --directory docs/build/html 8000
```

and open <http://localhost:8000>. A standalone build displays the installed
package version. The version dropdown is populated only when the build is part
of an assembled versioned site.

## Published versions

GitHub Pages uses these paths:

- `/edrixs/` redirects to `/edrixs/stable/`;
- `/edrixs/stable/` contains the latest non-prerelease;
- `/edrixs/dev/` contains the current `master` documentation; and
- `/edrixs/X.Y.Z/` contains an immutable release build.

A push to `master` updates `dev`. Publishing a GitHub release creates its
immutable version and, unless it is a prerelease, updates `stable`. Historical
versions can be built with the workflow's manual `ref`, `docs_version`, and
`make_stable` inputs.

The publishing workflow is self-initializing. On a push to `master`, it compares
the version recorded in `stable-version.txt` with GitHub's latest
non-prerelease. If `stable` is missing or outdated, it builds that release tag
and creates or repairs the immutable release, the `stable` alias, and the root
redirect before deploying `dev`.
