"""GPM: stateless password manager using a MLP generator."""

import argparse
import functools

import gpm.pipeline

# CLI #########################################################################

def main():
    # init
    __password = ''
    # CLI args
    __parser = argparse.ArgumentParser(description='Generate / retrieve the password matching the input informations.')
    __parser.add_argument('--key', '-k', action='store', dest='master_key', type=str, default='', help='the master key (all ASCII)')
    __parser.add_argument('--target', '-t', action='store', dest='login_target', type=str, default='', help='the login target (URL, IP, name, etc)')
    __parser.add_argument('--id', '-i', action='store', dest='login_id', type=str, default='', help='the login id (username, email, etc)')
    __parser.add_argument('--length', '-l', action='store', dest='password_length', type=int, default=16, help='the length of the password (default 16)')
    __parser.add_argument('--nonce', '-n', action='store', dest='password_nonce', type=int, default=1, help='the nonce of the password (default 1)')
    __parser.add_argument('--lower', '-a', action='store_false', dest='include_lower', default=True, help='exclude lowercase letters from the password')
    __parser.add_argument('--upper', '-A', action='store_false', dest='include_upper', default=True, help='exclude uppercase letters from the password')
    __parser.add_argument('--digits', '-d', action='store_false', dest='include_digits', default=True, help='exclude digits from the password')
    __parser.add_argument('--symbols', '-s', action='store_true', dest='include_symbols', default=False, help='include symbols in the password')
    # parse
    try:
        __args = vars(__parser.parse_args())
        # fill the missing arguments
        if not __args.get('master_key', ''):
            __args['master_key'] = input('> Master key:\n')
        if not __args.get('login_target', ''):
            __args['login_target'] = input('> Login target:\n')
        # generate the password
        __password = process(
            input_vocabulary=gpm.pipeline.INPUT_VOCABULARY,
            model_context_dim=gpm.pipeline.N_CONTEXT_DIM,
            model_embedding_dim=gpm.pipeline.N_EMBEDDING_DIM,
            **__args)
    except:
        pass # automatically prints the help message
    # return it
    print(__password)

# MAIN ########################################################################

if __name__ == '__main__':
    main()

# TEST ########################################################################

_process = functools.partial(
    gpm.pipeline.process,
    password_length=32,
    password_nonce=1,
    include_lower=True,
    include_upper=True,
    include_digits=True,
    include_symbols=False,
    input_vocabulary=gpm.pipeline.INPUT_VOCABULARY,
    model_context_dim=gpm.pipeline.N_CONTEXT_DIM,
    model_embedding_dim=gpm.pipeline.N_EMBEDDING_DIM)
