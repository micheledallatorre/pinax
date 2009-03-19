import os

PINAX_SVN_LOCATION = 'http://svn.pinaxproject.com/pinax/trunk'

def extend_parser(parser):
    parser.add_option(
        '--svn',
        metavar='DIR_OR_URL',
        dest='pinax_svn',
        default=PINAX_SVN_LOCATION,
        help='Location of a svn directory or URL to use for the installation of Pinax'
    )

def adjust_options(options, args):
    if not args:
        return # caller will raise error

def after_install(options, home_dir):
    base_dir = os.path.dirname(home_dir)
    src_dir = join(home_dir, 'src')
    pinax_svn = options.pinax_svn
    if os.path.exists(pinax_svn):
        # A directory
        logger.debug('Using svn checkout in directory %s' % pinax_svn)
        pinax_dir = os.path.abspath(pinax_svn)
        logger.info('Using existing svn checkout at %s' % pinax_svn)
    else:
        pinax_dir = join(src_dir, 'pinax')
        logger.notify('Fetching Pinax from %s to %s' % (pinax_svn, pinax_dir))
        fs_ensure_dir(src_dir)
        call_subprocess(['svn', 'checkout', '--quiet', pinax_svn, pinax_dir],
                        show_stdout=True)
    logger.indent += 2
    try:
        logger.notify('Installing pip')
        call_subprocess([os.path.abspath(join(home_dir, 'bin', 'easy_install')), '--quiet', 'pip'],
                        cwd=os.path.abspath(pinax_dir),
                        filter_stdout=filter_python_develop,
                        show_stdout=False)
        logger.notify('Installing Django 1.0.2')
        call_subprocess([os.path.abspath(join(home_dir, 'bin', 'pip')), 'install', 'Django', '--quiet'],
                        cwd=os.path.abspath(pinax_dir),
                        filter_stdout=filter_python_develop,
                        show_stdout=False)
        logger.notify('Installing Pinax')
        call_subprocess([os.path.abspath(join(home_dir, 'bin', 'pip')), 'install', '-e', '%s/' % pinax_dir, '--quiet'],
                        filter_stdout=filter_python_develop,
                        show_stdout=False)
    finally:
        logger.indent -= 2
    logger.notify('Now activate the newly created virtualenv by running: ')
    logger.indent += 2
    logger.notify('source %s (Linux/Unix/Mac OS) or activate.bat in the bin directory (Windows)'
                  % join(home_dir, 'bin', 'activate'))
    logger.indent -= 2
    logger.notify('Then install the external apps and libraries used in all Pinax projects by running: ')
    logger.indent += 2
    logger.notify('pip install --requirement %s'
                  % join(pinax_dir, 'requirements', 'external_apps.txt'))
    logger.indent -= 2

def fs_ensure_dir(dir):
    if not os.path.exists(dir):
        logger.info('Creating directory %s' % dir)
        os.makedirs(dir)

def filter_python_develop(line):
    if not line.strip():
        return Logger.DEBUG
    for prefix in ['Searching for', 'Reading ', 'Best match: ', 'Processing ',
                   'Moving ', 'Adding ', 'running ', 'writing ', 'Creating ',
                   'creating ', 'Copying ']:
        if line.startswith(prefix):
            return Logger.DEBUG
    return Logger.NOTIFY
