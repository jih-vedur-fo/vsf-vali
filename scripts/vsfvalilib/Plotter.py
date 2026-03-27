import matplotlib.pyplot as plt

class Plotter:
    def __init__(self):
        self.dataseries = None


        self.ds_plt = None
    # def END
    #
    #=======================================================
    def plotDataSeries(self, data_series_list):
        # Plot a list of DataSeries objects as scatter plots''
        self.dateseries = data_series_list

        plt.figure(figsize=(10, 6))
        self.ds_plt = plt


        for ds in self.dataseries:
            print("ds shape {}".format(ds.shape))
            plt.scatter(ds.x, ds.y, label=ds.names)
        # for END

        plt.xlabel('Datetime')
        plt.ylabel('Value')
        plt.title('Scatter Plot of Data Series')
        plt.legend()
        plt.grid(True)
        plt.show()
    # def END
