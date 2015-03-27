# spellcheck
Compare spellchecking algorithms for texts in a dataset

# Install
1. `git clone https://github.com/smilli/spellcheck.git`
2. (recommended) `virtualenv venv && source venv/bin/active`
3. `pip install -r requirements.txt`
4. Install the [Enchant library](http://www.abisource.com/projects/enchant/).  If on Mac OS X, you can just do `brew install enchant`.

# Usage
To run the spellchecker statistics use `python spellchecker_stats.py -d <path to dataset file>`
