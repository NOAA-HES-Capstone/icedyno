# IceDyno Dev Workflow

This is where we should document how we should merge/rebase/squash/etc and things we should know while working.

## Resolving rebase conflicts with pixi.lock
You will only enounter this if you have added/removed dependencies and main has received commits since you first branched that included new/removed dependencies.

If you encounter this, please make sure that the pixi.toml contains the (non-duplicated) additions from your commits and main's, then delete the pixi.lock and run `pixi install` to regnerate the lock file given both sets of dependencies.
