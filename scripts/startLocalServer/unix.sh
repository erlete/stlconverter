# Check argument count:
if [ "$1" == "" ]; then
    echo No port specified
    exit 1
fi

# Start local server:
php -S localhost:$1 -t js/src
