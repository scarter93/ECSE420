#!/bin/bash

if [ -n "$1" ]; then
    MODE="$1"
else
    MODE="binarize"
fi
   
INPUT='grayscale.png'
OUTPUT='test.png'

function avg(){
    if [ -n "$2" ]; then
        echo $(($(for _ in {1..100}; do ./"$1" $INPUT $OUTPUT "$2"; done | grep -o '[[:digit:]]\+' | paste -s -d+ | bc -l)/100))
    else
        echo $(($(for _ in {1..100}; do ./"$1" $INPUT $OUTPUT; done | grep -o '[[:digit:]]\+' | paste -s -d+ | bc -l)/100))
    fi
}


function calc() {
    local result="";
    result="$(printf "scale=10;$*\n" | bc --mathlib | tr -d '\\\n')";
    #                       +- default (when `--mathlib` is used) is 20
    #
    if [[ "$result" == *.* ]]; then
        # improve the output for decimal numbers
        printf "%0.5f" "$result" |
        sed -e 's/^\./0./'        `# add "0" for cases like ".5"` \
            -e 's/^-\./-0./'      `# add "0" for cases like "-.5"`\
            -e 's/0*$//;s/\.$//';  # remove trailing zeros
    else
        printf "%0.5f" "$result";
    fi;
    printf "\n";
}

echo "Getting data for files..."

#avg_bs=$(avg "binarize_sequential")
#avg_ss=$(avg "sobel_sequential")

if [ ! -f "./$MODE""_sequential" ]; then
    echo "No file ./$MODE""_sequential"
    exit 1
elif [ ! -f "./$MODE""_pthreads" ]; then
    echo "No file ./$MODE""_pthreads"
    exit 2
elif [ ! -f "./$MODE""_openmp" ]; then
    echo "No file ./$MODE""_openmp";
    exit 3
fi

avg_s=$(avg "$MODE""_sequential")

echo "Sequential: $avg_s"
echo

for i in {1..5}; do
    p=$(echo "2^$i" | bc)
    echo "--- THREAD COUNT: $p ---"
    echo -n "$MODE""_pthreads: "
    avg_p=$(avg "$MODE""_pthreads" "$p")
    calc "$avg_s/$avg_p"
    echo

    echo -n "$MODE""_openmp: "
    avg_o=$(avg "$MODE""_pthreads" "$p")
    calc "$avg_s/$avg_o"
    echo
done