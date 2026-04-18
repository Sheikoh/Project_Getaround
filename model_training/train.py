#---- IMPORT LIBRAIRIES ----

import mlflow
from mlflow.models.signature import infer_signature
from mlflow import MlflowClient

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, root_mean_squared_error

from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

#---- VARIABLES ----
target = 'rental_price_per_day'

# Variables training
os.environ["MLFLOW_TRACKING_URI"] = "https://sheyko-mlflow-server-ft34.hf.space/"
EXPERIMENT_NAME = "GetAround"
model_name = "linear_regression_model"
test_size = 0.25
registered_model_name = "Greedy_model"
alias = "challenger"

#---- Data Collection ----
dataset = pd.read_csv(r"data\get_around_pricing_project.csv", index_col=0)

print("Data collected")

#---- DATA CLEANING ----

df = dataset.copy()
#print(f'df shape: {df.shape}')
dataset.loc[:, dataset.dtypes.eq('bool')] = dataset.loc[:, dataset.dtypes.eq('bool')].astype('int64')
num_col = dataset.select_dtypes(exclude="object").columns
obj_col = dataset.select_dtypes(include="object").columns
# obj_col
# for col in obj_col:
#     value_set = list(set(dataset[col]))
#     trad_dic = {}
#     for i in range(len(value_set)):
#         trad_dic[value_set[i]] = i

#     dataset[col]  = dataset[col].map(trad_dic)



print("Data cleaned")
print(f'Dataset shape : {dataset.shape}')

#------------------------------------------------------
#---------------------- TRAINING ----------------------
#------------------------------------------------------

print("Training in progress....")

# Features and target definition
X = dataset.drop(target, axis=1)
y = dataset[target]

num_col = X.select_dtypes(exclude="object").columns
obj_col = X.select_dtypes(include="object").columns

x_train, x_test, y_train, y_test = train_test_split(
    X, y, test_size=test_size, random_state=24
)

input_example = x_train.iloc[:3]

# MLflow config
mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
mlflow.set_experiment(EXPERIMENT_NAME)

experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)

# Pipeline (Scaler + Model)
# pas de ColumnTransformer car seulement des colonnes numériques
coltran = ColumnTransformer([
    ("scaler", StandardScaler(), num_col),
    ("ohe", OneHotEncoder(), obj_col)
]

)
pipeline = Pipeline(
    steps=[
        ("coltran", coltran),
        ("model", LinearRegression())
    ]
)

run_description = (
    f"Target: {target}\n"
    "Estimator: Linear Regression\n"
    "StandardScaler and OneHotEncoder + LinearRegression\n"
    "Base run with all data"
)

# MLflow run
with mlflow.start_run(experiment_id=experiment.experiment_id, description=run_description):
    # Train
    pipeline.fit(x_train, y_train)

    # Predict
    y_pred = pipeline.predict(x_test)

    # Metrics
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    n = len(y_test)
    p = x_test.shape[1]
    adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1)

    # MLflow signature
    signature = infer_signature(x_train, pipeline.predict(x_train))

    # Log metrics
    mlflow.log_metrics({
        "MAE": mae,
        "MSE": mse,
        "RMSE": rmse,
        "R2": r2,
        "Adjusted_R2": adj_r2
    })

    # Log params
    mlflow.log_param("scaler", "StandardScaler")
    mlflow.log_param("model", "LinearRegression")
    mlflow.log_param("test_size", test_size)


    # Log model
    mlflow.sklearn.log_model(
        pipeline,
        name=model_name,
        registered_model_name = registered_model_name,
        input_example=input_example,
        signature=signature,
        # code_paths=["func_feat_eng.py", "Model_func.py"]
    )

#--- Set registered model alias
client = MlflowClient()

model = client.get_registered_model(registered_model_name)
latest_version = model.latest_versions[-1].version

client.set_registered_model_alias(registered_model_name, alias, latest_version)
print(f"Attribution de l'alias '{alias}' à la version {latest_version} du model {registered_model_name}")
print("End of model training")