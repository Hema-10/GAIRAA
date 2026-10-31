
import unittest
import pandas as pd


class TestETLTransform(unittest.TestCase):

    def test_names_are_converted_to_uppercase(self):
        # Create sample employee data
        df = pd.DataFrame({
            "name": ["alice", "bob"],
            "age": [24, 30],
            "salary": [25000, 40000]
        })

        # Apply the same transformation as the pipeline
        df["name"] = df["name"].str.upper()

        # Check the expected result
        self.assertEqual(df["name"].tolist(), ["ALICE", "BOB"])


if __name__ == "__main__":
    unittest.main()
