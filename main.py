import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
import requests
import pickle
import time
import threading
from sklearn.linear_model import LogisticRegression
import numpy as np

API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
WINDOW_SIZE = 3

class FatalApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.result_label = Label(text="Loading...", font_size='24sp')
        self.pred_label = Label(text="", font_size='20sp')
        self.layout.add_widget(Label(text="🔥 Fatal Wingo Predictor", font_size='28sp'))
        self.layout.add_widget(self.result_label)
        self.layout.add_widget(self.pred_label)
        Clock.schedule_interval(self.update, 15)
        self.last_numbers = []
        self.model = self.load_model()
        return self.layout

    def load_model(self):
        try:
            return pickle.load(open('wingo_model.pkl', 'rb'))
        except:
            return None

    def fetch(self):
        url = f"{API_URL}?ts={int(time.time() * 1000)}"
        resp = requests.get(url, timeout=5).json()
        latest = resp['data']['list'][0]
        num = int(latest['number'])
        size = "BIG" if num >= 5 else "SMALL"
        return num, size

    def extract(self, window):
        big_count = sum(1 for n in window if n >=5)
        diff = window[-1] - window[-2] if len(window) >1 else 0
        avg = sum(window)/len(window)
        return window + [big_count, diff, avg]

    def predict(self):
        if self.model and len(self.last_numbers) >= WINDOW_SIZE:
            feat = self.extract(self.last_numbers[-WINDOW_SIZE:])
            X = np.array(feat).reshape(1, -1)
            return "BIG" if self.model.predict(X)[0] == 1 else "SMALL"
        return ""

    def update(self, dt):
        def work():
            try:
                num, size = self.fetch()
                self.last_numbers.append(num)
                self.result_label.text = f"✅ Last Result: {size}"
                pred = self.predict()
                self.pred_label.text = f"🧠 Next Prediction: {pred}" if pred else ""
            except:
                pass

        threading.Thread(target=work).start()
