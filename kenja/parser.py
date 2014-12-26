from __future__ import absolute_import
import os
from subprocess import (
    Popen,
    PIPE,
    )
from multiprocessing import (
    Pool,
    cpu_count
    )


def execute_parser(cmd, src):
    p = Popen(cmd, stdin=PIPE)
    p.stdin.write(src)
    p.communicate()
    return True


class ParserExecutor:
    def __init__(self, output_dir, parser_path, processes=None):
        self.output_dir = output_dir
        self.parser_path = parser_path
        self.processes = processes if processes else cpu_count()
        self.pool = Pool(self.processes)
        self.closed = False

    def parse_blob(self, blob):
        src = blob.data_stream.read()
        cmd = self.make_cmd(blob.hexsha)

        if(self.closed):
            self.pool = Pool(self.processes)
            self.closed = False

        self.pool.apply_async(execute_parser, args=[cmd, src])

    def make_cmd(self, hexsha):
        cmd = ["java",
               "-jar",
               self.parser_path,
               os.path.join(self.output_dir, hexsha)
               ]
#        print cmd
        return cmd

    def join(self):
        self.pool.close()
        self.closed = True
        self.pool.join()
        self.pool = None


class ParserExecutor_py(ParserExecutor): # tmp
    def make_cmd(self, hexsha):
        cmd = ["python",
               self.parser_path,
               os.path.join(self.output_dir, hexsha)
               ]
        return cmd
