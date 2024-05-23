from abc import ABC, abstractmethod

import pandas as pd


class Feature(ABC):

    def __init__(self, data_store, name):
        self.data_store = data_store
        self.orders_tip = data_store.get_orders_tip()
        self.orders_joined = data_store.get_orders_joined()
        self.feature = name

    def compute_feature(self):
        self._handle_missing_values()
        self._compute_feature()
        if self._reference_outdated():
            self._update_data_store()
            self._refresh_references()

    def _handle_missing_values(self):
        self.orders_tip['days_since_prior_order'] = self.orders_tip['days_since_prior_order'].fillna(-1).astype(int)

    @abstractmethod
    def _compute_feature(self):
        pass

    def analyze_feature(self):
        pass

    @abstractmethod
    def _analyze_feature(self):
        pass

    @abstractmethod
    def _refresh_references(self):
        pass

    @abstractmethod
    def _update_data_store(self):
        pass

    @abstractmethod
    def _reference_outdated(self):
        pass


class StaticFeature(Feature):

    def __init__(self, data_store, name):
        super().__init__(data_store, name)

    def compute_feature(self):
        self._refresh_references()
        if self.feature not in self.orders_tip.columns:
            super().compute_feature()

    @abstractmethod
    def _compute_feature(self):
        pass

    @abstractmethod
    def _analyze_feature(self):
        pass

    def _refresh_references(self):
        self.orders_tip = self.data_store.get_orders_tip()
        self.orders_joined = self.data_store.get_orders_joined()

    def _update_data_store(self):
        self.data_store.merge_orders_tip(self.orders_tip, self.feature)

    def _reference_outdated(self):
        return self.orders_tip is not self.data_store.get_orders_tip()


class DynamicFeature(Feature):

    def __init__(self, data_store, name):
        super().__init__(data_store, name)
        self.orders_tip = data_store.get_orders_tip_subset()
        self.orders_joined = data_store.get_orders_joined_subset()

    def compute_feature(self):
        self._refresh_references()
        super().compute_feature()

    @abstractmethod
    def _compute_feature(self):
        pass

    @abstractmethod
    def _analyze_feature(self):
        pass

    def _refresh_references(self):
        self.orders_tip = self.data_store.get_orders_tip_subset()
        self.orders_joined = self.data_store.get_orders_joined_subset()

    def _update_data_store(self):
        self.data_store.merge_orders_tip_subset(self.orders_tip, self.feature)

    def _reference_outdated(self):
        return self.orders_tip is self.data_store.get_orders_tip_subset()


class TipHistory(StaticFeature):

    def __init__(self, data_store):
        super().__init__(data_store, 'tip_history')

    def _compute_feature(self):
        self.orders_tip[self.feature] = (self.orders_tip.assign(tip_bool=self.orders_tip['tip'].astype(bool))
                                         .groupby('user_id')['tip_bool']
                                         .transform('cumsum').shift(1) / self.orders_tip['order_number'].shift(1))
        self.orders_tip.loc[self.orders_tip['order_number'] == 1, self.feature] = -1

    def _analyze_feature(self):
        pass


class ReorderedRatio(StaticFeature):

    def __init__(self, data_store):
        super().__init__(data_store, 'reordered_ratio')

    def _compute_feature(self):
        reordered_rate = (self.orders_joined.groupby('order_id')['reordered'].mean().reset_index()
                          .rename(columns={'reordered': self.feature}))
        self.orders_tip = pd.merge(self.orders_tip, reordered_rate, on='order_id', how='left')

    def _analyze_feature(self):
        pass
