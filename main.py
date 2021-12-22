import json
import random
import sys

import pandas as pd
import pyrebase
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def Data_Clean():
    firebaseConfig = {"apiKey": "AIzaSyD-OZkuZ3qv2XjlPSm8gSrPG4Vrfseo_Ck",
                      "authDomain": "planitpk-cf006.firebaseapp.com",
                      "databaseURL": "https://planitpk-cf006-default-rtdb.firebaseio.com",
                      "projectId": "planitpk-cf006",
                      "storageBucket": "planitpk-cf006.appspot.com",
                      "messagingSenderId": "1091135325457",
                      "appId": "1:1091135325457:web:4ae3b47d1e8f09719b38b0",
                      "measurementId": "${config.measurementId}"

                      }

    firebase = pyrebase.initialize_app(firebaseConfig)

    db = firebase.database()
    auth = firebase.auth()

    users = db.child("Users").get()
    # print (users.val())

    user = None;
    for user in users.val():
        print("For User: ", user)
        likes = []
        favorites = db.child("Users").child(user).child("preferences").child("favorites").get()

        # if favorites.val():
        #     print("FAVORITES exist")
        # else:
        #     print("FAVORITES empty")

        recommendations = db.child("Users").child(user).child("preferences").child("temp").get()

        res = []
        if recommendations is not None:
            for i in recommendations.val():
                if i not in res:
                    res.append(i)
            j = 0
            # db.child("Users").child(user).child("preferences").child("recommendations").remove()
            for i in res:
                print("name is : ", i)
                if favorites.val():
                    db.child("Users").child(user).child("preferences").child("recommendations").update({str(j): str(i)})
                j += 1
        else:
            continue
        db.child("Users").child(user).child("preferences").child("temp").remove()


def execute():


    firebaseConfig = {"apiKey": "AIzaSyD-OZkuZ3qv2XjlPSm8gSrPG4Vrfseo_Ck",
                    "authDomain": "planitpk-cf006.firebaseapp.com",
                    "databaseURL": "https://planitpk-cf006-default-rtdb.firebaseio.com",
                    "projectId": "planitpk-cf006",
                    "storageBucket": "planitpk-cf006.appspot.com",
                    "messagingSenderId": "1091135325457",
                    "appId": "1:1091135325457:web:4ae3b47d1e8f09719b38b0",
                    "measurementId": "${config.measurementId}"

                    }

    firebase = pyrebase.initialize_app(firebaseConfig)

    db = firebase.database()
    auth = firebase.auth()

    locs = db.child("Locations").get()

    userLike = db.child("Users").get()
    # print (userLike.val())


    print(len(userLike.val()))

    likes = []

    i = 0
    for user in userLike.each():
        value = user.val()['preferences']
        # print(value['uid'])
        likes.append(value['favorites'])
        # print('count',user.val())
        # print('count',likes[i],end='\n\n\n')
        i += 1

    lnames = []
    lcategory = []
    ldesc = []
    for loc in locs.each():
        lnames.append(loc.val()['name'])
        lcategory.append(loc.val()['category'])
        ldesc.append(loc.val()['Desc'])

    df = pd.DataFrame({'name': lnames})
    df['category'] = lcategory
    df['description'] = ldesc

    tfidf = TfidfVectorizer(stop_words='english')
    df['description'] = df['description'].fillna('')

    overview_matrix = tfidf.fit_transform(df['description'])

    similarity_matrix = linear_kernel(overview_matrix, overview_matrix)

    mapping = pd.Series(df.index, index=df['name'])


    def intersection(lst1, lst2):
        return list(set(lst1) & set(lst2))


    def guess(locInput):
        indexLoc = mapping[locInput]
        similarity_score = list(enumerate(similarity_matrix[indexLoc]))

        similarity_score = sorted(similarity_score, key=lambda x: x[1], reverse=True)

        similarity_score = similarity_score[1:15]
        location_indices = [i[0] for i in similarity_score]
        return (df['name'].iloc[location_indices])


    rows, cols = (len(likes), 15)
    arr = [[0] * cols] * rows

    i = 0

    for like in likes:
        j = 0
        # print ("likes is : ", like)
        arr[i] = [guess(lik) for lik in like]
        i += 1

    li = []
    # df_temp = pd.DataFrame.from_records(arr)

    for user in userLike.val():
        i = 0
        print('For User : ', user)
        for name in arr:
            for n in name:
                # print ('name is :', n)
                print(i + 1, ':', n.iloc[random.randint(0, len(n) - 1)])
                db.child("Users").child(user).child("preferences").child("temp").update(
                    {str(i + 1): str(n.iloc[random.randint(0, len(n) - 1)])})
                i += 1

    Data_Clean()




while(1):
    inp=input("Press any key to run........")
    execute()