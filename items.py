actions = {}

for username, user_attrs in node.metadata.get('users', []).items():
    if 'dotfiles_git' in user_attrs:
        actions['deploy_dotfiles_{}'.format(username)] = {
            'command': 'git clone %s /home/%s/.dotfiles' % (user_attrs['dotfiles_git'], username),
            'needs': {
                'pkg_apt:',
            },
            'unless': 'test -x /home/%s/.dotfiles' % (username),
            'triggers': {
                'action:change_user_{}'.format(username),
                'action:run_make_dotfiles_{}'.format(username),
            },
        }

        actions['checkout_dotfiles_{}'.format(username)] = {
            'command': 'cd /home/%s/.dotfiles && sudo -u %s -H git pull origin master' % (username, username),
            'cascade_skip': False,
            'needs': {
                'action:deploy_dotfiles_{}'.format(username),
            },
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
        }
