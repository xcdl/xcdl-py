import sys

from application import Application


if __name__ == '__main__':
    sys.exit(Application(*sys.argv).run())
