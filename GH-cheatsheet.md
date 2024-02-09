# GitHub Cheatsheet

Here's a quick cheatsheet on getting started with a GitHub project, if you are
new to GitHub.

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

Let's keep this file growing with the GH tip that you get know and would like
to share with others.
