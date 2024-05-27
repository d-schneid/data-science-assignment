from feature_engineering import DynamicFeature


class DynamicFeatureTest1(DynamicFeature):

    def __init__(self):
        super().__init__('dynamic_feature_test_1')

    def _compute_feature(self):
        self.orders_tip[self.feature] = self.orders_tip['order_number'] / self.orders_tip.groupby('user_id').transform(
            'size')

    def _analyze_feature(self):
        pass
