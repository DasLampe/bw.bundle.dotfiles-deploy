global node
from urllib.parse import urlparse

actions = {}
git_deploy = {}
directories = {}

for username, user_attrs in node.metadata.get('users', {}).items():
    if user_attrs.get('dotfiles_git', False):
        repourl = user_attrs.get('dotfiles_git')
        dirname = f'/home/{username}/.dotfiles'
        clone_options = []

        if node.metadata.get('dotfiles-deploy', {}).get('recursive'):
            clone_options.append('--recursive')

        if not urlparse(repourl):
            directories[dirname] = {
                'owner': username,
            }

            git_deploy[dirname] = {
                'repo': repourl,
                'rev': 'master',
                'needs': [
                    f'user:{username}',
                ],
                'owner': username,
                'tags': [
                    f'dotfiles_deploy_{username}'
                ]
            }
        else:
            actions[f'clone_dotfiles_for_{username}'] = {
                'command': f'sudo -u {username} -H git clone {" ".join(clone_options)} {repourl} {dirname}',
                'unless': f'test -d {dirname}',
                'needs': [
                    f'user:{username}',
                    'pkg_apt:git',
                ],
                'tags': [
                    f'dotfiles_deploy_{username}',
                ]
            }

            if node.metadata.get('dotfiles-deploy', {}).get('update'):
                actions[f'update_dotfiles_for_{username}'] = {
                    'command': f'cd {dirname} && sudo -u {username} -H git pull origin',
                    'unless': f'test ! -d {dirname}/.git', # Skip if there is no .git dir
                    'needs': [
                        f'action:clone_dotfiles_for_{username}',
                        f'user:{username}',
                    ],
                    'interactive': False,
                }

        actions[f'chown_dotfiles_for_{username}'] = {
            'command': f'chown -R {username} {dirname}',
            'needs': [
                f'tag:dotfiles_deploy_{username}'
            ],
            'interactive': False,
        }

        actions['run_make_dotfiles_{}'.format(username)] = {
            'command': f'cd {dirname} && sudo -u {username} -H make all',
            'needs': [
                f'action:chown_dotfiles_for_{username}',
                'pkg_apt:make',
            ],
            'interactive': False,
        }
