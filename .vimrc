inoremap jj <Esc>


" Set up blinking cursor in insert mode
let &t_SI = "\e[5 q"
let &t_EI = "\e[2 q"

" Optional: Blink faster
set ttimeoutlen=10

" Function to toggle cursor blinking
function! BlinkCursor()
  if &insertmode
    set guicursor+=i:blinkwait0-blinkon250-blinkoff250
  else
    set guicursor+=i:blinkwait0-blinkon0-blinkoff0
  endif
endfunction

" Set up autocommand to call BlinkCursor when entering/leaving insert mode
augroup CursorBlink
  autocmd!
  autocmd InsertEnter * call BlinkCursor()
  autocmd InsertLeave * call BlinkCursor()
augroup END

