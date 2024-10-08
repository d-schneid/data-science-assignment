import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

from data_management.cross_validation import CustomTSCVSplitter


class UserTSCVSplitter(BaseEstimator, TransformerMixin, CustomTSCVSplitter):

    def __init__(self, data_manager, n_splits, validation_set_ratio, seed):
        super().__init__(data_manager, n_splits, 'user')
        self.validation_set_ratio = validation_set_ratio
        self.random_state = np.random.RandomState(seed)
        self.validation_sets = self._assign_cv_validation_set()

    def _assign_cv_validation_set(self):
        """
        Assigns each point of the given user time-series to its respective validation set for cross-validation.
        It is iterated across the given user time-series and the last 'validation_set_ratio'% points of the remaining
        points are assigned to the same validation set for cross-validation.

        :param data_manager: The data manager instance containing the orders time-series.
        :return: The given user time-series along with a label 'cv_validation_set' indicating to which validation set
                 the respective point belongs to for cross-validation.
        """
        validation_sets = self.data_manager.get_orders_tip_train()[['user_id', 'order_number']].copy()
        validation_sets = validation_sets.groupby('user_id').apply(self._assign_cv_validation_set_by_user,
                                                                   include_groups=False)

        return validation_sets

    def _assign_cv_validation_set_by_user(self, user_validation_set):
        num_remaining_orders = len(user_validation_set)
        cv_validation_set = 1
        validation_sets_temp = user_validation_set.copy()

        for i in range(1, self.n_splits + 1):
            num_orders_to_assign = num_remaining_orders * self.validation_set_ratio
            selection_probability = num_orders_to_assign - int(num_orders_to_assign)
            if selection_probability > 0:
                num_orders_to_assign += self.random_state.choice([0, 1], p=[1 - selection_probability,
                                                                            selection_probability])
            num_orders_to_assign = int(num_orders_to_assign)

            if num_orders_to_assign > 0:
                idx_to_assign = validation_sets_temp.index[-num_orders_to_assign:]
                user_validation_set.loc[idx_to_assign, 'cv_validation_set'] = cv_validation_set
                validation_sets_temp = validation_sets_temp.iloc[:-num_orders_to_assign]
                num_remaining_orders -= num_orders_to_assign

            cv_validation_set += 1

        idx_to_assign = validation_sets_temp.index[:num_remaining_orders]
        user_validation_set.loc[idx_to_assign, 'cv_validation_set'] = cv_validation_set
        user_validation_set['cv_validation_set'] = user_validation_set['cv_validation_set'].astype(int)

        return user_validation_set

    def split(self, X, y=None, groups=None):
        for i in range(1, self.n_splits + 1):
            train = X.index[self.validation_sets['cv_validation_set'] > i].tolist()
            test = X.index[self.validation_sets['cv_validation_set'] == i].tolist()

            # print(f'Iteration {i}: Train size: {len(train)}, Test size: {len(test)}')
            yield train, test

    def get_n_splits(self, X, y, groups=None):
        return self.n_splits
