import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix

def main():

    data = random_df()

    X = data.drop('Win', axis=1)
    y = data['Win']

    # Normalize the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # Initialize and train the logistic regression model
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Make prediction
    y_pred = model.predict(X_test)

    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)

    print('Accuracy:', accuracy)
    print(f'Confusion matrix:\n{conf_matrix[0]}\n{conf_matrix[1]}')

    
# Generate a DataFrame with random NBA statistics.
def random_df():
    num_rows = 1000

    # Random NBA stats
    points = np.random.randint(80, 150, num_rows)  # Points scored
    field_goal_pct = np.random.uniform(40, 60, num_rows)  # Field goal percentage
    three_point_pct = np.random.uniform(25, 50, num_rows)  # Three-point percentage
    free_throw_pct = np.random.uniform(70, 90, num_rows)  # Free throw percentage
    rebounds = np.random.randint(20, 60, num_rows)  # Number of rebounds
    assists = np.random.randint(15, 40, num_rows)  # Number of assists
    turnovers = np.random.randint(5, 20, num_rows)  # Number of turnovers
    steals = np.random.randint(5, 15, num_rows)  # Number of steals
    blocks = np.random.randint(2, 10, num_rows)  # Number of blocks

    # Random binary 'Win' column (1 for win, 0 for loss)
    win = np.random.randint(0, 2, num_rows)

    # Creating the DataFrame
    df = pd.DataFrame({
        'Points': points,
        'FieldGoal%': field_goal_pct,
        'ThreePoint%': three_point_pct,
        'FreeThrow%': free_throw_pct,
        'Rebounds': rebounds,
        'Assists': assists,
        'Turnovers': turnovers,
        'Steals': steals,
        'Blocks': blocks,
        'Win': win
    })

    return df

if __name__ == '__main__':
    main()

