@metadata_processor
def add_apt_packages(metadata):
    if node.has_bundle("apt"):
        metadata.setdefault('apt', {})
        metadata['apt'].setdefault('packages', {})

        metadata['apt']['packages']['make'] = {'installed': True}
        metadata['apt']['packages']['git'] = {'installed': True}

    return metadata, DONE