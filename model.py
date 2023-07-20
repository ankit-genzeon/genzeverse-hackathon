import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def process_text(text):
    # Tokenize the text
    tokens = word_tokenize(text)
    # Remove stop words
    tokens = [token for token in tokens if token not in stop_words]
    # Lemmatize the words (reduce them to their root form)
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    # Join the words back into a single string
    return ' '.join(tokens)

# Load the data
data_expanded = pd.read_excel("expanded_data.xlsx")

# Process the questions
data_expanded['Processed_Questions'] = data_expanded['Questions'].apply(process_text)

# Split the data into training and testing sets
X = data_expanded['Processed_Questions']
y = data_expanded['Intent']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a pipeline with a TF-IDF vectorizer and an SVM classifier
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', ngram_range=(1, 2), analyzer='word')),
    ('clf', SVC(kernel='linear'))
])

# Train the model
pipeline.fit(X_train, y_train)

# Predict the labels for the test set
y_pred = pipeline.predict(X_test)

# Evaluate the model
print(classification_report(y_test, y_pred))

# Save the model to a file
joblib.dump(pipeline, 'intent_recognition_model.pkl')

# Sample questions
questions = [
    "What is the deadline for the project?",
    "Edit my timeshet for this week",
    "how many hours have i worked this week",
    "Can I view my timesheet for this week?",
    "i want to submit my timesheet for this week"
]

# Process the sample questions
questions = [process_text(question) for question in questions]

# Predict the intents for the sample questions
predicted_intents = pipeline.predict(questions)

# Print the predicted intents
for question, intent in zip(questions, predicted_intents):
    print(f"Question: {question}")
    print(f"Predicted Intent: {intent}")
    print()
