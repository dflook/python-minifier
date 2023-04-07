class Result(object):

    def __init__(self, corpus_entry, original_size, minified_size, time, outcome):
        """
        :param str corpus_entry: The name of the file in the corpus
        :param int original_size: The size of the original file
        :param int minified_size: The size of the minified file
        :param float time: The time taken to minify the file
        :param str outcome: The result of the minification
        """
        self.corpus_entry = corpus_entry
        self.original_size = original_size
        self.minified_size = minified_size
        self.time = time
        self.outcome = outcome


class ResultWriter:
    def __init__(self, results_path):
        """
        :param str results_path: The path to the results file
        """
        self._results_path = results_path

    def __enter__(self):
        self.results = open(self._results_path, 'w')
        self.results.write('corpus_entry,original_size,minified_size,time,result\n')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.results.close()

    def write(self, result):
        """
        :param Result result: The result to write to the file
        """
        self.results.write(
            result.corpus_entry + ',' +
            str(result.original_size) + ',' +
            str(result.minified_size) + ',' +
            str(result.time) + ',' + result.outcome + '\n'
        )


class ResultReader:
    def __init__(self, results_path):
        """
        :param str results_path: The path to the results file
        """
        self._results_path = results_path

    def __enter__(self):
        self.results = open(self._results_path, 'r')
        header = self.results.readline()
        assert header == 'corpus_entry,original_size,minified_size,time,result\n' or header == ''
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.results.close()

    def __iter__(self):
        return self

    def __next__(self):
        """
        :return Result: The next result in the file
        """
        line = self.results.readline()
        if line == '':
            raise StopIteration
        else:
            result_line = line.split(',')
            return Result(
                result_line[0],
                int(result_line[1]),
                int(result_line[2]),
                float(result_line[3]),
                result_line[4].rstrip()
            )
