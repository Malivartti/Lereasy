import csv
import json
import os


def addTask(file, id):
    with open(file) as csvfile:
        reader = list(csv.reader(csvfile, delimiter=';'))
        dr = {}
        for i in reader:
            dr[i[0]] = {'variants': i[1].split('/'), "answer": i[2]}
    data = None
    with open('db/tasks.json', "r") as cat_file:
        if os.path.getsize("db/tasks.json") > 0:
            data = json.load(cat_file)
    with open('db/tasks.json', "w") as cat_file:
        if data:
            data[id] = dr
            cat_file.write(json.dumps(data, ensure_ascii=False))
        else:
            cat_file.write(json.dumps({id: dr}, ensure_ascii=False))
    os.remove(file)


def editTask(file, id):
    with open(file) as csvfile:
        reader = list(csv.reader(csvfile, delimiter=';'))
        dr = {}
        for i in reader:
            dr[i[0]] = {'variants': i[1].split('/'), "answer": i[2]}

    with open('db/tasks.json', "r") as cat_file:
        data = json.load(cat_file)
        data[str(id)] = dr
    with open('db/tasks.json', "w") as cat_file:
        cat_file.write(json.dumps(data, ensure_ascii=False))
    os.remove(file)


def deleteTask(id):
    with open('db/tasks.json', "r") as cat_file:
        data = json.load(cat_file)
        data.pop(str(id), None)
    with open('db/tasks.json', "w") as cat_file:
        cat_file.write(json.dumps(data, ensure_ascii=False))
