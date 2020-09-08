#!/usr/bin/env python3

import argparse, os, sys, re
import subprocess as sp
import os.path as op
import pathlib
import pdb

HOME = os.environ['HOME']

def add_lines(fname, lines_to_add):
    pathlib.Path(fname).touch()  # make sure the file exists
    with open(fname, 'r') as f:
        lines = f.read().splitlines()

    if not set(lines).intersection(lines_to_add):
        lines += lines_to_add
        with open(fname, 'w') as f:
            f.write('\n'.join(lines))

def run_apt():
    pkgs = [ "ccache","curl","gnome-terminal","aptitude","exuberant-ctags",
             "htop","python3-pip","ipython3","python3-ipdb","xclip",
             "cmake-curses-gui","ninja-build","ubuntu-sounds"]

    #"zathura",
    #"xdotool",
    #"global",
    #"libnotify-dev",
    #"flake8",
    #"notify-osd",
    #"clang-tools-6.0"
    sp.check_call(['sudo', 'apt', 'update'])
    sp.check_call(['sudo', 'apt', 'install', '-y'] + pkgs)

def update_repo(url, parent_dir, sha=None):
    tail = url.split('/')[-1]
    if tail[-4:] == '.git':
        tail = tail[:-4]
    repo_dir = op.join(parent_dir, tail)
    if not op.isdir(repo_dir):
        sp.check_call(['git', 'clone', url], cwd=parent_dir)

    if sha:
        sp.check_call(['git', 'fetch'], cwd=repo_dir)
        sp.check_call(['git', 'checkout', sha], cwd=repo_dir)
    else:
        try:
            sp.check_call(['git', 'pull'], cwd=repo_dir)
        except sp.CalledProcessError:
            sp.check_call(['git', 'fetch'], cwd=repo_dir)

def setup_vimrc(config_dir):
    for d in ['bundle', 'autoload', 'swaps', 'backups']:
        os.makedirs(op.join(HOME, ".vim", d), exist_ok=True)

    lines_to_add = [
        'source ' + op.join(config_dir, '.vimrc'),
        'set backup',
        'set backupdir=' + op.join(HOME, '.vim', 'backups'),
        'set dir=' + op.join(HOME, '.vim', 'swaps')]

    print(op.join(HOME, '.vimrc'))
    #pdb.set_trace()
    add_lines(op.join(HOME, '.vimrc'), lines_to_add)

def install_vim_plugins(config_dir, repos_dir):
    vim_dir = op.join(repos_dir, 'vim')
    os.makedirs(vim_dir, exist_ok=True)
    os.makedirs(op.join(HOME, '.vim', 'autoload'), exist_ok=True)
    os.makedirs(op.join(HOME, '.vim', 'bundle'), exist_ok=True)
    update_repo('https://github.com/tpope/vim-pathogen.git', vim_dir)
    try:
        os.symlink(
            op.join(vim_dir, 'vim-pathogen', 'autoload', 'pathogen.vim'),
            op.join(HOME, '.vim', 'autoload', 'pathogen.vim'))
    except FileExistsError:
        pass

    def _update(repo, sha=None):
        update_repo(repo, vim_dir, sha)
        repo_name = repo.split('/')[-1]
        if repo_name.split('.')[-1] == 'git':
            repo_name = '.'.join(repo_name.split('.')[:-1])
        try:
            os.symlink(op.join(vim_dir, repo_name),
                       op.join(HOME, '.vim', 'bundle', repo_name))
        except FileExistsError:
            pass

    _update('https://github.com/tpope/vim-fugitive')

'''    _update('https://github.com/milkypostman/vim-togglelist')
    _update('https://github.com/neomake/neomake')
    _update('https://github.com/esquires/tabcity')
    _update('https://github.com/esquires/vim-map-medley')
    _update('https://github.com/ctrlpvim/ctrlp.vim')
    _update('https://github.com/majutsushi/tagbar')
    _update('https://github.com/tmhedberg/SimpylFold')
    _update('https://github.com/ludovicchabant/vim-gutentags')
    _update('https://github.com/tomtom/tcomment_vim.git')
    _update('https://github.com/esquires/neosnippet-snippets')
    _update('https://github.com/Shougo/neosnippet.vim.git')
    _update('https://github.com/jlanzarotta/bufexplorer.git')
    _update('https://github.com/lervag/vimtex')
    _update('https://github.com/vim-airline/vim-airline')
    _update('https://github.com/Shougo/echodoc.vim.git')
    _update('https://github.com/tpope/vim-surround')
    _update('https://github.com/tpope/vim-repeat')
    _update('https://github.com/chaoren/vim-wordmotion')

    # deoplete has a 3.6 dependency after the below commit
    deoplete_sha = 'origin/master' if sys.version_info >= (3, 6) else '7853113'
    _update('https://github.com/Shougo/deoplete.nvim', deoplete_sha)
    _update('https://github.com/Shougo/neco-syntax.git')
    _update('https://github.com/autozimu/LanguageClient-neovim')

    sp.check_call(['nvim', '-c', 'UpdateRemotePlugins', '-c', 'q'])

    # lvdb
    lvdb_python_dir = op.join(vim_dir, 'lvdb', 'python')
    _update('https://github.com/esquires/lvdb')
    sp.check_call(['sudo', 'pip2', 'install', '-e', '.'], cwd=lvdb_python_dir)
    sp.check_call(['sudo', 'pip3', 'install', '-e', '.'], cwd=lvdb_python_dir)

    # LanguageClient-neovim dependencies
    languageclient_dir = op.join(vim_dir, 'LanguageClient-neovim')
    sp.check_call(['bash', 'install.sh'], cwd=languageclient_dir)
    sp.check_call(['sudo', 'pip3', 'install', 'python-language-server[all]'])

    # orgmode and its dependencies
    update_repo('https://github.com/jceb/vim-orgmode', vim_dir)
    update_repo('https://github.com/vim-scripts/utl.vim', vim_dir)
    update_repo('https://github.com/tpope/vim-repeat', vim_dir)
    update_repo('https://github.com/tpope/vim-speeddating', vim_dir)
    update_repo('https://github.com/chrisbra/NrrwRgn', vim_dir)
    update_repo('https://github.com/mattn/calendar-vim', vim_dir)
    update_repo('https://github.com/inkarkat/vim-SyntaxRange', vim_dir)

    # patches
    vimtex_dir = op.join(vim_dir, 'vimtex')
    patch_msg = '[PATCH] open tag in reverse_goto when indicated by switchbuf'
    patch_file = op.join(
        config_dir, 'patches',
        '0001-open-tag-in-reverse_goto-when-indicated-by-switchbuf.patch')
    apply_patch(patch_file, patch_msg, vimtex_dir)
'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_dir')
    parser.add_argument('repos_dir')
    args = parser.parse_args()

    args.config_dir = op.abspath(args.config_dir)
    os.makedirs(op.join(args.config_dir), exist_ok=True)
    args.repos_dir = op.abspath(args.repos_dir)
    #os.makedirs(op.join(HOME, ".vim", d), exist_ok=True)

    os.makedirs(op.join(HOME, 'dev'), exist_ok=True)

    run_apt()

    setup_vimrc(args.config_dir)
    install_vim_plugins(args.config_dir, args.repos_dir)

    print("Done")

if __name__ == '__main__':
    main()
