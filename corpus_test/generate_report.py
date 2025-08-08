import argparse
import os
import sys

from dataclasses import dataclass, field
from typing import Iterable

from result import Result, ResultReader

ENHANCED_REPORT = os.environ.get('ENHANCED_REPORT', True)


@dataclass
class ResultSet:
    """
    A set of results from minifying a corpus using a specific version of Python and a specific version of python-minifier
    """

    python_version: str
    sha: str

    entries: dict[str, Result] = field(default_factory=dict)

    valid_count = 0
    larger_than_original_count = 0
    recursion_error_count = 0
    unstable_minification_count = 0
    exception_count = 0

    total_percent_of_original: float = 0
    total_time: float = 0

    def add(self, result: Result):
        """Add a result to the result set"""
        self.entries[result.corpus_entry] = result

        if result.outcome in ['Minified', 'Success', 'SizeIncrease', 'NoChange']:
            self.valid_count += 1
            self.total_time += result.time

            if result.original_size > 0:
                percent_of_original = (result.minified_size / result.original_size) * 100
                self.total_percent_of_original += percent_of_original

            if result.original_size < result.minified_size:
                self.larger_than_original_count += 1

        if result.outcome == 'RecursionError':
            self.recursion_error_count += 1
        elif result.outcome == 'UnstableMinification':
            self.unstable_minification_count += 1
        elif result.outcome.startswith('Exception') and result.outcome != 'Exception: source code string cannot contain null bytes':
            self.exception_count += 1

    @property
    def mean_time(self) -> float:
        """Return the mean time to minify a file"""
        return self.total_time / self.valid_count if self.valid_count else 0

    @property
    def mean_percent_of_original(self) -> float:
        """Return the mean minified size as a percent of the original size"""
        return self.total_percent_of_original / self.valid_count if self.valid_count else 0

    def larger_than_original(self) -> Iterable[Result]:
        """Return those entries that have a larger minified size than the original size"""
        for result in self.entries.values():
            if result.outcome != 'Minified':
                continue

            if result.original_size < result.minified_size:
                yield result

    def recursion_error(self) -> Iterable[Result]:
        """Return those entries that have a recursion error"""
        for result in self.entries.values():
            if result.outcome == 'RecursionError':
                yield result

    def exception(self) -> Iterable[Result]:
        """Return those entries that have an exception"""
        for result in self.entries.values():
            if result.outcome.startswith('Exception'):
                yield result

    def unstable_minification(self) -> Iterable[Result]:
        """Return those entries that have an unstable minification"""
        for result in self.entries.values():
            if result.outcome == 'UnstableMinification':
                yield result

    def compare_size_increase(self, base: 'ResultSet') -> Iterable[Result]:
        """
        Return those entries that have a size increase in this result set compared to the base result set
        """

        for result in self.entries.values():
            if result.outcome != 'Minified':
                # This result was not minified, so we can't compare
                continue

            if result.corpus_entry not in base.entries:
                continue

            base_result = base.entries[result.corpus_entry]
            if base_result.outcome != 'Minified':
                # The base result was not minified, so we can't compare
                continue

            if result.minified_size > base_result.minified_size:
                yield result

    def compare_size_decrease(self, base: 'ResultSet') -> Iterable[Result]:
        """
        Return those entries that have a size decrease in this result set compared to the base result set
        """

        for result in self.entries.values():
            if result.outcome != 'Minified':
                continue

            if result.corpus_entry not in base.entries:
                continue

            base_result = base.entries[result.corpus_entry]
            if base_result.outcome != 'Minified':
                # The base result was not minified, so we can't compare
                continue

            if result.minified_size < base_result.minified_size:
                yield result


def result_summary(results_dir: str, python_version: str, sha: str) -> ResultSet:
    """
    Return a summary of the results for a specific version of Python and a specific version of python-minifier

    :param results_dir: The directory containing the results
    :param python_version: The version of Python
    :param sha: The git sha of the version of python-minifier
    """

    summary = ResultSet(python_version, sha)

    results_file_path = os.path.join(results_dir, 'results_' + python_version + '_' + sha + '.csv')
    with ResultReader(results_file_path) as result_reader:

        result: Result
        for result in result_reader:
            summary.add(result)

    return summary


def format_difference(compare: Iterable[Result], base: Iterable[Result]) -> str:
    """
    Return a string representing the difference between two sets of results

    The returned string will include:
     - the size of the compare set
     - the number of new entries in the compare set that are not in the base set
     - and the number of entries that are in the base set but not in the compare set.

    :param compare: The results we are interested in
    :param base: The results to compare against
    """

    compare_set = {result.corpus_entry for result in compare}
    base_set = {result.corpus_entry for result in base}

    s = str(len(compare_set))

    detail = []

    if len(compare_set - base_set) > 0:
        detail.append(f'+{len(compare_set - base_set)}')

    if len(base_set - compare_set) > 0:
        detail.append(f'-{len(base_set - compare_set)}')

    if detail:
        return f'{s} ({", ".join(detail)})'
    else:
        return s


def report_larger_than_original(results_dir: str, python_versions: list[str], minifier_sha: str) -> str:
    yield '''
## Larger than original

| Corpus Entry | Original Size | Minified Size |
|--------------|--------------:|--------------:|'''

    for python_version in python_versions:
        try:
            summary = result_summary(results_dir, python_version, minifier_sha)
        except FileNotFoundError:
            continue

        larger_than_original = sorted(summary.larger_than_original(), key=lambda result: result.original_size)

        for entry in larger_than_original:
            yield f'| {entry.corpus_entry} | {entry.original_size} | {entry.minified_size} ({entry.minified_size - entry.original_size:+}) |'


def report_unstable(results_dir: str, python_versions: list[str], minifier_sha: str) -> str:
    yield '''
## Unstable

| Corpus Entry | Python Version | Original Size |
|--------------|----------------|--------------:|'''

    for python_version in python_versions:
        try:
            summary = result_summary(results_dir, python_version, minifier_sha)
        except FileNotFoundError:
            continue

        unstable = sorted(summary.unstable_minification(), key=lambda result: result.original_size)

        for entry in unstable:
            yield f'| {entry.corpus_entry} | {python_version} | {entry.original_size} |'


def report_exceptions(results_dir: str, python_versions: list[str], minifier_sha: str) -> str:
    yield '''
## Exceptions

| Corpus Entry | Python Version | Exception |
|--------------|----------------|-----------|'''

    exceptions_found = False

    for python_version in python_versions:
        try:
            summary = result_summary(results_dir, python_version, minifier_sha)
        except FileNotFoundError:
            continue

        exceptions = sorted(summary.exception(), key=lambda result: result.original_size)

        for entry in exceptions:
            exceptions_found = True
            yield f'| {entry.corpus_entry} | {python_version} | {entry.outcome} |'

    if not exceptions_found:
        yield ' None | | |'


def report_larger_than_base(results_dir: str, python_versions: list[str], minifier_sha: str, base_sha: str) -> str:
    yield '''
## Top 10 Larger than base

| Corpus Entry | Original Size | Minified Size |
|--------------|--------------:|--------------:|'''

    there_are_some_larger_than_base = False

    for python_version in python_versions:
        try:
            summary = result_summary(results_dir, python_version, minifier_sha)
        except FileNotFoundError:
            continue

        try:
            base_summary = result_summary(results_dir, python_version, base_sha)
        except FileNotFoundError:
            continue

        larger_than_original = sorted(summary.compare_size_increase(base_summary), key=lambda result: result.original_size)[:10]

        for entry in larger_than_original:
            there_are_some_larger_than_base = True
            yield f'| {entry.corpus_entry} | {entry.original_size} | {entry.minified_size} ({entry.minified_size - base_summary.entries[entry.corpus_entry].minified_size:+}) |'

    if not there_are_some_larger_than_base:
        yield '| N/A | N/A | N/A |'


def report_slowest(results_dir: str, python_versions: list[str], minifier_sha: str) -> str:
    yield '''
## Top 10 Slowest

| Corpus Entry | Original Size | Minified Size | Time |
|--------------|--------------:|--------------:|-----:|'''

    for python_version in python_versions:
        try:
            summary = result_summary(results_dir, python_version, minifier_sha)
        except FileNotFoundError:
            continue

        for entry in sorted(summary.entries.values(), key=lambda entry: entry.time, reverse=True)[:10]:
            yield f'| {entry.corpus_entry} | {entry.original_size} | {entry.minified_size} | {entry.time:.3f} |'

def format_size_change_detail(summary, base_summary) -> str:
    mean_percent_of_original_change = summary.mean_percent_of_original - base_summary.mean_percent_of_original

    s = f'{summary.mean_percent_of_original:.3f}% ({mean_percent_of_original_change:+.3f}%'

    got_bigger_count = len(list(summary.compare_size_increase(base_summary)))
    got_smaller_count = len(list(summary.compare_size_decrease(base_summary)))

    if got_bigger_count > 0:
        s += f', {got_bigger_count} :chart_with_upwards_trend:'
    if got_smaller_count > 0:
        s += f', {got_smaller_count} :chart_with_downwards_trend:'

    s += ')'

    return s

def report(results_dir: str, minifier_ref: str, minifier_sha: str, base_ref: str, base_sha: str) -> Iterable[str]:
    """
    Generate a report comparing the results of two versions of python-minifier

    The report is generated as a markdown string.

    :param results_dir: The directory containing the results
    :param minifier_ref: The git ref of the version of python-minifier
    :param minifier_sha: The git sha of the version of python-minifier
    :param base_ref: The git ref of the base version of python-minifier we are comparing against
    :param base_sha: The git sha of the base version of python-minifier we are comparing against
    """

    yield f'''
# Python Minifier Test Report

Git Ref: {minifier_ref}
Git Sha: {minifier_sha}
Base Ref: {base_ref}
Base Sha: {base_sha}

This report is generated by the `corpus_test/generate_report.py` script.

## Summary

| Python Version | Valid Corpus Entries | Average Time | Minified Size | Larger than original | Recursion Error | Unstable Minification | Exception |
|----------------|---------------------:|-------------:|--------------:|---------------------:|----------------:|----------------------:|----------:|'''

    for python_version in ['2.7', '3.3', '3.4', '3.5', '3.6', '3.7', '3.8', '3.9', '3.10', '3.11', '3.12', '3.13']:
        try:
            summary = result_summary(results_dir, python_version, minifier_sha)
        except FileNotFoundError:
            yield f'| {python_version} | N/A | N/A | N/A | N/A | N/A | N/A | N/A |'
            continue

        try:
            base_summary = result_summary(results_dir, python_version, base_sha)
        except FileNotFoundError:
            base_summary = ResultSet(python_version, base_ref)

        mean_time_change = summary.mean_time - base_summary.mean_time

        yield (
                f'| {python_version} ' +
                f'| {summary.valid_count} ' +
                f'| {summary.mean_time:.3f} ({mean_time_change:+.3f}) ' +
                f'| {format_size_change_detail(summary, base_summary)} ' +
                f'| {format_difference(summary.larger_than_original(), base_summary.larger_than_original())} ' +
                f'| {format_difference(summary.recursion_error(), base_summary.recursion_error())} ' +
                f'| {format_difference(summary.unstable_minification(), base_summary.unstable_minification())} ' +
                f'| {format_difference(summary.exception(), base_summary.exception())} '
        )

    if ENHANCED_REPORT:
        yield from report_larger_than_original(results_dir, ['3.13'], minifier_sha)
        yield from report_larger_than_base(results_dir, ['3.13'], minifier_sha, base_sha)
        yield from report_slowest(results_dir, ['3.13'], minifier_sha)
        yield from report_unstable(results_dir, ['2.7', '3.3', '3.4', '3.5', '3.6', '3.7', '3.8', '3.9', '3.10', '3.11', '3.12', '3.13'], minifier_sha)
        yield from report_exceptions(results_dir, ['2.7', '3.3', '3.4', '3.5', '3.6', '3.7', '3.8', '3.9', '3.10', '3.11', '3.12', '3.13'], minifier_sha)


def main():
    parser = argparse.ArgumentParser(description='Generate a test report for a given python-minifier ref')
    parser.add_argument('results_dir', type=str, help='Path to results directory', default='results')
    parser.add_argument('minifier_ref', type=str, help='The python-minifier ref we are testing')
    parser.add_argument('minifier_sha', type=str, help='The python-minifier sha we are testing')
    parser.add_argument('base_ref', type=str, help='The python-minifier sha to compare with')
    parser.add_argument('base_sha', type=str, help='The python-minifier sha to compare with')
    args = parser.parse_args()

    sys.stderr.write(f'Generating report for {args.minifier_ref} ({args.minifier_sha})')

    for segment in report(args.results_dir, args.minifier_ref, args.minifier_sha, args.base_ref, args.base_sha):
        print(segment)


if __name__ == '__main__':
    main()
