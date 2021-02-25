trap "stty sane" EXIT
stty min 1 time 0 -icanon -echo
stdbuf -o0 tr "$@"
