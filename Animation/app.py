from scipy.spatial import Voronoi, voronoi_plot_2d
from shiny import App, render, reactive, ui
from matplotlib import pyplot as plt, patches
import numpy as np

# Initialize the plot
fig, ax = plt.subplots(1,2,figsize=(12,6))

games = {1:'Game 1', 2:'Game 2'}

# App design
# ------------------------------------------------------------------------
app_ui = ui.page_fluid(
    ui.panel_title("Rebound Zone"),

    ui.layout_sidebar(

      ui.panel_sidebar(
        ui.input_select("player_select", "Select Player", games),
        ui.input_slider("play", "Play Number", 0, 200, 0)
      ),

      ui.panel_main(
        ui.output_plot("plot", height='500px'),
      ),
    ),
)

# App logic
# ------------------------------------------------------------------------
def server(input, output, session):


    @output(id='plot')
    @render.plot
    def plot():
      ax[0].scatter(0,input.play())
      return ax[0]

app = App(app_ui, server, debug=False)
