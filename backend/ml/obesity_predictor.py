
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
import os
import sklearn
from sklearn.model_selection import train_test_split

from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import SGDClassifier

from joblib import dump, load
import json
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report

def preprocess_data():
    df = pd.read_csv('./ObesityDataSet_raw.csv')
    df.columns = ['Gender', 'Age', 'Height', 'Weight', 'Family History with Overweight',
       'Frequent consumption of high caloric food', 'Frequency of consumption of vegetables', 'Number of main meals', 'Consumption of food between meals', 'Smoke', 'Consumption of water daily', 'Calories consumption monitoring', 'Physical activity frequency', 'Time using technology devices',
       'Consumption of alcohol', 'Transportation used', 'Obesity']
    df['Obesity'] = df['Obesity'].apply(lambda x: x.replace('_', ' '))
    df['Transportation used'] = df['Transportation used'].apply(lambda x: x.replace('_', ' '))
    df['Height'] = df['Height']*100
    df['Height'] = df['Height'].round(1)
    df['Weight'] = df['Weight'].round(1)
    df['Age'] = df['Age'].round(1)

    df_copy = df.copy()

    mapping0 = {1:'Never', 2:'Sometimes', 3:'Always'}
    mapping1 = {1: '1', 2:'2' , 3: '3', 4: '3+'}
    mapping2 = {1: 'Less than a liter', 2:'Between 1 and 2 L', 3:'More than 2 L'}
    mapping3 = {0: 'I do not have', 1: '1 or 2 days', 2: '2 or 4 days', 3: '4 or 5 days'}
    mapping4 = {0: '0–2 hours', 1: '3–5 hours', 2: 'More than 5 hours'}

    df['Frequency of consumption of vegetables'] = df['Frequency of consumption of vegetables'].replace(mapping0)
    df['Number of main meals'] = df['Number of main meals'].replace(mapping1)
    df['Consumption of water daily'] = df['Consumption of water daily'].replace(mapping2)
    df['Physical activity frequency'] = df['Physical activity frequency'].replace(mapping3)
    df['Time using technology devices'] = df['Time using technology devices'].replace(mapping4)

    return df, df_copy

def prepare_datasets():
    df_processed = pd.read_csv('Obesity_dataset_processed.csv')
    df_original = pd.read_csv('ObesityDataset_raw.csv')

    return df_processed, df_original


def prepare_training_data(df_processed, df_copy):
    x = df_copy[df_copy.columns[:-1]]
    y = df_processed['Obesity']

    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(x, y, test_size=0.1)

    le = LabelEncoder()
    y_train = le.fit_transform(y_train)
    y_train

    Scale_features = ['Age', 'Height', 'Weight']
    Scale_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('Scaling', StandardScaler())
    ])

    Ordi_features = ['Consumption of food between meals', 'Consumption of alcohol']
    Ordi_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('Ordi', OrdinalEncoder())
    ])

    NonO_features = ['Gender', 'Family History with Overweight', 'Frequent consumption of high caloric food', 'Smoke', 'Calories consumption monitoring', 'Transportation used']
    NonO_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('Non-O', OneHotEncoder())
    ])

    Preprocessor = ColumnTransformer(transformers=[
        ('Scale', Scale_transformer, Scale_features),
        ('Ordinal', Ordi_transformer, Ordi_features),
        ('Non-Ordinal', NonO_transformer, NonO_features)
    ], remainder = 'passthrough')
        
    clf = Pipeline(steps=[('preprocessor', Preprocessor)])

    clf.fit(x_train, y_train)

    ohe_cols = clf.named_steps['preprocessor'].transformers_[2][1].named_steps['Non-O'].get_feature_names_out(NonO_features)
    ohe_cols = [x for x in ohe_cols]

    le = LabelEncoder()
    y_test = le.fit_transform(y_test)
    le_name_mapping = dict(zip(le.transform(le.classes_), le.classes_))


    classifiers = [
    KNeighborsClassifier(n_neighbors = 5),
    SVC(kernel="rbf", C=0.025, probability=True),
    DecisionTreeClassifier(),
    RandomForestClassifier(),
    AdaBoostClassifier(),
    GradientBoostingClassifier(),
    SGDClassifier()
    ]

    top_class = []

    max_accuracy = 0
    best_classifier = None
    for classifier in classifiers:
        pipe = Pipeline(steps=[('preprocessor', Preprocessor),
                        ('classifier', classifier)])
        
        # training model
        pipe.fit(x_train, y_train)   
        
        acc_score = pipe.score(x_test, y_test)
        
        # using the model to predict
        y_pred = pipe.predict(x_test)
        
        #target_names = [le_name_mapping[x] for x in le_name_mapping]
        target_names = [str(le_name_mapping[x]) for x in le_name_mapping]
    #print(classification_report(y_test, y_pred, target_names=target_names))
        if max_accuracy < acc_score:
            best_classifier = pipe
            max_accuracy = acc_score
        if acc_score > 0.8:
            top_class.append(classifier)
    
    return best_classifier, le_name_mapping

    
def run_obesity_prediction():
    if not os.path.exists('model_file.joblib'): 
        df_processed, df_original = preprocess_data()

        classifier, class_mapping = prepare_training_data(df_processed, df_original)
        # Assuming dict_with_int_keys is your dictionary with integer keys
        class_mapping_str = {str(key): value for key, value in class_mapping.items()}

        with open("class_labels.json", "w") as outfile: 
            json.dump(class_mapping_str, outfile)
        
        dump(classifier, 'model_file.joblib')

    else:
        print("Model is already present. Quitting...")
        
def test_functionality(model_name = 'model_file.joblib'):
            pipeline_loaded = load('model_file.joblib')
            labels_from_file = {}
            with open("class_labels.json", "r") as infile: 
                labels_from_file = json.load(infile)


            labels_processed = {int(key): value for key, value in labels_from_file.items()}
            # predict class for data just passed
            x_train = pd.read_csv('x_train.csv')
            y_prediction = pipeline_loaded.predict(x_train.iloc[[0]])[0]
            print("Prediction happens here, ", labels_processed[y_prediction])
            
if __name__ == '__main__':
    run_obesity_prediction()