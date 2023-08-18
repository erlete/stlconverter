# Check argument count:
if [ "$1" == "" ]; then
    echo No compilation mode specified
    exit 1
fi

# Check argument values:
if [ "$1" == "Single" ]; then
    extraArg=
elif [ "$1" == "Continuous" ]; then
    extraArg=-w
else
    echo Invalid compilation mode specified
    exit 1
fi

# Compile CSS:
cd js
npx tailwindcss -i src/styles/template.css -o src/styles/output.css $extraArg
