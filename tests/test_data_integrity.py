import unittest
import pandas as pd
import numpy as np
from src.main import *

class test_tcga_scraping(unittest.case):

    def test_data_integrity(self):
        """
        Test if the data pivoted is the same as the data downloaded from the GDC API
        """

        df = get_data(file_uuid = "9eda745e-b182-4611-a4a6-242db8a07337")
        data = dict(zip(df["gene_id"].values, df[type_of_counts].values))
        gene_expression_temp = pd.DataFrame(data = data, index = [inv_file_dict[case["file_name"]]] )
        gene_expression = pd.concat([gene_expression, gene_expression_temp])

        # np.testing.assert_array_equal returns None if the arrays are equal
        self.assertIsNone(np.testing.assert_array_equal(gene_expression.values[0], df["unstranded"].values))