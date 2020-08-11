import ast
import csv
import inspect
import json
import os
import sqlite3
import time
from abc import abstractmethod
from datetime import datetime
import pandas as pd

import Persistence as p
from AsyncCollector import AsyncCollector


class Project(object):
    def __init__(self, pagination_mask):
        self.pagination_mask = pagination_mask
        self.name = inspect.getmodule(self).__file__.split("\\")[-2]
        self.db = p.Database("ScrappingDB.db")
        self.scrapper = AsyncCollector()
        self.__install_db()
        self.__create_project()
        self.id = self.get_id()
        self.import_selectors()

    @staticmethod
    def __import_sql_file(file):
        with open(file, "r") as f:
            content = f.read()
        return content

    def __install_db(self):

        # Import SQL File
        sql = self.__import_sql_file("install.sql")

        if os.stat(self.db.db_name).st_size == 0:
            print("Création de la base de données {} ...".format(self.db.db_name))
            self.db.db_cur.executescript(sql)
        else:
            print("La base de donnée existe déja")

    def get_id(self):
        query = "select id from project where project.name = ?"
        result = self.db.query(query, [self.name]).fetchone()
        return None if result is None else result[0]

    def __create_project(self):
        result = None
        if self.get_id() is None:
            query = "insert into project(name, pagination_mask) values(?,?)"
            result = self.db.query(query, [self.name, self.pagination_mask])
            print("Cération du projet {} ...".format(self.name))
            self.id = self.get_id()
            print("Le projet {} a été créé dans la base de données avec l'id {}.".format(self.name, self.get_id()))
        return result

    def save_urls(self, urls):
        if urls:
            query = "insert into link(fk_project, link, created) values(?, ?, ?)"
            data = []
            for item in urls:
                line = []
                line.insert(0, self.id)
                line.insert(1, item)
                line.insert(2, time.time())
                data.append(line)

            self.db.query_many(query, data)

    def __convert_csv_to_list(self, file):
        with open(file, newline='') as f:
            result = list(csv.reader(f, delimiter=','))
            for item in result:
                item.insert(0, self.id)
                item.insert(4, time.time())
        return result

    def __timestamp_to_datetime(self, timestamp):
        return datetime.fromtimestamp(timestamp)

    def __delete_selectors(self):
        query = "delete from selector where fk_project = ?"
        self.db.query(query, [self.id])
        print("Suppression des sélecteurs actuels du projet {}...".format(self.name))

    def import_selectors(self):
        file = "./Projects/" + self.name + "/selectors.csv"
        if os.path.isfile(file):
            query = "insert into selector(fk_project, field, selector, created) values(?, ?, ?, ?)"
            try:
                self.__delete_selectors()
                print("Importation des sélecteurs depuis selectors.csv...")
                self.db.query_many(query, self.__convert_csv_to_list(file))
            except sqlite3.IntegrityError as e:
                print("\033[31mUn selecteur existe déjà, merci de corriger votr fichier et rééssayer.\033[0m")
                print(e)
        else:
            print(
                "\033[31mLe fichier selectors.csv n'existe pas dans le dossier du projet {}.\033[0m".format(self.name))

    def reset_project(self):

        query = ["delete from project where id = ?; ",
                 "delete from link where fk_project = ?; ",
                 "delete from scrapped_data where fk_project = ?;",
                 "delete from selector where fk_project = ?;"]

        try:
            [self.db.query(q, [self.id]) for q in query]
        except sqlite3.IntegrityError as e:
            print("\033[31mProblème de réinitialisation.\033[0m")
            print(e)
        print(
            "Le projet {} est réinitialisé, toutes les données sont supprimées de la base de données".format(self.name))
        self.__create_project()
        self.import_selectors()

    def get_links(self, valid, passed):
        query = "select id, link from link where fk_project = ? and valid = ? and passed = ?"
        result = self.db.query(query, [self.id, valid, passed]).fetchall()
        return result

    def get_selectors(self):
        query = "select field, selector from selector where fk_project = ?"
        result = self.db.query(query, [self.id]).fetchall()
        return dict(result)

    def scrapped_data_to_dataframe(self):
        query = "select data from scrapped_data where fk_project = ?"
        result = self.db.query(query, [self.id]).fetchall()
        output = []
        for item in result:
            try:
                line = json.loads(json.dumps(ast.literal_eval(item[0])))
                for k, v in line.items():
                    line[k] = None if v == '' else v
                output.append(line)
            except json.decoder.JSONDecodeError as e:
                print(e, item[0])

        # output = [json.loads(item[0].replace("\'", '"')) for item in result]
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        df = pd.DataFrame(output)

        # Post process
        df['created'] = pd.to_datetime(df['created'])
        return df

    def scrapped_data_to_csv(self, filename):
        project_path = '\\'.join(inspect.getmodule(self).__file__.split("\\")[:-1])
        self.scrapped_data_to_dataframe().to_csv(f"{project_path}\\{filename}.csv", index=False)
        print(f"Fichier {filename}.csv exporté avec succès")

    def scrapped_data_to_excel(self, filename):
        project_path = '\\'.join(inspect.getmodule(self).__file__.split("\\")[:-1])
        self.scrapped_data_to_dataframe().to_excel(f"{project_path}\\{filename}.xlsx", index=False, sheet_name=self.name)
        print(f"Fichier {filename}.xlsx exporté avec succès")

    def save_scrapped_data(self, data):
        query = "insert into scrapped_data(fk_project, link, data, created) values(?, ?, ?, ?)"
        data_to_send = []
        for item in data:
            line = []
            line.insert(0, self.id)
            line.insert(1, item['fk_link'])
            line.insert(2, json.dumps(item))
            line.insert(3, time.time())
            data_to_send.append(line)

        result = self.db.query_many(query, data_to_send)
        print("{} lignes insérées dans la base de données, dernier id : {}".format(result.rowcount, result.lastrowid))
        return result

    @abstractmethod
    def change_pagination(self, value):
        pass

    @abstractmethod
    def process_elements(self, elements: dict):
        pass

    @abstractmethod
    def start_scrapping(self, start_page_number, end_page_number):
        pass

    @abstractmethod
    def get_page_urls_from_listing_page(self, listing_page):
        pass
