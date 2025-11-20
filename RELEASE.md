# Release Process

* Make sure that the code is in a good shape, all tests are passed etc.
* Switch to `master` branch (`$ git checkout master`).
* Run `$ make setup`
* Run `$ git diff --exit-code && git pull`
* If there were releases this month, run `$ poetry version patch`, if not upgrade minor version `$ poetry version minor`
* Run `$ ./tools/update_changelog.py` to update `CHANGELOG.md`.
* Open `CHANGELOG.md`, make sure that the generated file content looks good. Fix it if needed.
* Checkout to the branch `$ git switch -c release/vYY.MM.N`, where YY is short form of a year, MM -- month, N -- release number in this month starting with 0.
* Commit changed files. Use `Release vYY.MM.N` commit message
* Push commited changes on github using the feature branch.
* Wait for CI checks finish, make sure that all tests are passed.
* Merge your PR to master branch.
* Wait for CI checks finish, make sure that all tests are passed.
* Restart CI failed jobs in case of failed flaky tests.
* Checkout to the master branch locally `$ git checkout master`
* Make sure you have a right permissions to push master branch tags.
* After CI is green make a git tag. For version `20.6.22` the tag should be `v20.6.22` (`$ git tag -a v20.6.22 -m "Release 20.6.22"`).
* Push a new tag, e.g. `$ git push origin v20.6.22`.
* Make sure that CI is green. Restart a job for tagged commit if a flaky test is encountered.
* Open PyPI (https://pypi.org/project/apolo-all/),
  make sure that a new release is published and all needed files are awailable for downloading