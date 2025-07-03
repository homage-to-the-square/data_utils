import pandas as pd

class GeneralCVSplit:
    """
    General class to split indices.
    """

    def __init__(self):
        raise NotImplementedError

    def split(self, indices):
        raise NotImplementedError


class RollingWindowSplit(GeneralCVSplit):
    """
        Implements a (fixed) rolling window splitter.
    """
    def __init__(self, train_size: int, test_size: int, gap: int = 0):
        self.train_size = train_size
        self.test_size = test_size
        self.gap = gap

        self.min_size = self.train_size + self.test_size + self.gap
        
    def split(self, indices: pd.Series):
        assert (
            len(indices) >= self.min_size
        ), "Error: Number of indices is less than the minimum index size for training, test, and gap."
        
        train_start_index = 0
        while train_start_index + self.min_size <= len(indices):
            end_train = train_start_index + self.train_size
            start_test = end_train + self.gap  
            end_test = start_test + self.test_size
            yield indices.iloc[train_start_index:end_train], indices.iloc[
                start_test:end_test
            ]
            train_start_index += 1
