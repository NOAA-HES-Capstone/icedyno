# GitHub Cheatsheet

Here's a quick cheatsheet on getting started with a GitHub project, if you are
new to GitHub. Before we start, anything that is within the angle brackets (`<`
or `>`) should be replaced as a whole. For example: `<your-username>` should be 
replaced to something like `SooluThomas`

## Setting up SSH keys to easily clone, push, pull contents from GH repo

Most of GitHub's documentation is pretty good. So pointing to GH docs for 
1. [Check for existing SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/checking-for-existing-ssh-keys)
2. [Generate new SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
    > Its easier to just follow the 3 steps mentioned under 
    ["Generating a new SSH key"](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key) section.
3. [Add a new SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)
4. [Test your SSH connection](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection)

## Clone the repo

Once SSH keys are set up, in your terminal move to the which ever directory
you want to have the local repo copy to live using the command

```bash
cd Documents/<your-folder-path>/Capstone
```

Then clone the repo using the command

```bash
git clone git@github.com:NOAA-HES-Capstone/icedyno.git
cd icedyno
```

_(Tip: the link was obtained from the repo -> green button called "Code" on 
top right of the repo -> SSH)_

Once this is done, you should be able to see the main branch _(by default)_
locally.

## Creating feature branches

Create a branch using the command

```bash
git checkout -b <your-initials>/<branch-name>

# This command can show you which branch you are in
# The * shows the current branch you are in 
git branch
# you can use `git checkout main` to go to main branch and then 
# `git checkout <branch-name>` to go to different branch
```

## Checking if your username and email are correct in your local git

This is an optional step but might be nice to have. Run the following:

```bash
git config user.name
git config user.email
```

If this is showing the correct github username and email, you are good. 
Otherwise, run

```bash
git config user.name <your-username>
git config user.email <your-registered-email>
```

## Add, commit and push changes to feature branch

```bash
# This will show us a summary of the files changed when compared main branch
git status

# Add the files that were changed
# It is always best to add the file names rather than to use `git add *`
# so that unwanted files don't get added
git add <path>/<file-name>

# Commit your changes
git commit -m "Type out commit message with a one line summary briefing the changes"
# TIP: if you want to add more descriptive commit add -m "descriptive message"
# after the one line summary message

# [ALWAYS] Push commit to your branch
git push origin <your-initials>/<branch-name>
```

## Create Pull Request (PR)

If you are **pushing from a branch for the first time**, the first commit will
show a link that point to creating a PR directly. It should be something like

```bash
Enumerating objects: 4, done.
Counting objects: 100% (4/4), done.
Delta compression using up to 12 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 1.36 KiB | 1.36 MiB/s, done.
Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
remote: 
remote: Create a pull request for 'soo/add-gh-cheatsheat' on GitHub by visiting
remote:      https://github.com/NOAA-HES-Capstone/icedyno/pull/new/soo/add-gh-cheatsheat
remote: 
To github.com:NOAA-HES-Capstone/icedyno.git
 * [new branch]      soo/add-gh-cheatsheat -> soo/add-gh-cheatsheat
```

Another way to open a PR is going to the repo itself and find your branch name
under the branch selector in the repository. After you click on it, it should
have a button to create a pull request.

## Pull changes from the `main` to our feature branch

There could be cases where other PRs could be merged before ours and so we will
need to pull those changes in our branch before we can merge or to make sure
that our work doesn't break anything with the new changes made in the main
branch. For this we can use

```bash
# Fetch all the changes from remote to local
git fetch

# pull the changes from main to our feature branch
git pull origin main
```

If your are pulling for the first time in that repo, the might be a lot more 
that will be asked in the terminal and run the command for **merge** which is
something like

```bash
git config pull.rebase false
```

---
Let's keep this file growing with the GitHub tips that you get know and would
like to share with others.
