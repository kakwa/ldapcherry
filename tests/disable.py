import os
def travis_disabled(f):
    def _decorator(f):
            print 'test has been disabled on travis'
    if 'TRAVIS' in os.environ and os.environ['TRAVIS'] == 'yes':
        return _decorator
    else:
        return f
