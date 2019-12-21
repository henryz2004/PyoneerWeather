import colorsys
import glob
import math
import os
import requests
import time
from datetime import datetime

import pygame

from pyoneer3.graphics import Image
from pyoneer3.graphics import Scene
from pyoneer3.graphics import Screen
from pyoneer3.graphics import ScrollingFrame
from pyoneer3.graphics import Text
from pyoneer3.graphics import UIElement


class Weather:

    @staticmethod
    def make_api_request(current=True, future=True):

        api_key = "b7c14b432889587727611d2f146b56ae"
        city_id = 4951591  # Southborough, US

        # Forecasts will include weather, temp, pressure, humidity, highs and lows
        forecast = []

        if current:

            current_fc = requests.get("http://api.openweathermap.org/data/2.5/weather?id={}&units=imperial&APPID={}".format(city_id,api_key)).json()
            forecast.append(
                Weather(
                    "Now",
                    current_fc["dt"],
                    current_fc["weather"][0],
                    current_fc["main"]["temp"],
                    current_fc["main"]["temp_min"],
                    current_fc["main"]["temp_max"],
                    current_fc["main"]["pressure"],
                    current_fc["main"]["humidity"]
                )
            )

        if future:

            future_fc = requests.get("http://api.openweathermap.org/data/2.5/forecast?id={}&units=imperial&APPID={}".format(city_id,api_key)).json()

            for fc in future_fc["list"]:
                forecast.append(
                    Weather(
                        time.strftime("%m/%d\n%I:00 %p", time.localtime(fc["dt"])),
                        fc["dt"],
                        fc["weather"][0],
                        fc["main"]["temp"],
                        fc["main"]["temp_min"],
                        fc["main"]["temp_max"],
                        fc["main"]["pressure"],
                        fc["main"]["humidity"]
                    )
                )

        return forecast

    def __init__(self, time, unix, weather, temp, low, high, pressure, humidity):

        self.time = time
        self.unix_time = unix
        self.id = weather["id"]
        self.main = weather["main"]
        self.desc = weather["description"]
        self.icon = weather["icon"]

        self.temp = temp
        self.low = low
        self.high = high
        self.pressure = pressure
        self.humidity = humidity

    def create_weather_widget(self) -> UIElement:

        frame = UIElement(
            (0, 0, 0, 0),
            pygame.Surface((290, 90))
        )
        frame.name = "WWidget"
        frame.surf.fill((255, 255, 255))
        frame.bind_mbd(show_more_info(self))

        desc_text = Text(
            (0, 190, 0, 0),
            (100, 90),
            self.desc.title().replace(' ', '\n'),
            (255, 255, 255),
            pygame.font.Font(None, 22),
            True,
            (50, 50, 50),
        )
        desc_text.name = "WWidget_main"
        desc_text.set_parent(frame)

        weather_icon = Image(
            (0, 125, 0, 10),
            weather_icons[self.icon],
        )
        weather_icon.set_parent(frame)
        weather_icon.surf = pygame.transform.smoothscale(weather_icon.surf, (70, 70))

        time_text = Text(
            (0, 0, 0, 0),
            (100, 90),
            self.time,
            (255, 255, 255),
            pygame.font.Font(None, 22),
            True,
            (50, 50, 50)
        )
        time_text.set_parent(frame)

        time_band = UIElement(
            (0, 100, 0, 0),
            pygame.Surface((15, 90)),
        )
        time_band.name = "WWidget_time_band"
        time_band.set_parent(frame)
        lerped = color_lerp(
            (228, 100, 11),
            (211, 69, 100),
            gradient_b_o(datetime.fromtimestamp(self.unix_time).hour)
        )
        time_band.surf.fill(
            [v * 255 for v in colorsys.hsv_to_rgb(
                lerped[0]/360,
                lerped[1]/100,
                lerped[2]/100
            )]
        )

        return frame

def update_weather_widgets():
    global weather_widgets

    for widget in weather_widgets:
        widget.unparent()

    weather_widgets = []

    weather = Weather.make_api_request()

    for i, w in enumerate(weather):

        widget = w.create_weather_widget()
        widget.set_parent(main_frame)
        widget.rel_pos = (0, 5, 0, 5 + i * 100)
        widget.update()

        for c in widget.get_descendants():
            c.update()

        weather_widgets.append(widget)

    # Update last updated text as well
    last_updated.text = time.strftime("Last updated:\n%I:%M %p", time.localtime(int(time.time())))
    last_updated.draw_text()
    last_updated.update()

def show_more_info(weather):

    def handler(uie, event):

        temp = weather.temp
        low = weather.low
        high = weather.high
        pressure = weather.pressure
        humidity = weather.humidity

        main_scene.active = False
        card_scene.active = True

    return handler

def gradient_b_o(hour):
    return (math.sin(math.pi/4*(hour/3-2))+1)/2

def color_lerp(start, end, step):
    res = []
    for s, e in zip(start, end):
        res.append(int(s+(e-s)*step))
    return res

if __name__ == "__main__":

    pygame.init()

    CLOCK = pygame.time.Clock()
    FPS_CAP = 90

    s = pygame.display.set_mode((310, 640))
    screen = Screen(s)

    main_scene = Scene(screen, active=True)
    card_scene = Scene(screen, active=False)

    # Main scene UI
    main_frame = ScrollingFrame(
        (0, 0, 0, 40),
        (310, 40 * 100 + 5),
        (1, 0, 1, -40),
        (150, 150, 150)
    )
    main_frame.set_parent(main_scene)
    main_frame.scroll_speed = 100
    main_frame.update()

    last_updated = Text(
        (0, 0, 0, 0),
        (310, 50),
        "Last updated:",
        (225, 225, 225),
        pygame.font.Font(None, 20),
        True,
        (75, 75, 75)
    )
    last_updated.set_parent(main_scene)
    last_updated.update()

    # Card scene UI
    card_frame = UIElement(
        (0, 10, 0, 10),
        pygame.Surface((290, 620)),
    )
    card_frame.set_parent(card_scene)
    card_frame.surf.fill((255, 255, 255))
    card_frame.update()

    back_btn = UIElement(
        (0, 0, 0, 0),
        pygame.Surface((60, 35)),
    )
    back_btn.set_parent(card_frame)
    back_btn.surf.fill((205, 210, 220))
    back_btn.update()

    back_icon = Image(
        (0, 0, 0, 0),
        "rsrc/back_btn.png",
    )
    back_icon.set_parent(back_btn)
    back_icon.surf = pygame.transform.smoothscale(back_icon.surf, (30, 30))
    back_icon.update()
    back_icon.center_position((0.5, 0, 0.5, 0))
    back_icon.update_rect()

    card_title = Text(
        (0.40, 0, 0.125, 0),
        (130, 60),
        "Placeholder Text",
        (255, 255, 255),
        pygame.font.Font(None, 30),
        True,
        (0, 0, 0)
    )
    card_title.set_parent(card_frame)
    card_title.update()

    card_div = UIElement(
        (0.40, -10, 0.125, 10),
        pygame.Surface((2, 40))
    )
    card_div.set_parent(card_frame)
    card_div.surf.fill((0, 0, 0))
    card_div.update()

    # Load weather icons
    weather_icons = {}
    for filepath in glob.iglob("rsrc/*.png"):
        filename = os.path.splitext(os.path.basename(filepath))[0]
        weather_icons[filename] = pygame.image.load(filepath).convert_alpha()

    weather_widgets = []
    update_weather_widgets()

    # MAINLOOP
    update_forecast = pygame.USEREVENT + 1
    pygame.time.set_timer(update_forecast, 900000)      # Update forecast every 15 minutes

    run = True
    while run:
        CLOCK.tick(FPS_CAP)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False

            elif e.type == update_forecast:
                update_weather_widgets()
                pygame.time.set_timer(update_forecast, 900000)

            else:
                for scene in screen.scenes:                         # For each scene
                    for c in scene.get_descendants():               # For each element in scene
                        if any(c.handlers.values()):                # If element has any active bound listeners
                            c.handle_event(e)                       # Handle event

        screen.render((225, 225, 225))
        pygame.display.flip()