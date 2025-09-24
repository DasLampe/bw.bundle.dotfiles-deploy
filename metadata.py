from urllib.parse import urlparse

defaults = {
    'dotfiles-deploy': {
        'recursive': True,
        'update': True,
    }
}

@metadata_reactor
def check_https_format(metadata):
    for username, user_attrs in node.metadata.get('users', {}).items():
        if (user_attrs.get('dotfiles_git', False) and
                (metadata.get('dotfiles-deploy/recursive') or metadata.get('dotfiles-deploy/update'))
                and not urlparse(user_attrs.get('dotfiles_git'))):
                raise Exception("We can't handle recursive clones for non http(s) git repos right now.")

    return {}


@metadata_reactor
def add_apt_packages(metadata):
    if not node.has_bundle("apt"):
        raise DoNotRunAgain

    return {
        'apt': {
            'packages': {
                'rsync': {'installed': True},
            },
        },
    }
