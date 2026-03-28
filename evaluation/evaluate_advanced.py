import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import *

# =========================
# LOAD DATASET
# =========================
df = pd.read_csv("dataset.csv")

# Features
X = df[["diff", "speed", "distance", "acceleration", "jerk"]]

# Target
y = df["attack_type"]

# =========================
# TRAIN TEST SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# =========================
# TRAIN MODEL
# =========================
model = RandomForestClassifier()
model.fit(X_train, y_train)

# =========================
# PREDICT
# =========================
y_pred = model.predict(X_test)

# =========================
# METRICS
# =========================
print("\n===== MODEL EVALUATION =====")
print("Accuracy :", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred, average='weighted'))
print("Recall   :", recall_score(y_test, y_pred, average='weighted'))
print("F1 Score :", f1_score(y_test, y_pred, average='weighted'))

# =========================
# CONFUSION MATRIX
# =========================
cm = confusion_matrix(y_test, y_pred)

plt.figure()
plt.imshow(cm)
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")

for i in range(len(cm)):
    for j in range(len(cm)):
        plt.text(j, i, cm[i][j], ha='center')

plt.show()

# =========================
# GRAPH: DIFF VS LABEL
# =========================
plt.figure()
plt.scatter(df["diff"], df["attack_type"])
plt.xlabel("GPS Deviation (diff)")
plt.ylabel("Attack Type")
plt.title("Deviation vs Attack Type")
plt.show()