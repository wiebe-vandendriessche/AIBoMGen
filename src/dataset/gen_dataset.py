from datasets import load_dataset

dataset = load_dataset("imdb")

dataset["train"].to_csv("/imdb_dataset/train.csv", index=False)
dataset["test"].to_csv("/imdb_dataset/test.csv", index=False)

print("Dataset saved at /dataset/imdb_dataset")
