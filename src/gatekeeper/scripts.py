# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de


import sys
import uuid
import os.path
import logging

from cookiecutter.main import (prompt_for_config,
                               get_user_config, _get_parser, generate_context,
                               generate_files, clone)


def parse_cookiecutter_args(args):
    """ Parse the command-line arguments to Cookiecutter. """
    parser = _get_parser()
    import pdb; pdb.set_trace()
    parser.add_argument(
        'output_dir',
        help='Base Output Directory'
    )
    return parser.parse_args(args)


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
        'path': args.output_dir,
        'secret': secret,
    }

    input_dir = args.input_dir
    checkout = args.checkout
    no_input = args.no_input

    config_dict = get_user_config()

    if "git@" in input_dir or "https://" in input_dir:
        repo_dir = clone(
            repo_url=input_dir,
            checkout=checkout,
            clone_to_dir=config_dict['cookiecutters_dir']
        )
    else:
        repo_dir = input_dir

    context_file = os.path.join(repo_dir, 'cookiecutter.json')
    logging.debug('context_file is {0}'.format(context_file))

    context = generate_context(
        context_file=context_file,
        default_context=config_dict['default_context'],
        extra_context=extra_context,
    )
    if not no_input:
        cookiecutter_dict = prompt_for_config(context)
        context['cookiecutter'] = cookiecutter_dict

    generate_files(
        repo_dir=repo_dir,
        context=context,
        output_dir=args.output_dir,
    )


if __name__ == '__main__':
    main()
