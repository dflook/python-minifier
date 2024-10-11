import argparse
import datetime
import gzip
import logging
import os
import sys
import time

import python_minifier

from .result import Result, ResultWriter

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

    if os.path.isfile(os.path.join(corpus_path, corpus_entry + '.py.gz')):
        with gzip.open(os.path.join(corpus_path, corpus_entry + '.py.gz'), 'rb') as f:
            source = f.read()
    else:
        with open(os.path.join(corpus_path, corpus_entry), 'rb') as f:
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

    except AssertionError as assertion_error:
        result.outcome = 'Exception: AssertionError'

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
    python_version = '.'.join([str(s) for s in sys.version_info[:2]])

    log_path = 'results_' + python_version + '_' + sha + '.log'
    print('Logging in GitHub Actions is absolute garbage. Logs are going to ' + log_path)

    logging.basicConfig(filename=os.path.join(results_path, log_path), level=logging.DEBUG)

    corpus_entries = [entry[:-len('.py.gz')] for entry in os.listdir(corpus_path)]

    results_file_path = os.path.join(results_path, 'results_' + python_version + '_' + sha + '.csv')

    if os.path.isfile(results_file_path):
        print('Results file already exists: %s' % results_file_path)
        if regenerate_results:
            os.remove(results_file_path)

    total_entries = len(corpus_entries)
    print('Testing python-minifier on %d entries' % total_entries)
    tested_entries = 0

    start_time = time.time()
    next_checkpoint = time.time() + 60

    with ResultWriter(results_file_path) as result_writer:
        print('%d results already present' % len(result_writer))

        for entry in corpus_entries:
            if entry in result_writer:
                continue

            logging.debug('Corpus entry [' + entry + ']')

            result = minify_corpus_entry(corpus_path, entry)
            result_writer.write(result)
            tested_entries += 1

            sys.stdout.flush()

            if time.time() > next_checkpoint:
                percent = len(result_writer) / float(total_entries) * 100
                time_per_entry = (time.time() - start_time) / tested_entries
                entries_remaining = len(corpus_entries) - len(result_writer)
                time_remaining = datetime.timedelta(seconds=int(entries_remaining * time_per_entry))
                print('Tested %d/%d entries (%d%%) estimated %s remaining' % (len(result_writer), total_entries, percent, time_remaining))
                sys.stdout.flush()
                next_checkpoint = time.time() + 60

    print('Finished')


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
