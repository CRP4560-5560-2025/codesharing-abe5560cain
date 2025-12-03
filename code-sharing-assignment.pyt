import arcpy
import os

class Toolbox(object):
    def __init__(self):
        self.label = "Simple Join and Plot"
        self.alias = "simple_join_plot"
        self.tools = [JoinCSVToGeoJSON]
#2c
class JoinCSVToGeoJSON(object):
    def __init__(self):
        self.label = "Join CSV to GeoJSON and Plot"
        self.description = "Converts GeoJSON to feature class, joins CSV, and makes the simple graph."

    def getParameterInfo(self):
        geojson = arcpy.Parameter(
            displayName="Input GeoJSON file",
            name="in_geojson",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")
        geojson.filter.list = ["json", "geojson"]
#2a
        csv = arcpy.Parameter(
            displayName="Input CSV file",
            name="in_csv",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")
        csv.filter.list = ["csv"]
#2b
        out_fc = arcpy.Parameter(
            displayName="Output Feature Class",
            name="out_fc",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")
#2d
        join_field = arcpy.Parameter(
            displayName="Join field name (same in both files)",
            name="join_field",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
#2e
        disp_opt = arcpy.Parameter(
            displayName="Display option",
            name="display_option",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        disp_opt.filter.type = "ValueList"
        disp_opt.filter.list = ["Single symbol", "Graduated colors", "Unique values"]

        out_png = arcpy.Parameter(
            displayName="Output graph PNG",
            name="out_png",
            datatype="DEFile",
            parameterType="Required",
            direction="Output")

        return [geojson, csv, out_fc, join_field, disp_opt, out_png]
    
#2f & #2g 

    def execute(self, parameters, messages):
        import matplotlib
        matplotlib.use("Agg")          
        import matplotlib.pyplot as plt
        import pandas as pd

        in_geojson = parameters[0].valueAsText
        in_csv = parameters[1].valueAsText
        out_fc = parameters[2].valueAsText
        join_field = parameters[3].valueAsText
        display_option = parameters[4].valueAsText  
        out_png = parameters[5].valueAsText

        messages.addMessage("Converting GeoJSON to feature class...")
        temp_fc = arcpy.conversion.JSONToFeatures(in_geojson, arcpy.env.scratchGDB + os.sep + "temp_fc").getOutput(0)

        messages.addMessage("Loading CSV table...")
        csv_table = arcpy.conversion.TableToTable(
            in_csv,
            arcpy.env.scratchGDB,
            "csv_table"
        ).getOutput(0)

        messages.addMessage("Joining CSV to feature class...")
        arcpy.management.AddJoin(temp_fc, join_field, csv_table, join_field, "KEEP_COMMON")

        arcpy.management.CopyFeatures(temp_fc, out_fc)
        messages.addMessage("Output feature class created: {}".format(out_fc))

        messages.addMessage("Creating graph from CSV data...")
        df = pd.read_csv(in_csv)

        x_labels = df[join_field].head(10).index.astype(str)
        y_values = df[join_field].head(10)

        plt.figure()
        plt.bar(x_labels, y_values)
        plt.xlabel("Row")
        plt.ylabel(join_field)
        plt.title("Simple graph of {}".format(join_field))
        plt.tight_layout()
        plt.savefig(out_png)
        plt.close()

        messages.addMessage("Graph saved to: {}".format(out_png))
