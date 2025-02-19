import pandas as pd
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split

# Read CSV and explicitly define column names
df = pd.read_csv("combined_job_postings_cleaned.csv", header=None, names=["job_title", "job_description", "fraudulent_bool"])

# Combine text fields
df["text"] = df["job_title"].astype(str) + " " + df["job_description"].astype(str)

# Map 'fraudulent_bool' values properly
mapping = {"f": 0, "t": 1, "1": 1}
df["fraudulent_bool"] = df["fraudulent_bool"].astype(str).map(mapping)

# Drop rows with NaN labels
df = df.dropna(subset=["fraudulent_bool"])

# Ensure labels are numeric
df["fraudulent_bool"] = df["fraudulent_bool"].astype(int)

# Check the updated labels
print("Unique labels after fixing:", df["fraudulent_bool"].unique())

# Tokenization & Padding
max_features = 10000
max_len = 200

tokenizer = Tokenizer(num_words=max_features, lower=True, oov_token="<OOV>")
tokenizer.fit_on_texts(df["text"].values)
sequences = tokenizer.texts_to_sequences(df["text"].values)

X = pad_sequences(sequences, maxlen=max_len, padding='post')
y = df["fraudulent_bool"].values

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model Definition (Fixing `input_dim` issue)
embedding_dim = 100
model = Sequential([
    Embedding(input_dim=max_features, output_dim=embedding_dim, input_length=max_len),  # Ensure `input_length`
    Dropout(0.2),
    LSTM(64, dropout=0.2, recurrent_dropout=0.2),
    Dropout(0.2),
    Dense(1, activation='sigmoid')  # Binary classification
])

# Compile Model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Print Model Summary
model.summary()

# Train Model
history = model.fit(X_train, y_train, epochs=10, batch_size=128, validation_data=(X_test, y_test))

# Evaluate Model
test_loss, test_accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {test_accuracy:.4f}")
import pickle

with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)

model.save("fraud_detection_model.h5")

