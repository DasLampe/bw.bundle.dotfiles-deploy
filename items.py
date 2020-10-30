global node

actions = {}
git_deploy = {}
directories = {}

for username, user_attrs in node.metadata.get('users', {}).items():
    if user_attrs.get('dotfiles_git', False):
        dirname = '/home/{}/.dotfiles'.format(username)

        directories[dirname] = {
            'owner': username,
        }

        git_deploy[dirname] = {
            'repo': user_attrs.get('dotfiles_git'),
            'rev': 'master',
            'needs': [
                'user:{}'.format(username),
            ]
        }

        actions['chown_dotfiles_for_{}'.format(username)] = {
            'command': 'chown -R {user} {dir}'.format(user=username, dir=dirname),
            'needs': [
                'git_deploy:{}'.format(dirname)
            ]
        }

        actions['run_make_dotfiles_{}'.format(username)] = {
            'command': 'cd {dir} && sudo -u {user} -H make all'.format(dir=dirname, user=username),
            'needs': [
                'action:chown_dotfiles_for_{}'.format(username),
                'pkg_apt:make',
            ]
        }