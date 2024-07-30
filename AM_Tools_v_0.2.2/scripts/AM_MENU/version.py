VERSION_MAJOR = 0
VERSION_MINOR = 2
VERSION_PATCH = 2

version_info = (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)
version = '%i.%i.%i' % version_info
__version__ = version

__all__ = ['version', 'version_info', '__version__']





def compareVer( latestVersion ):
    
    update_available = False
    
    for new , current in zip( latestVersion , list(version_info) ):
        if new == current:
            continue
        elif new < current:
            break
        elif new > current:
            update_available = True
            break
        
        
    return update_available