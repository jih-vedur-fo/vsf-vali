import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

class DataSeries:
    def __init__(self, x=None, y=None, x_name = None, y_names = None, x_unit = None, y_units = None):
        """
        Initializes a DataSeries instance with x and y values.

        :param x: The x values (e.g., timestamps or positions).
        :param y: The y values (e.g., data points or measurements).
        """
        self.x = np.array(x) if x is not None else np.array([])
        self.y = np.array(y) if y is not None else np.array([])
        self.x_name = None
        self.x_unit = None
        self.y_names = None
        self.y_units = None

        self.p_plt = None
        self.p_fig = None
        self.p_display = True # If the plot should be displayed
        self.p_blocking = False
    # def END
    #
    #==========================================================
    def addData(self, x, y):
        """
        Adds data to the DataSeries object.

        :param x: A 1-dimensional numpy array of x values.
        :param y: A list of numpy arrays representing y values.
        """
        # Check if x is a 1-dimensional numpy array
        if not isinstance(x, np.ndarray) or x.ndim != 1:
            raise ValueError("x must be a 1-dimensional numpy array.")

        # Check if y is a list of numpy arrays
        if not isinstance(y, list) or not all(isinstance(arr, np.ndarray) for arr in y):
            raise ValueError("y must be a list of numpy arrays.")

        # Concatenate the new data to the existing data
        self.x = np.concatenate((self.x, x))
        self.y = np.concatenate((self.y, y), axis=0) if self.y.size else np.array(y)
    # def END
    #
    #==========================================================
    def setNames(self, x_name, y_names):
        self.x_name  = x_name
        self.y_names = y_names
    # def END
    #
    #==========================================================
    def setUnits(self, x_unit, y_units):
        self.x_unit  = x_unit
        self.y_units = y_units
    # def END
    #
    #==========================================================
    def getPointsCount(self):
        if self.x is not None:
            return len(self.x)
        else:
            return -1
    # def END
    #
    #==========================================================
    def plot(self, title="Data Series Scatter Plot"):
        """
        Plots the DataSeries as a scatter plot with different colors for each Y array.

        :param title: The title of the plot.
        :param xlabel: Label for the x-axis.
        :param ylabel: Label for the y-axis.

        """
        if not self.p_display:
            mpl.use("Agg") #
        #self.p_plt = plt
        self.p_fig = plt.figure(figsize=(8, 6))

        if (not self.p_blocking):
            plt.ion() #if non-blocking



        # Generate a color map to use different colors for each series
        colors = plt.cm.get_cmap("tab10", len(self.y))

        # Plot each array in y with a different color
        print(self.y.shape)
        self.testing=False
        if self.testing:
            self.x = np.linspace(0,12)
            self.y = self.x*self.x
        # if END
        convert all values to numpy native in export....
        print(self.x.dtype)
        print(self.y.dtype)
        print(self.y.shape)
        if self.y.ndim==1:
            plt.plot(self.x, self.y, marker="o")#, marker='o', color=colors(i), label=f'Series {i+1}', alpha=0.7)
            plt.yscale("linear")
            print("X: {}".format(self.x))
            print("Y: {}".format(self.y))
        elif self.y.ndim==2:
            for i in range(self.y.shape[0]):
                x=float(self.x)
                y = self.y[i]
                plt.plot(x,y)
                # plt.plot(self.x, self.y[i], marker="o")#, marker='o', color=colors(i), label=f'Series {i+1}', alpha=0.7)
                plt.yscale("linear")
                print("X: {}".format(self.x))
                print("Y: {}".format(self.y[i]))

            # for END
        # if END
        #for idx, y_array in enumerate(self.y):
        #    plt.scatter(self.x, y_array, marker='o', color=colors(idx), label=f'Series {idx+1}', alpha=0.7)


        xlabel = ""
        ylabel = "Y"
        if self.x_name is not None and self.x_unit is not None:
            xlabel = "{} ({})".format(self.x_name,self.x_unit)
        elif self.x_name is not None:
            xlabel = "{}".format(self.x_name)
        elif self.x_unit is not None:
            xlabel = "(){})".format(self.x_unit)
        else:
            xlabel = "X"


        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend()
        plt.grid(True)
        plt.show()
    # def END

    def __repr__(self):
        return f"DataSeries(x={self.x}, y={self.y})"
    # def END
