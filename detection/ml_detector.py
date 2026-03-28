import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class MLDetector:
    def __init__(self):
        self.scaler = StandardScaler()

        # 🔥 Better model
        self.model = RandomForestClassifier(n_estimators=50)

        # Training data (can replace with real later)
        X = [
            [0, 5, 50],
            [0.1, 5, 40],
            [5, 5, 30],
            [10, 5, 20],
            [0, 0, 50],
            [8, 4, 10],
            [15, 6, 5],
            [20, 6, 2]
        ]

        y = [0, 0, 1, 1, 0, 1, 1, 1]

        X = self.scaler.fit_transform(X)
        self.model.fit(X, y)

    def predict(self, diff, speed, distance):
        X = np.array([[diff, speed, distance]])
        X = self.scaler.transform(X)

        pred = self.model.predict(X)[0]
        prob = self.model.predict_proba(X)[0][1]

        return pred, prob