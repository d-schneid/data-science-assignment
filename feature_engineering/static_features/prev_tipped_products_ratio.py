import numpy as np
import pandas as pd

from feature_engineering import StaticFeature


class PrevTippedProductsRatio(StaticFeature):

    def __init__(self):
        super().__init__('prev_tipped_products_ratio')
        self.feature_type = self.STEADY_FEATURE

    def _prev_tipped_products_ratio_calculation(self, user_orders):
        cumulative_products = set()
        for idx, order in user_orders.iterrows():
            prev_tipped_products = cumulative_products.intersection(order['products'])
            user_orders.at[idx, self.feature] = len(prev_tipped_products) / len(order['products'])
            if order['tip'] == 1.0:
                cumulative_products.update(order['products'])
        return user_orders

    def _compute_feature(self):
        grouped = (self.orders_joined.groupby(['user_id', 'order_number', 'order_id']).agg(
            products=('product_id', lambda x: set(x)), tip=('tip', 'first'))).reset_index()

        grouped = grouped.groupby('user_id').apply(self._prev_tipped_products_ratio_calculation,
                                                   include_groups=False).reset_index(
            drop=False).drop(columns='level_1')

        self.orders_tip = pd.merge(self.orders_tip, grouped[['order_id', self.feature]], on='order_id', how='left')

        self.orders_tip.loc[self.orders_tip['order_number'] == 1, self.feature] = np.nan

