import webbrowser
import subprocess
import requests

def open_chrome():
    webbrowser.open("https://www.google.com")
    print("Chrome opened.")

def close_chrome():
    if subprocess.run(["tasklist"], capture_output=True, text=True).stdout.find("chrome.exe") != -1:
        subprocess.run(["taskkill", "/IM", "chrome.exe", "/F"])
        print("Chrome closed.")
    else:
        print("Chrome is not running.")

def check_weather():
    lat = 33.7092
    lon = -117.9540
    API_KEY = "9406cd799a8355297a79841d07a313d1"

    # Correct URL with scheme
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        first_forecast = data["list"][0]
        temp = first_forecast["main"]["temp"]
        desc = first_forecast["weather"][0]["description"]
        return f"The current temperature is {temp} degrees Celcius with {desc}."
    else:
        print(f"Could not fetch weather. Status code: {response.status_code}")
        print("Response:", response.text)




def search_google(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    print(f"Searching Google for: {query}")

# check_weather()