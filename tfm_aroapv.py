# -*- coding: utf-8 -*-
"""TFM_AroaPV.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1OxDnOMxyPYvjLNSKC5piYO1G77mYz8e5

## Inicializacion
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import SelectKBest, chi2, f_classif
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_curve, auc, roc_auc_score, ConfusionMatrixDisplay
from scipy.stats import chi2_contingency, ttest_ind, normaltest

data = pd.read_csv('/content/alzheimers_disease_data.csv')
data.head()

"""## Exploracion inicial
----
"""

data.shape

data.info()

"""### Eliminacion variables irrelevantes"""

data = data.drop(columns=['PatientID', 'DoctorInCharge'])

"""# Estadística

#### Estadisticas descriptivas
"""

data.describe().T

"""### Correlaciones"""

data.corr()

sns.set()
plt.figure(figsize=(22,10))
mask = np.triu(np.ones_like(data.corr(), dtype=bool))
sns.heatmap(data.corr(), annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, mask=mask)
plt.grid(False)
plt.title('Correlaciones')
plt.show()

"""### Inferencia

#### Variables categoricas
"""

X_cat= data[['Gender','Ethnicity','EducationLevel','Smoking','FamilyHistoryAlzheimers','CardiovascularDisease','Diabetes',
'Depression','HeadInjury','Hypertension','MemoryComplaints','BehavioralProblems','Confusion','Disorientation','PersonalityChanges',
'DifficultyCompletingTasks','Forgetfulness']]
#X=data.drop(columns=['Diagnosis'])
y_cat=data['Diagnosis']
chi_scores = chi2(X_cat, y_cat)
chi2_df = pd.DataFrame({"Feature": X_cat.columns, "Chi2": chi_scores[0], "p-valor": chi_scores[1]})
print(chi2_df.sort_values(by="Chi2", ascending=False))

"""#### Variables numericas"""

X_num = data[['Age','BMI','AlcoholConsumption','PhysicalActivity','DietQuality','SleepQuality','SystolicBP','DiastolicBP','CholesterolTotal','CholesterolLDL','CholesterolHDL','MMSE','FunctionalAssessment','ADL']]
y_num=data['Diagnosis']

t_test =[]
group_0 = X_num[y_num == 0]
group_1 = X_num[y_num == 1]

for column in X_num.columns:
    t_stat, p_val = ttest_ind(group_0[column], group_1[column], nan_policy='omit')
    t_test.append({"Feature": column, "t-stat": t_stat, "p-valor": p_val})
t_test = pd.DataFrame(t_test)
print(t_test.sort_values(by="t-stat", key=abs, ascending=False))

"""# Visualizacion"""

cat_levels = {'Gender': ['Male', 'Female'],
    'Ethnicity': ['Caucasian', 'African American', 'Asian', 'Other'],
    'EducationLevel': ['None', 'High School', 'Bachelor\'s', 'Higher'],
    'Smoking': ['No', 'Yes'],
    'FamilyHistoryAlzheimers': ['No', 'Yes'],
    'CardiovascularDisease': ['No', 'Yes'],
    'Diabetes': ['No', 'Yes'],
    'Depression': ['No', 'Yes'],
    'HeadInjury': ['No', 'Yes'],
    'Hypertension': ['No', 'Yes'],
    'MemoryComplaints': ['No', 'Yes'],
    'BehavioralProblems': ['No', 'Yes'],
    'Confusion': ['No', 'Yes'],
    'Disorientation': ['No', 'Yes'],
    'PersonalityChanges': ['No', 'Yes'],
    'DifficultyCompletingTasks': ['No', 'Yes'],
    'Forgetfulness': ['No', 'Yes']}

for column, levels in cat_levels.items():
    data[column] = data[column].map(dict(enumerate(levels)))
    data[column] = data[column].astype('category', copy=False )

data.info()

diag = data['Diagnosis'].value_counts()
plt.figure(figsize=(10, 8))
plt.pie(diag, labels=['No', 'Sí'], colors = ['palegreen', 'coral'], autopct=lambda p: f'{p:.1f}%\n({int(p * sum(diag) / 100):,})',  startangle=70, explode=[0.05, 0], shadow=True,  wedgeprops={'edgecolor': 'black'})
plt.title("Distribución del diagnóstico de la EA", fontsize=12)
plt.show()

"""### Demográficas


"""

plt.figure(figsize=(10, 6))
ax = sns.countplot(x='Gender', hue='Diagnosis', data=data, palette='Set2')
plt.title('Distribución de la variable objetivo por género')
plt.xlabel('Género')
plt.xticks([0, 1], ['Hombre', 'Mujer'], fontsize=10)
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles, ['No Alzheimer', 'Alzheimer'], title='Diagnóstico')
plt.ylabel('Frecuencia')
plt.show()

plt.figure(figsize=(10, 6))
sns.boxplot(x='Gender', y='Age', data=data, palette='hls', width=0.6)
plt.title('Distribución de la variable Edad por Género')
plt.xlabel('Género')
plt.xticks([0, 1], ['Mujer','Hombre'], fontsize=10)
plt.ylabel('Edad')
plt.show()

plt.figure(figsize=(10, 6))
sns.histplot(data['Age'], kde=True, color='skyblue', edgecolor='black', linewidth=1.5)
plt.title('Distribución de la variable Edad')
mean = data['Age'].mean()
plt.axvline(mean, color='orange', linestyle='--', linewidth=2, label=f'Edad media: {mean:.1f}')
plt.legend()
plt.xlabel('Edad')
plt.ylabel('Frecuencia')
plt.show()

plt.figure(figsize=(10, 6))  # Adjust the size of the figure
sns.boxplot(x='Diagnosis', y='Age', data=data, palette='Paired', width=0.6)
plt.title('Distribución de la variable edad por diagnóstico')
plt.xlabel(' (0: No Alzheimer, 1: Alzheimer)', fontsize=12)
plt.ylabel('Edad')
plt.show()

plt.figure(figsize=(10, 6))
ax = sns.countplot(x='Ethnicity', hue='Diagnosis', data=data, palette='Paired')
plt.title('Distribución de la variable objetivo según la etnia')
plt.xlabel('Etnia')
plt.xticks([0, 1, 2, 3], ['Afroamericano','Asiático','Caucásico','Otro'], fontsize=10)
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles, ['No Alzheimer', 'Alzheimer'], title='Diagnóstico')
plt.ylabel('Frecuencia')

plt.figure(figsize=(10, 6))
ax = sns.countplot(x='EducationLevel', hue='Diagnosis', data=data, palette='Accent')
plt.title('Distribución de la variable objetivo según el nivel educativo')
plt.xlabel('Nivel educativo')
plt.xticks([0, 1, 2, 3], ['Bachillerato','Educación secundaria', 'Superior','Ninguno'], fontsize=10)
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles, ['No Alzheimer', 'Alzheimer'], title='Diagnóstico')
plt.ylabel('Frecuencia')

plt.figure(figsize=(10, 6))
sns.boxplot(x='EducationLevel', y='Age', data=data, palette='Paired', width=0.6)
plt.title('Distribución de la variable edad por nivel educativo')
plt.xlabel('Nivel educativo')
plt.xticks([0, 1, 2, 3], ['Bachillerato','Educación secundaria', 'Superior','Ninguno'], fontsize=10)
plt.ylabel('Age')
plt.show()

"""### Factores de estilo de vida"""

plt.figure(figsize=(10, 6))
sns.histplot(data['BMI'], kde=True, color='coral', edgecolor='black', linewidth=1.5)
plt.title('Distribución de la variable índice de masa corporal')
mean = data['BMI'].mean()
plt.axvline(mean, color='orange', linestyle='--', linewidth=2, label=f'IMC media: {mean:.1f}')
plt.legend()
plt.xlabel('BMI')
plt.show()

plt.figure(figsize=(10, 6))
sns.boxplot(x='Diagnosis', y='BMI', data=data, palette='Paired', width=0.6)
plt.title('Distribución del IMC según el diagnóstico')
plt.xlabel(' Diagnóstico (0: No Alzheimer, 1: Alzheimer)', fontsize=12)
plt.ylabel('IMC')
plt.show()

plt.figure(figsize=(10, 6))
ax = sns.countplot(x='Smoking', hue='Diagnosis', data=data, palette='Accent')
plt.title('Distribución de la variable objetivo según si fuma')
plt.xlabel('Fumador')
plt.xticks([0, 1], ['No', 'Sí'], fontsize=10)
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles, ['No Alzheimer', 'Alzheimer'], title='Diagnóstico')
plt.ylabel('Frecuencia')

plt.figure(figsize=(10, 6))
sns.boxplot(x='Diagnosis', y='AlcoholConsumption', data=data, palette='Paired', width=0.6)
plt.title('Distribución de la consumición de alcohol según el diagnóstico')
plt.xlabel(' Diagnóstico (0: No Alzheimer, 1: Alzheimer)', fontsize=12)
plt.ylabel('Consumición media semanal')
plt.show()

plt.figure(figsize=(12, 8))
sns.scatterplot(x='BMI', y='PhysicalActivity', hue='Diagnosis', data=data, palette='Set2', s=120, edgecolor='black', alpha=0.8)
plt.title('Distribución del IMC vs. Actividad física según diagnóstico', fontsize=12)
plt.xlabel('IMC')
plt.ylabel('Actividad física (horas/semana)', fontsize=10)
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles, ['No Alzheimer', 'Alzheimer'], title='Diagnóstico', loc='center left', bbox_to_anchor=(1, 0.5))
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()

plt.figure(figsize=(10, 6))
sns.boxplot(x='Diagnosis', y='SleepQuality', data=data, palette='Accent', width=0.6)
plt.title('Calidad del sueño según el diagnóstico')
plt.xlabel(' Diagnóstico (0: No Alzheimer, 1: Alzheimer)', fontsize=12)
plt.ylabel('Calidad del sueño')
plt.show()

"""### Historial medico"""

plt.figure(figsize=(10, 6))
ax = sns.countplot(x='FamilyHistoryAlzheimers', hue='Diagnosis', data=data, palette='Paired')
plt.title('Distribución de la variable objetivo según historial familiar')
plt.xlabel('Historial familiar')
plt.xticks([0, 1], ['No', 'Sí'], fontsize=10)
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles, ['No Alzheimer', 'Alzheimer'], title='Diagnóstico')
plt.ylabel('Frecuencia')

var_hm= ['CardiovascularDisease', 'Depression', 'Diabetes','HeadInjury','Hypertension']
for var in var_hm:
  plt.figure(figsize=(10, 6))
  ax = sns.countplot(x=var, hue='Diagnosis', data=data, palette='Accent')
  plt.title(f'Distribución de la variable objetivo según si tiene {var}')
  plt.xlabel(var)
  plt.xticks([0, 1], ['No', 'Sí'], fontsize=10)
  handles, labels = plt.gca().get_legend_handles_labels()
  plt.legend(handles, ['No Alzheimer', 'Alzheimer'], title='Diagnóstico')
  plt.ylabel('Frecuencia')

"""### Mediciones clinicas"""

var_mc = ['SystolicBP', 'DiastolicBP', 'CholesterolTotal','CholesterolLDL', 'CholesterolHDL', 'CholesterolTriglycerides']
for var in var_mc:
    plt.figure(figsize=(10, 6))
    sns.histplot(data=data, x=var, hue='Diagnosis', kde=True, element='step',  stat='density', common_norm=False, palette='hls', linewidth=2)
    plt.title(f'Distribución de {var} según diagnóstico', fontsize=12)
    plt.xlabel(var)
    plt.ylabel('Densidad')
    plt.grid(False)
    plt.show()

"""### Evaluaciones cognitivas y funcionales"""

var_ev=['MMSE','FunctionalAssessment','ADL']
for var in var_ev:
  plt.figure(figsize=(10, 6))
  sns.histplot(data = data, x=var, kde=True, color='greenyellow', edgecolor='black', linewidth=1.5)
  plt.title(f'Distribución de la variable {var}')
  mean = data[var].mean()
  plt.axvline(mean, color='orange', linestyle='--', linewidth=2, label=f'Puntuacion media: {mean:.1f}')
  plt.legend()
  plt.xlabel(var)
  plt.show()

for var in var_ev:
  plt.figure(figsize=(10, 6))
  sns.boxplot(x='Diagnosis', y=var, data=data, palette='Accent', width=0.6)
  plt.title(f'Distribución de la variable {var} por diagnóstico')
  plt.xlabel(' (0: No Alzheimer, 1: Alzheimer)', fontsize=12)
  plt.ylabel(var)
  plt.show()

plt.figure(figsize=(12, 8))
sns.scatterplot(x='FunctionalAssessment', y='ADL', hue='Diagnosis', data=data, palette='Set2', s=120, edgecolor='black', alpha=0.8)
plt.title('Distribución de la habilidad funcional vs. Actividades de la vida diaria según diagnóstico', fontsize=12)
plt.xlabel('Habilidad funcional ')
plt.ylabel('Actividades de la vida diaria', fontsize=10)
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles, ['No Alzheimer', 'Alzheimer'], title='Diagnóstico', loc='center left', bbox_to_anchor=(1, 0.5))
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()

"""### Sintomas"""

var_sin= ['Confusion', 'Disorientation', 'PersonalityChanges','DifficultyCompletingTasks','Forgetfulness']
for var in var_sin:
  plt.figure(figsize=(10, 6))
  ax = sns.countplot(x=var, hue='Diagnosis', data=data, palette='Dark2')
  plt.title(f'Distribución de la variable objetivo según si tiene {var}')
  plt.xlabel(var)
  plt.xticks([0, 1], ['No', 'Sí'], fontsize=10)
  handles, labels = plt.gca().get_legend_handles_labels()
  plt.legend(handles, ['No Alzheimer', 'Alzheimer'], title='Diagnóstico')
  plt.ylabel('Frecuencia')

"""# Prepocesamiento

## Valores nulos
"""

pd.isnull(data).sum()

(data.isnull().sum()).plot.bar()
plt.title('Valores nulos por variable')
plt.xlabel('Variable')
plt.ylabel('Número de valores nulos')
plt.show()

"""##Outliers"""

for variable in data.select_dtypes(include='number').columns:
    q1 = data[variable].quantile(0.25)
    q3 = data[variable].quantile(0.75)
    IQR = q3 - q1
    lower = q1 - 1.5 * IQR
    upper = q3 + 1.5 * IQR

    outliers = ((data[variable] < lower) | (data[variable] > upper)).sum()

    print(f"{variable}: {outliers} outliers")

data.head()

"""## Estandarizacion"""

num = data.select_dtypes(exclude=['category']).columns.tolist()
num.remove('Diagnosis')
scaler = StandardScaler()
data[num] = scaler.fit_transform(data[num])

"""## Transformacion de variables categoricas"""

cat = data.select_dtypes(include=['category']).columns.tolist()
data = pd.get_dummies(data, columns=cat, drop_first=True, dtype = float)

data.head()

"""## Seleccion de caracteristicas

#### ANOVA
"""

best = SelectKBest(f_classif, k=15)
X_selected = best.fit_transform(X, y)
selected_features = list(X.columns[best.get_support()])
print("Características Seleccionadas:", selected_features)

"""#### ACP"""

pca = PCA()
X_pca = pca.fit_transform(X)

explained_variance = pca.explained_variance_ratio_
cumulative_variance = np.cumsum(explained_variance)

plt.figure(figsize=(10, 6))
plt.plot(range(1, len(cumulative_variance) + 1), cumulative_variance, marker='o', linestyle='-', color='r', label='Varianza acumulada')
plt.xlabel('Número de componentes principales')
plt.ylabel('Varianza explicada acumulada')
plt.title('Gráfico de codo: varianza explicada acumulada')
plt.axhline(y=0.85, color='g', linestyle='--', label='85% de varianza explicada')
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(10, 6))
plt.bar(range(1, len(explained_variance) + 1), explained_variance, alpha=0.6, color='b')
plt.xlabel('Componentes principales')
plt.ylabel('Porcentaje de varianza explicada')
plt.title('Varianza explicada por cada componente principal')
plt.show()

pca = PCA(n_components=17)  # numero de componentes principales seleccionadas
X_pca = pca.fit_transform(X)
explained_variance = pca.explained_variance_ratio_
print("Varianza explicada por cada componente principal:", explained_variance)
print("Varianza explicada total:", sum(explained_variance))

print("\nComparacion de caracteristicas seleccionadas:")
print("ANOVA:", selected_features)
print("PCA:", [f"PC{i+1}" for i in range(len(explained_variance))])

selected_features.extend(['Age', 'Gender_Male'])

"""##Division conjunto test y entrenamiento"""

X = data.drop("Diagnosis", axis=1)
y = data["Diagnosis"]
X_train, X_test, y_train, y_test = train_test_split(X[selected_features], y, test_size=0.35, random_state=42, shuffle = True)

print(f"X Train :{X_train.shape}")
print(f"X Test :{X_test.shape}")
print(f"y Train :{y_train.shape}")
print(f"y Test :{y_test.shape}")

"""# Machine Learning

## Regresion logistica
"""

model_log = LogisticRegression()

# Hiperparámetros para optimizar el modelo
param_grid_rl = {
    'C': [0.01, 0.1, 1, 10, 100],
    'penalty': ['l1', 'l2'],
    'solver': ['liblinear', 'saga']
}

#Búsqueda del mejor hiperparámetro
grid_search_rl = GridSearchCV(estimator=model_log,
                              param_grid=param_grid_rl,
                              cv=5,
                              scoring='accuracy')
# Entrenamiento del modelo con los datos de entrenamiento
grid_search_rl.fit(X_train, y_train)

best_rl = grid_search_rl.best_estimator_
print("Mejores hiperparámetros encontrados con búsqueda en grid:", best_rl)

# Construcción del modelo con los mejores hiperparametros
rl_pred = best_rl.predict(X_test)
print(classification_report(y_test, rl_pred))

# Matriz de confusion
ConfusionMatrixDisplay.from_estimator(best_rl, X_test, y_test)

"""## Random Forest"""

# Modelo
rf_model= RandomForestClassifier()
estimators = 50
random_f = RandomForestClassifier(n_estimators=estimators, random_state=42)

# Hiperparametros para optimizar el modelo
param_grid_rf = {
    'n_estimators': [1, 50, 100, 200],
    'max_depth': [10, 20, 30, 50],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

#Busqueda del mejor hiperparametro
grid_search_rf = GridSearchCV(estimator=random_f,
                           param_grid=param_grid_rf,
                           scoring='accuracy',
                           cv=3)
# Entrenamiento del modelo con los datos de entrenamiento
grid_search_rf.fit(X_train, y_train)

best_rf = grid_search_rf.best_estimator_
print("Mejores hiperparámetros encontrados con búsqueda en grid:", best_rf)

# Construccion del modelo con los mejores hiperparametros
rf_pred = best_rf.predict(X_test)
print(classification_report(y_test, rf_pred))

# Matriz de confusion
ConfusionMatrixDisplay.from_estimator(best_rf, X_test, y_test)

print("Exactitud: ", accuracy_score(y_test,rf_pred))

"""## Support Vector Machine"""

svm_model = SVC (probability=True)

param_grid_svm = {
    'C': [0.1, 1, 10, 100],
    'kernel': ['linear', 'rbf', 'poly'],
    'gamma': ['scale', 'auto']
}

# Búsqueda del mejor hiperparámetro
grid_search_svm = GridSearchCV(estimator=svm_model,
                           param_grid=param_grid_svm,
                           scoring='accuracy',
                           cv=3)

# Entrenamiento del modelo con los datos de entrenamiento
grid_search_svm.fit(X_train, y_train)

best_svm = grid_search_svm.best_estimator_
print("Mejores hiperparámetros encontrados con búsqueda en grid:", best_svm)
print("Kernel seleccionado:", best_svm.kernel)

svm_pred = best_svm.predict(X_test)
print(classification_report(y_test, svm_pred))

# Matriz de confusión
ConfusionMatrixDisplay.from_estimator(best_svm, X_test, y_test)

print("Exactitud: ", accuracy_score(y_test,svm_pred))

"""## Variables relevantes en cada modelo"""

modelos = [
    ("LogisticRegression", best_rl),
    ("RandomForestClassifier", best_rf),
    ("SVC", best_svm)
]


for nombre, modelo in modelos:
  if hasattr(modelo, 'feature_importances_'):
    feature_importances = modelo.feature_importances_
    importance_type = 'Feature Importances'

  elif hasattr(modelo, 'coef_'):
    feature_importances = abs(modelo.coef_[0])
    importance_type = 'Coefficient Magnitude'

  else:
    print(f"{nombre} no tiene importancia de características.")
    continue

  feature_importances_df = pd.DataFrame({
      'Feature': X_train.columns,
      'Importance': feature_importances
  })

  feature_importances_df = feature_importances_df.sort_values(by='Importance', ascending=False)

  plt.figure(figsize=(10, 6))
  sns.barplot(x='Importance', y='Feature', data=feature_importances_df[:20], palette='Set2')
  plt.title(f"Top 20 variables importantes - {nombre} ({importance_type})")
  plt.xlabel('Importancia')
  plt.ylabel('Variable')
  plt.grid(False)
  plt.show()

"""# Evaluacion"""

def metricas(modelo, X_test, y_test):
    # Predicciones del modelo
    y_pred = modelo.predict(X_test)


    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)


    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()


    sensibilidad = tp / (tp + fn)
    especificidad = tn / (tn + fp)


    y_pred_prob = modelo.predict_proba(X_test)[:, 1]
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_prob)
    auc_score = auc(fpr, tpr)


    print(f'Métricas del modelo: {modelo}')
    print(f'Exactitud: {accuracy:.2f}')
    print(f'Precisión: {precision:.2f}')
    print(f'Recall: {recall:.2f}')
    print(f'F1-Score: {f1:.2f}')
    print(f'Sensibilidad: {sensibilidad:.2f}')
    print(f'Especificidad: {especificidad:.2f}')
    print(f'AUC: {auc_score:.2f}')
    print()


    plt.plot(fpr, tpr, label=f'Modelo (AUC = {auc_score:.2f})')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('Tasa de Falsos Positivos (FPR)')
    plt.ylabel('Tasa de Verdaderos Positivos (TPR)')
    plt.title(f'Curva ROC {modelo}')
    plt.legend(loc='lower right')
    plt.show()

#Regresion logistica
metricas(best_rl, X_test, y_test)

#Random forest
metricas(best_rf, X_test, y_test)

# SVM
metricas(best_svm, X_test, y_test)