import os.path

global node
from urllib.parse import urlparse

actions = {}
git_deploy = {}
directories = {}

for username, user_attrs in node.metadata.get('users', {}).items():
    if user_attrs.get('dotfiles_git', False):
        repourl = user_attrs.get('dotfiles_git')
        homedir = user_attrs.get('home', f'/home/{username}')
        tempDotfilesDir = f'{homedir}/.dotfiles'

        # No .git in $HOME, let's run init
        if node.run(f"test -d {homedir}/.git", may_fail=True).return_code != 0:
            clone_options = []

            if node.metadata.get('dotfiles-deploy', {}).get('recursive'):
                clone_options.append('--recursive')

            if not urlparse(repourl):
                directories[tempDotfilesDir] = {
                    'owner': username,
                    'needs': [
                        f'user:{username}'
                    ]
                }

                git_deploy[tempDotfilesDir] = {
                    'repo': repourl,
                    'rev': 'master',
                    'needs': [
                        f'user:{username}',
                    ],
                    'owner': username,
                    'tags': [
                        f'dotfiles_deploy_{username}'
                    ],
                    'triggers': [
                        f'action:move_dotfiles_to_home_{username}',
                    ],
                }
            else:
                actions[f'clone_dotfiles_for_{username}'] = {
                    'command': f'sudo -u {username} -H git clone {" ".join(clone_options)} {repourl} {tempDotfilesDir}',
                    'unless': f'test -d {tempDotfilesDir}',
                    'needs': [
                        f'user:{username}',
                        'pkg_apt:git',
                    ],
                    'tags': [
                        f'dotfiles_deploy_{username}',
                    ],
                    'triggers': [
                        f'action:move_dotfiles_to_home_{username}',
                    ],
                    'before': [
                        f'action:update_dotfiles_for_{username}',
                    ]
                }

            # Move all dotfiles to $HOME
            actions[f'move_dotfiles_to_home_{username}'] = {
                'command': f'rsync -avb --backup-dir={homedir}/.orig_home {tempDotfilesDir}/ {homedir}/. && rm -rf {tempDotfilesDir}',
                'unless': f'test -d {homedir}/.git', # Skip f there is already a $HOME/.git dir
                'needs': [
                    'pkg_apt:rsync',
                ],
                'triggered': True,
                'before': [
                    f'action:update_dotfiles_for_{username}',
                ],
            }

        if node.metadata.get('dotfiles-deploy', {}).get('update'):
            actions[f'update_dotfiles_for_{username}'] = {
                'command': f'cd {homedir} && '
                           f'sudo -u {username} -H git remote set-url origin {repourl} && '
                           f'sudo -u {username} -H git pull origin',
                'unless': f'test ! -d {homedir}/.git', # Skip if there is no .git dir
                'needs': [
                    f'user:{username}',
                ],
                'interactive': False,
            }
