echo
echo -e "1234 7890\nqdrw fup;\nasht neoi\nzxmc l,.'" \
    | tr "12347890qdrwfup;ashtneoizxmcl,.'" "$@" | tr a-z A-Z
echo
trap "stty sane" EXIT
stty min 1 time 0 -icanon -echo
stdbuf -o0 tr "12347890qdrwfup;ashtneoizxmcl,.'" "$@"
