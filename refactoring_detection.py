from __future__ import absolute_import
from git.repo import Repo
from gitdb.exc import BadObject
from kenja.detection.extract_method import detect_extract_method
from kenja.detection.extract_method import detect_extract_method_from_commit
import argparse
import csv


class RefactoringDetectionCommandParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Kenja a refactoring detection tool')
        self.subparsers = self.parser.add_subparsers()

        self.add_all_command()
        self.add_commits_command()

    def parse_and_execute_command(self):
        args = self.parser.parse_args()
        args.func(args)

    def add_all_command(self):
        subparser = self.subparsers.add_parser('all',
                                               help='detect refactoring from all commits in the Historage')
        subparser.add_argument('historage_dir',
                               help='path of Historage dir')
        subparser.set_defaults(func=self.detect_all)

    def detect_all(self, args):
        historage = Repo(args.historage_dir)
        extract_method_information = detect_extract_method(historage)

        candidate_revisions = set()
        for a_commit, b_commit, org_commit, a_package, b_package, c, m, method, sim in extract_method_information:
            candidate_revisions.add(b_commit)
            print self.format_for_umldiff('jedit', a_commit, b_commit, org_commit, a_package, b_package, c, m, method,
                                          sim)

        print 'candidates:', len(extract_method_information)
        print 'candidate revisions:', len(candidate_revisions)

    def format_for_umldiff(self, package_prefix, a_commit, b_commit, org_commit, a_package, b_package, c, m, method,
                           sim):
        target_method_info = [package_prefix]
        if a_package:
            target_method_info.append(a_package)
        target_method_info.extend((c, m))
        target_method = '.'.join(target_method_info)
        extracted_method_info = [package_prefix]
        if b_package:
            extracted_method_info.append(b_package)
        extracted_method_info.extend((c, method))
        extracted_method = '.'.join(extracted_method_info)
        return '"%s","%s","%s","%s","%s","%s"' % (a_commit, b_commit, org_commit, target_method, extracted_method, sim)

    def add_commits_command(self):
        subparser = self.subparsers.add_parser('commits',
                                               help='detect refactoring from commits in the csv')
        subparser.add_argument('historage_dir',
                               help='path of Historage dir')
        subparser.add_argument('commits_list',
                               help='comma separated commits list. please write a_commit hash and b_commit hash per line')
        subparser.set_defaults(func=self.detect_from_commits_list)

    def detect_from_commits_list(self, args):
        historage = Repo(args.historage_dir)
        extract_method_information = []
        try:
            for a_commit_hash, b_commit_hash in csv.reader(open(args.commits_list)):
                a_commit = historage.commit(a_commit_hash)
                b_commit = historage.commit(b_commit_hash)
                extract_method_information.extend(detect_extract_method_from_commit(a_commit, b_commit))
        except ValueError:
            print "Invalid input."
            return
        except BadObject, name:
            print "Invalid hash of the commit:", name.message

        for a_commit, b_commit, org_commit, a_package, b_package, c, m, method, sim in extract_method_information:
            print self.format_for_umldiff('jedit', a_commit, b_commit, org_commit, a_package, b_package, c, m, method,
                                          sim)
if __name__ == '__main__':
    parser = RefactoringDetectionCommandParser()
    parser.parse_and_execute_command()
