import joblib
import os


MODEL_PATH = os.path.join(
    os.getcwd(),
    "models",
    "sales_prediction_model.pkl"
)


model = joblib.load(MODEL_PATH)


def predict_sales(input_data):

    prediction = model.predict([input_data])

    return prediction[0]