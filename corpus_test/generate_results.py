import argparse
import gzip
import os
import sys
import time

import python_minifier
from result import Result, ResultWriter

try:
    RE = RecursionError
except NameError:
    # Python 2
    class RE(Exception):
        pass


def minify_corpus_entry(corpus_path, corpus_entry):
    """
    Minify a single entry in the corpus and return the result

    :param str corpus_path: Path to the corpus
    :param str corpus_entry: A file in the corpus
    :rtype: Result
    """

    with gzip.open(os.path.join(corpus_path, corpus_entry + '.py.gz'), 'rb') as f:
        source = f.read()

    result = Result(corpus_entry, len(source), 0, 0, '')

    start_time = time.time()
    try:
        minified = python_minifier.minify(source, filename=corpus_entry)
        end_time = time.time()
        result.time = end_time - start_time

        result.minified_size = len(minified)

        result.outcome = 'Minified'

    except RE:
        # Source is too deep
        result.outcome = 'RecursionError'

    except SyntaxError:
        # Source not valid for this version of Python
        result.outcome = 'SyntaxError'

    except python_minifier.UnstableMinification:
        # Minification does not equal original source
        end_time = time.time()
        result.time = end_time - start_time
        result.outcome = 'UnstableMinification'

    except Exception as exception:
        result.outcome = 'Exception: ' + str(exception)

    return result


def corpus_test(corpus_path, results_path, sha, regenerate_results):
    """
    Test the minifier on the entire corpus

    The results are written to a csv file in the results directory.
    The name of the file is results_<python_version>_<sha>.csv

    If the file already exists and regenerate_results is False, the test is skipped.

    :param str corpus_path: Path to the corpus
    :param str results_path: Path to the results directory
    :param str sha: The python-minifier sha we are testing
    :param bool regenerate_results: Regenerate results even if they are present
    """

    corpus_entries = (entry[:-len('.py.gz')] for entry in os.listdir(corpus_path))

    python_version = '.'.join([str(s) for s in sys.version_info[:2]])
    results_file_path = os.path.join(results_path, 'results_' + python_version + '_' + sha + '.csv')

    if os.path.isfile(results_file_path) and not regenerate_results:
        print('Results file already exists: %s', results_file_path)
        return

    with ResultWriter(results_file_path) as result_writer:
        for entry in corpus_entries:
            print(entry)
            result = minify_corpus_entry(corpus_path, entry)
            result_writer.write(result)


def bool_parse(value):
    return value == 'true'


def main():
    parser = argparse.ArgumentParser(description='Test python-minifier on a corpus of Python files.')
    parser.add_argument('corpus_dir', type=str, help='Path to corpus directory', default='corpus')
    parser.add_argument('results_dir', type=str, help='Path to results directory', default='results')
    parser.add_argument('minifier_sha', type=str, help='The python-minifier sha we are testing')
    parser.add_argument('regenerate_results', type=bool_parse, help='Regenerate results even if they are present', default='false')
    args = parser.parse_args()

    corpus_test(args.corpus_dir, args.results_dir, args.minifier_sha, args.regenerate_results)


if __name__ == '__main__':
    main()
