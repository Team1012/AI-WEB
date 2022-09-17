# AI researchers are based at South Africa’s
# 26 public universities and other research-based organisations. They publish the results of their research in
# a variety of venues, including journals, conference proceedings and workshop proceedings. The
# application will draw from and consolidate data from multiple public research data sources, including the
# researcher rating system used by the National Research Foundation (NRF) and Microsoft Academic
# Graph (MAG). A web based interface must be provided for users to perform queries and visualise
# information about the research community including: a) dominant research areas/topics, publications
# venues, collaborations (co-authors) and impact (citations) (b) in which
# researchers are based (c) finding interesting trends and patterns over time, (c) appropriate metrics to
# assess and analyse the community and network structure, and (d) manual update and synchronisation
# functionality with MAG, the NRF and other public data sources.

import sqlite3
from flask import Flask, render_template, request
from Analysis import Analysis
from DB_auto_setup import DB_auto_setup
from DB_manager import DB_manager
from SQL_queries import SQL_queries





# Global variables
# Defines the columns for the csv file and the columns for the NRF researchers table

from googleScholarOperations import handle_query
import plotly as plotly
import pandas as pd
import json
import plotly.express as px

from test import notdash








# Global variables
# Defines the columns for the csv file and the columns for the NRF researchers table
from DB_manager import DB_manager
from SQL_queries import SQL_queries
from googleScholarOperations import handle_query
import plotly as plotly
import pandas as pd
import json
import plotly.express as px

from test import notdash





# Global variables
# Defines the columns for the csv file and the columns for the NRF researchers table

secondary_options = []
primary_options = []
specializations_options = []
table_name = "Researchers"
NRF_Excel_path = "Data/Current-Rated-Researchers-22-August-2022.xlsx"
excel_sheet_name = 'Current Rated Researchers (Webs'
csv_file = "Data/DB.csv"
NRF_database_file = "Data/Database.db"
url = "https://www.nrf.ac.za/wp-content/uploads/2022/08/Current-Rated-Researchers-22-August-2022.xlsx"
specializations = ["Artificial Intelligence",
                   "Computer vision",
                   "Natural language processing",
                   "Artificial Neural Networks",
                   "Robotics",
                   "Deep learning",
                   "Knowledge representation and reasoning",
                   "Search methodologies",
                   "Machine learning",
                   "Reinforcement learning"]
columns = ["id INTEGER primary key autoincrement",
           "Surname TEXT",
           "Initials TEXT",
           "Title TEXT",
           "Institution TEXT",
           "Rating TEXT",
           "Rating_Start DATE",
           "Rating_Ending DATE",
           "PrimaryResearch TEXT",
           "SecondaryResearch TEXT",
           "Specializations TEXT"]

columns_csv = ["Surname",
               "Initials",
               "Title",
               "Institution",
               "Rating",
               "Rating_Start",
               "Rating_Ending",
               "PrimaryResearch",
               "SecondaryResearch",
               "Specializations"]

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/researchers", methods=["GET"])
def researchers():
    rows = None
    rating_dist_JSON = my_JSONs.researchers_per_rating_JSON()
    options_column = ["Surname", "Institution"]
    options = []
    try:
        conn = sqlite3.connect(NRF_database_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(SQL_queries.get_table(table_name))
            rows = cursor.fetchall()
        except sqlite3.Error:
            print("Unable to obtain rows")
        options = fetch_options("Researchers", options_column)
    except sqlite3.Error:
        print("Could not connect to database!")
    finally:
        if rows is not None:
            return render_template("researchers.html", rows=rows, options=options, sec=secondary_options,
                                   prim=primary_options, spec=specializations_options, rating_dist=rating_dist_JSON)
        else:
            return render_template("Error_page.html")


@app.route("/institutions", methods=["GET"])
def institutions():
    rows = None
    options = None
    conn = sqlite3.connect(NRF_database_file)
    conn.row_factory = sqlite3.Row
    try:

        cursor = conn.cursor()
        options = fetch_options("Institutions", option_columns=["Institution", "Location"])
        try:
            cursor.execute(SQL_queries.institutions_table() + " GROUP BY Institutions.institution ")
            rows = cursor.fetchall()
        except sqlite3.Error:
            print("Unable to obtain rows")
    except sqlite3.Error:
        print("Could not connect to database!")
    if rows is not None or rows is None:
        res_vs_inst_JSON = my_JSONs.researchers_per_inst_JSON()
        return render_template("institutions.html", res_vs_I=res_vs_inst_JSON, rows=rows, options=options)

@app.route("/callback_topics_data", methods=["GET"])
def topics_data():
    field = request.args.get('data')
    return my_JSONs.researchers_per_topic_JSON(field)



@app.route("/trendsAndAnalysisGoogle")
def trendsAndAnalysisGoogle():
   return render_template('TrendsAndAnalysisGoogle.html', graphJSON=notdash())


@app.route("/trendsAndAnalysis", methods=["GET"])
def trendsAndAnalysis():
    JSON_general = my_JSONs.researchers_per_rating_JSON()
    JSON_institution = my_JSONs.researchers_per_inst_JSON()
    ratings_pie_JSON = my_JSONs.rating_pie_chart_JSON()
    ratings_per_topic = my_JSONs.researchers_per_topic_JSON("Artificial intelligence")
    ratings = my_JSONs.get_ratings_list()
    researchers_per_field = my_JSONs.researchers_per_field_JSON()
    rating_percentages = []
    for rating in ratings:
        rating_percentages.append(round(int(rating)/sum(ratings) * 100))
    maxi = round(max(ratings)/sum(ratings) * 100)
    mini = round(min(ratings)/sum(ratings) * 100)
    rating_categories = ["A", "B", "C", "P", "Y"]
    min_rating = rating_categories[ratings.index(min(ratings))]
    max_rating = rating_categories[ratings.index(max(ratings))]
    rows = None
    conn = sqlite3.connect(NRF_database_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_queries.get_table(table_name))
        rows = cursor.fetchall()
    except sqlite3.Error:
        print("Unable to obtain rows")
    return render_template("TrendsAndAnalysis.html", general=JSON_general, institution=JSON_institution,
                           rating_pie=ratings_pie_JSON, ratings=ratings, rating_p=rating_percentages, sum=sum(ratings),
                           specialization_dist=researchers_per_field, ratings_per_topic=ratings_per_topic, max=maxi,
                           min=mini, min_r=min_rating, max_r=max_rating, rows=rows)



@app.route("/search_results")
def search_researchers():
    if request.method == "GET":
        rows = None
        try:
            item = request.args.get("researcher_search")
            operators = ["LIKE"] * len(columns_csv)
            wild_card_wrapped_item = "%" + item + "%"
            query = SQL_queries.get_subset(table_name, columns_csv, operators, to_one=wild_card_wrapped_item, wrap=True)
            conn = sqlite3.connect(NRF_database_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        except sqlite3.Error:
            print("sqlite3.Error: Could not execute search.")
        finally:
            if rows is not None:
                if len(rows) > 0:
                    return render_template("search_researchers.html", rows=rows, length=len(rows))
                else:
                    return render_template("NoItemsFound.html")
            else:
                return render_template("Error_page.html")

@app.route("/inst_search_results")
def search_Institutions():
    if request.method == "GET":
        rows = None
        try:
            item = request.args.get("Institution_search")
            conn = sqlite3.connect(NRF_database_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(SQL_queries.institutions_table_search_query(item))
            rows = cursor.fetchall()

        except sqlite3.Error:
            print("sqlite3.Error: Could not execute search.")
        finally:
            if rows is not None:
                if len(rows) > 0:
                    return render_template("search_institutions.html", rows=rows, length=len(rows))
                else:
                    return render_template("NoItemsFound.html")
            else:
                return render_template("Error_page.html")


@app.route("/inst_<institution>")
def universityofcpt(institution):
    institution = institution.replace('+', ' ')
    institution_dist, values = my_JSONs.researcher_rating_by_inst_JSON(institution)
    my_sum = 0
    rows = None
    try:
        conn = sqlite3.connect(NRF_database_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        quoted_inst = "\"" + institution + "\""
        cursor.execute(SQL_queries.get_table(table_name) + SQL_queries.compare_to_other("Institution",
                                                                                        quoted_inst, "=",
                                                                                        prefix="WHERE"))
        rows = cursor.fetchall()
        my_sum = sum(values)
    except sqlite3.Error:
        print("Failed to connect to database for the creation of institution.html")
    if rows is not None:
        return render_template("institution.html", institution_dist=institution_dist, institution=institution,
                               sum=my_sum, values=values, rows=rows)
    else:
        return render_template("Error_page.html")


# *
# *
# Supporting methods
# *
# *

def fetch_options(table_n, option_columns):
    conn = sqlite3.connect(NRF_database_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    options = []
    for i in range(len(option_columns)):
        try:
            cursor.execute(SQL_queries.get_table(table_n, single_column=option_columns[i], DISTINCT=True))
            options.append(cursor.fetchall())

        except sqlite3.Error:
            print("Unable to obtain " + option_columns[i] + "!")
    return options

def research_fields(column):
    conn = sqlite3.connect(NRF_database_file)
    cursor = conn.cursor()

    query = SQL_queries.get_table("Researchers", single_column=column, DISTINCT=True)

    cursor.execute(query)
    data = cursor.fetchall()

    research_options = []

    for item in data:
        string_fields = str(item[0])
        fields = string_fields.split(";")

        for option in fields:
            if option not in research_options:

                research_options.append(option)

    research_options.sort()
    return research_options


if __name__ == '__main__':
    # Creating objects to be used in program
    my_manager = DB_manager(NRF_database_file, specializations)
    my_JSONs = Analysis(NRF_database_file, specializations)
    auto = DB_auto_setup(NRF_database_file, NRF_Excel_path, excel_sheet_name, columns_csv, csv_file, table_name,
                         columns, url, specializations)
    # ****
    # ****
    # ****
    # Test code: Delete!!!
    # ****
    # ****
    # ****

    auto.set_up_DB()

    # ****
    # ****
    # ****
    # ****
    # ****
    # ****

    #  Retrieving options for select boxes and setting them.
    #  Possibly heavy computation to be done on start up and on update.

    primary_options = research_fields("PrimaryResearch")
    secondary_options = research_fields("SecondaryResearch")
    specializations_options = research_fields("Specializations")

    my_manager.researcher_rating_by_inst("University of Cape Town")

    app.run(debug=True)
