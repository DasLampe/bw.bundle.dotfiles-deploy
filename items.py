global node

actions = {}

pkg = {
    'make': {},
    'git': {
        'installed': True,
    },
}

for username, user_attrs in node.metadata.get('users', []).items():
    if 'dotfiles_git' in user_attrs:
        actions['deploy_dotfiles_{}'.format(username)] = {
            'command': 'sudo -u {user} -H git clone --recursive {repo} /home/{user}/.dotfiles' \
                .format(repo=user_attrs['dotfiles_git'], user=username),
            'needs': [
                'pkg:git',
            ],
            'unless': 'test -x /home/%s/.dotfiles' % (username),
            'triggers': {
                'action:change_user_{}'.format(username),
                'action:run_make_dotfiles_{}'.format(username),
            },
        }

        actions['checkout_dotfiles_{}'.format(username)] = {
            'command': 'cd /home/{user}/.dotfiles && '\
                'sudo -u {user} -H git pull origin master && '\
                'sudo -u {user} -H git submodule update --init'.format(user=username),
            'cascade_skip': False,
            'needs': [
                'pkg:git',
                'action:deploy_dotfiles_{}'.format(username),
            ],
            'triggers': {
                'action:run_make_dotfiles_{}'.format(username),
            }
        }

        actions['change_user_{}'.format(username)] = {
            'command': 'chown -R %s:%s /home/%s' % (username, username, username),
            'triggered': True,
        }

        actions['run_make_dotfiles_{}'.format(username)] = {
            'command': 'cd /home/%s/.dotfiles && sudo -u %s -H make' % (username, username),
            'triggered': True,
            'needs': [
                'pkg:make',
            ]
        }
