# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de


import sys
import uuid
import os.path
import logging

from cookiecutter.main import (parse_cookiecutter_args, cookiecutter,
                               get_user_config, generate_context)


def main(v=None):  # FIXME Buildout Argument CRAP
    args = parse_cookiecutter_args(sys.argv[1:])
    if args.verbose:
        logging.basicConfig(
            format='%(levelname)s %(filename)s: %(message)s',
            level=logging.DEBUG
        )
    else:
        # Log info and above to console
        logging.basicConfig(
            format='%(levelname)s: %(message)s',
            level=logging.INFO
        )
    secret = str(uuid.uuid4()).replace('-', '')[:16]
    extra_context = {
        'path':
        '/'.join(os.path.realpath(args.input_dir).split('/')[:-1]),
        'secret': secret,
    }
    cookiecutter(
        args.input_dir,
        args.checkout,
        args.no_input,
        extra_context=extra_context
    )


    ### Reading the Config a 2'nd time to have access to the context in the
    ### VHOST Script
    #input_dir = args.input_dir
    #checkout = args.checkout

    #config_dict = get_user_config()
    #
    #if "git@" in input_dir or "https://" in input_dir:
    #    repo_dir = clone(
    #        repo_url=input_dir,
    #        checkout=checkout,
    #        clone_to_dir=config_dict['cookiecutters_dir']
    #    )
    #else:
    #    repo_dir = input_dir

    #context_file = os.path.join(repo_dir, 'cookiecutter.json')
    #logging.debug('context_file is {0}'.format(context_file))

    #context = generate_context(
    #    context_file=context_file,
    #    default_context=config_dict['default_context'],
    #    extra_context=extra_context,
    #)
    #import pdb; pdb.set_trace()


if __name__ == '__main__':
    main()
