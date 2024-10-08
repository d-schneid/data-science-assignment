import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from analysis import Analysis


class ReorderedAnalysis(Analysis):

    def __init__(self, data_manager):
        super().__init__(data_manager)
        self.tip_probabilities = None
        self. reordered_probabilities = None
        self.order_counts_per_product = None

    def _analyze(self):
        self.tip_probabilities = self.orders_joined.groupby('product_id')['tip'].mean()
        self.reorder_probabilities = self.orders_joined.groupby('product_id')['reordered'].mean()

    def _show_results(self, save_plots=False):
        self._plot_scatter(self.tip_probabilities, self.reorder_probabilities, save_plots)

    def _plot_scatter(self, tip_probabilities, reorder_probabilities, save_plots=False):
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))

        sns.kdeplot(x=reorder_probabilities, y=tip_probabilities, cmap='viridis', fill=True, bw_adjust=.5, ax=ax)
        ax.set_xlabel('Reordered Rate')
        ax.set_ylabel('Tip Probability')
        plt.title('Tip Probability vs Reorder Rate by Product')

        plt.show()

        if save_plots:
            self._save_plot(fig, 'reordered_analysis.png')

