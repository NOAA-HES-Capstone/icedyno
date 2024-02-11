# Setup
To get started, clone the repo, checkout this branch, using Linux or Mac install pixi with:  
```curl -fsSL https://pixi.sh/install.sh | bash```

If using windows, install pixi with:  
```iwr -useb https://pixi.sh/install.ps1 | iex```

See here for more info on pixi: https://pixi.sh/.

Then to install the project and its dependencies, type:  
```pixi install```

You could activate the virtual environment with `pixi shell` (so every command uses the virtual environment until you type `exit`) or prefix your commands with `pixi run` inside the icedyno project folder (ex: `pixi run pytest`).

To set up the automatic linters (that run every time you commit your work), you would run:  
```pixi run pre-commit install```

![install_pre_commit](images/install_pre_commit.png)

## Testing the set up
If you activated the pixi environment, type `pytest`. If not, type `pixi run pytest`. You should have one dummy test that runs on that command.

## What does it look like when the linters and pre-commit hooks run?
After you've installed the pre-commit hooks and have changes to commit, this is what the process will look like for committing:

1. You have changes to commit:  
![added_changes](images/added_changes.png)

2. Commit with a descriptive message:  
![descriptive_commit](images/descriptive_commit.png)

3. One-time setup of the linters:  
![pre_commit_hook_installation](images/pre_commit_hook_installation.png)

4. Our code was not already compliant with the linters, so they "failed" our commit and automatically changed things about our code to become compliant:  
![failed_commit](images/failed_commit.png)

5. Go ahead and inspect what got modified if you'd like:  
![inspect_changes](images/inspect_changes.png)

6. Add the changes and redo your commit command:  
 ![final_commit](images/final_commit.png)

## Adding new dependencies
Just write ```pixi add conda_or_pip_package_name```. You can add multiple dependencies at once (which is better than one at a time, `pixi` will have to recompute work otherwise) by adding a space between the package names. I.e. `pixi add package1 package2 package3`.

You'll see that the `pixi.toml` and `pixi.lock` files will change after adding your new dependencies -- make sure to add those changes in your next commit!

## Removing a dependency
```pixi remove package_name```
