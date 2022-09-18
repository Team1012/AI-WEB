# Kagiso Yako
# 31/08/2022
# Class for executing high level sqlite instructions and database interaction and management.

import sqlite3
from SQL_queries import SQL_queries

class DB_manager:
    def __init__(self, DB_name, specializations):
        self.DB_name = DB_name
        self.AI_fields = specializations
        self.AI_fields.sort()

    def researchers_per_inst(self):
        conn = sqlite3.connect(self.DB_name)
        cursor = conn.cursor()
        cursor.execute("SELECT Institution, count(Institution) FROM Researchers group by institution " +
                       "order by count(institution) DESC;")
        count_inst = cursor.fetchall()
        institutions = []
        frequencies = []
        for i in range(len(count_inst)):
            institutions.append(count_inst[i][0])
            frequencies.append(count_inst[i][1])
        return institutions , frequencies

    def researchers_per_rating(self):
        frequencies = [0, 0, 0, 0, 0]
        ratings = ["A", "B", "C", "P", "Y"]
        conn = sqlite3.connect(self.DB_name)
        cursor = conn.cursor()
        query = SQL_queries.count_records("Researchers", single_column="Rating")
        query += SQL_queries.group_by("Rating")
        cursor.execute(query)
        values = cursor.fetchall()
        for i in range(len(values)):
            frequencies[i] = (values[i][0])
        return ratings, frequencies

    def researcher_rating_by_inst(self, institution):
        frequencies = [0, 0, 0, 0, 0]
        ratings = ["A", "B", "C", "P", "Y"]
        conn = sqlite3.connect(self.DB_name)
        cursor = conn.cursor()
        query = SQL_queries.count_records("Researchers", single_column="Rating") + " WHERE "
        query += SQL_queries.compare_to_other("Institution", "\"" + institution + "\"", "=", )
        query += SQL_queries.group_by("Rating")
        cursor.execute(query)
        values = cursor.fetchall()
        for i in range(len(values)):
            frequencies[i] = (values[i][0])

        return ratings, frequencies

    def researchers_per_specialization(self):

        conn = sqlite3.connect(self.DB_name)
        cursor = conn.cursor()

        field_X = []
        num_researchers_Y = []

        for field in self.AI_fields:
            query = "SELECT Count(Surname) FROM Researchers "
            query += "WHERE Specializations LIKE  '%" + field + "%';"

            cursor.execute(query)
            data = cursor.fetchall()

            field_X.append(field)
            num_researchers_Y.append(data[0][0])

        return field_X, num_researchers_Y

    def researcher_dist_by_specialization(self, field):

        conn = sqlite3.connect(self.DB_name)
        cursor = conn.cursor()

        ratings = ["A", "B", "C", "P", "Y"]
        rating_distribution = [0] * len(ratings)
        query = "SELECT Count(Rating) FROM Researchers "
        query += "WHERE Specializations LIKE '%" + field + "%' "
        query += "GROUP BY Rating"

        cursor.execute(query)
        data = cursor.fetchall()
        for i in range(len(data)):
            rating_distribution[i] = data[i][0]
        return ratings, rating_distribution

    def specialization_dist_by_inst(self, inst):

        conn = sqlite3.connect(self.DB_name)
        cursor = conn.cursor()

        specialization_distribution = []

        for field in self.AI_fields:
            query = "SELECT  Specializations, Count(Specializations) FROM Researchers "
            query += "WHERE Institution LIKE '%" + inst + "%'  AND specializations LIKE %" + field + "% "
            query += "GROUP BY Institution"

            cursor.execute(query)
            data = cursor.fetchall()

            specialization_distribution.append(data)

        return self.AI_fields, specialization_distribution
    
    def get_researchers(self):
    
        conn = sqlite3.connect(self.DB_name)
        cursor = conn.cursor()
    
        query = "SELECT Surname FROM Researchers"
    
        cursor.execute(query)
        data = cursor.fetchall()
    
        researchers = []
        
    
        for item in data:
            
            surname = str(item[0])
            researchers.append(surname)
    
        return researchers
    
    
    def get_institutions(self):
    
        conn = sqlite3.connect(self.DB_name)
        cursor = conn.cursor()
    
        query = "SELECT DISTINCT Institution FROM Researchers"
    
        cursor.execute(query)
        data = cursor.fetchall()
    
        institutions = []
        
    
        for item in data:
            
            surname = str(item[0])
            institutions.append(surname)
    
        return institutions

    
    # ai_topics is an arrray of different AI topics, ["Artificial Intelligence", "Machine Learning", "Deep learning",...]
    def clean_data(self, ai_topics):

        conn = sqlite3.connect(self.DB_name)
        cursor = conn.cursor()

        query = "DELETE FROM Researchers"

        specilizations = " WHERE "
        primary = " AND "
        secondary = " AND "

        for index in range(len(ai_topics)):

            if index == len(ai_topics)-1:

                specilizations += "Specializations NOT LIKE '%" + ai_topics[index] + "%'"
                primary += "PrimaryResearch NOT LIKE '%" + ai_topics[index] + "%'"
                secondary += "SecondaryResearch NOT LIKE '%" + ai_topics[index] + "%'"

            else:

                specilizations += "Specializations NOT LIKE '%" + ai_topics[index] + "%' AND "
                primary += "PrimaryResearch NOT LIKE '%" + ai_topics[index] + "%' AND "
                secondary += "SecondaryResearch NOT LIKE '%" + ai_topics[index] + "%' AND "
    
        query += specilizations
        query += primary
        query += secondary

        query += " OR Specializations IS NULL "
        query += " OR PrimaryResearch IS NULL "
        query += " OR SecondaryResearch IS NULL"

        #print(query)
        cursor.execute(query)

        
        query2 = "SELECT * FROM Researchers"
        cursor.execute(query2)
        new_data = cursor.fetchall()
        
        return new_data # returns a new table after the cleaning the data
