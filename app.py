from utils.data_loader import load_csv
from utils.analyzer import summarize_data
from services.ml_service import train_simple_model

def main():
    df = load_csv("sample.csv")
    print("Data summary:")
    print(summarize_data(df))

    print("\nTraining simple model...")
    model = train_simple_model(df)
    print("Model coefficients:", model.coef_)

if __name__ == "__main__":
    main()
