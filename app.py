import pandas as pd
from flask import Flask, render_template, request, Markup
import random
from datetime import datetime

app = Flask(__name__)

# Load the data
data = pd.read_csv('API_SP.DYN.LE00.IN_DS2_en_csv_v2_206.csv', skiprows=4)
latest_year = data.columns[-1]

# Function to get life expectancy
def get_life_expectancy(country, birth_year):
    country = country.lower().strip()
    # Get all column names that are just year numbers
    year_columns = [col for col in data.columns if col.isdigit()]
    # Find the closest year to the birth_year for which data is available
    closest_year = max(int(year) for year in year_columns if int(year) <= birth_year)
    
    # Now we just use the closest year as the column name, since it's already a string
    result = data[data['Country Name'].str.lower() == country]
    if not result.empty and str(closest_year) in result.columns:
        life_expectancy_at_birth = result.iloc[0][str(closest_year)]
        if pd.notnull(life_expectancy_at_birth):
            return float(life_expectancy_at_birth)
    return "data not available"

# Function to get a humorous comment
def humorous_comment(age):
    if age > 60:
        jokes = [
            "You know you're getting wiser with every year, right? At your age, you're practically a sage!",
            "Age is like fine wine; it gets better with time. You're just entering your vintage year!",
            "Remember, you're not old, you're just retro. And retro is incredibly trendy right now!",
            "You're not getting older; you're just becoming a classic. Classics are always in high demand!"
        ]
    elif 10 <= age <= 40:
        jokes = [
            "At your age, you've got all the time in the world to seize the day!",
            "They say youth is a gift of nature, but age is a work of art. You're the artist in your prime!",
            "You're at the perfect age to challenge the impossible and turn it into the incredible.",
            "Being young is a beautiful blank canvas, and you've got the whole palette to color it as you wish!"
        ]
    else:
        jokes = [
            "Ah, to be young and full of energy! Enjoy these years – they're some of the best.",
            "Not a teenager, but not quite over the hill – sounds like you're in the adventure years!",
            "The years between 40 and 60 are the 'middle youth' – or so they say. Time to make it count!"
        ]
    
    return random.choice(jokes)


@app.route('/', methods=['GET', 'POST'])
def home():
    message = ''
    user_data = {'name': '', 'age': '', 'location': ''}
    health_tips_increase = [
        "Regular exercise can improve your heart health.",
        "Eating a balanced diet with plenty of fruits and vegetables may add years to your life.",
        "Regular check-ups with a healthcare provider can catch potential issues early."
    ]

    health_tips_decrease = [
        "Smoking has been linked to a variety of health issues and can shorten your life expectancy.",
        "Excessive alcohol consumption can lead to health problems and diminish life expectancy.",
        "High-stress levels over a long period can take a toll on your health."
    ]

    if request.method == 'POST':
        user_data['name'] = request.form.get('name', '')
        user_data['age'] = request.form.get('age', '')
        user_data['location'] = request.form.get('location', '')
    
    # Make sure to convert age to an integer before using it in calculations
        try:
            age = int(user_data['age'])
            current_year = datetime.now().year
            birth_year = current_year - age
        except ValueError:
            # Handle the case where age is not a valid integer
            age = None
            message = "Please enter a valid age."

        if age is not None:
            life_expectancy_at_birth = get_life_expectancy(user_data['location'], birth_year)

            if life_expectancy_at_birth != "data not available":
                years_left = life_expectancy_at_birth - age
                minutes_left = years_left * 525600
                seconds_left = years_left * 31536000

                increase_tip = random.choice(health_tips_increase)
                decrease_tip = random.choice(health_tips_decrease)

                # Call the humorous_comment function to get a joke based on the age
                joke = humorous_comment(age)

                # Construct the message with the joke included
                message = Markup(
                    f"Hello, {user_data['name']} from {user_data['location']}. Based on our data, you have approximately {years_left:.1f} years left, "
                    f"which is about {int(minutes_left):,} minutes, or even about {int(seconds_left):,} seconds.<br><br>"
                    f"Tip to potentially increase your life expectancy: {increase_tip}<br>"
                    f"Tip that might decrease it: {decrease_tip}<br><br>"
                    f"And a little humor for your day: {joke}"
            )
            else:
                message = f"Hello, {user_data['name']}. Unfortunately, we do not have life expectancy data for {user_data['location']}."
        else:
            # If age is None, you could choose to not do the calculations and instead show an error message
            pass  # Or set message to an error message

    return render_template('index.html', message=message, user_data=user_data)

if __name__ == '__main__':
    app.run(debug=True)

