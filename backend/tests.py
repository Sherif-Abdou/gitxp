import unittest
from time import sleep
from points import *
import database
from sqlalchemy.orm import Session
from sqlalchemy import select

class BackendMethods(unittest.TestCase):
    # Mainly checks that the database can read data
    def test_read_database(self):
        engine = database.init_db(False)
        with Session(engine) as session:
            items = session.execute(select(database.User)).all()
            self.assertNotEqual(len(items), 0)



    def test_commit_points(self):
        commit_source = CommitEvent(16, 2)
        points = commit_source.generate_points()
        self.assertEqual(points, 3.25)

    def test_pr_points(self):
        commit_source = ClosePullRequestEvent(16, 2)
        points = commit_source.generate_points()
        self.assertEqual(points, 16.25)

    def test_issue_points(self):
        issue_source = OpenIssueEvent()
        self.assertEqual(issue_source.generate_points(), 1)

if __name__ == '__main__':
    unittest.main()
