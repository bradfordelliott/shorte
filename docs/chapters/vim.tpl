@body

@h1 Setting up VIM
A lexer is provided for VIM. It can be setup as follows:

@h2 Edit your .vimrc
Edit your ~/.vimrc file and add the following line to the end:

@code
source ~/.vim/filetype.vim

@h2 Create filetype.vim
Create ~/.vim/filetype.vim with the following content:
@code
" shorte syntax
augroup filetype
    au!
    au! bufread,bufnewfile *.tpl    set filetype=tpl
augroup end 

