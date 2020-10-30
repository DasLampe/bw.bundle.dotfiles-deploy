from bundlewrap.metadata import DoNotRunAgain


@metadata_reactor
def add_apt_packages(metadata):
    if not node.has_bundle("apt"):
        return DoNotRunAgain

    return {
        'apt': {
            'packages': {
                'make': {'installed': True},
           }
        }
    }
