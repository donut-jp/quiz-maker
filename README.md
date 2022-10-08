# Quiz Maker

Ever quiz grinded all the names of animals only to realize that your next book is about plants? Solve this issue by creating custom quizzes for your target book!

To use:
- Install requirements (will be large due to tokenizer)
- Convert target text to a txt file
- Run the script

```bash
python ./make_quiz.py -n1
```

## Arguments

```bash
positional arguments:
  input                 Input file

optional arguments:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile OUTFILE
                        Output file
  -n1                   Remove words below n1
  -n2                   Remove words below n2
  -n3                   Remove words below n3
  -n4                   Remove words below n4
  -n5                   Remove words below n5
  -e EXCLUDE, --exclude EXCLUDE
                        List of words to exclude. 1 word per line.
```

## Excluding terms

Use the `-nX` flags to exclude terms from premade jlpt lists.

Add terms to the `excluded.txt` file to manually exclude terms. The pre-made jlpt lists often don't include very simple terms.

A different exclude file can be provided using the `-e` option.
