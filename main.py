import json
import os

import pystray
import requests
import sys
from PIL import Image
from pystray import MenuItem as item


class Main:
    def __init__(self):
        config_filename = 'config.json'
        try:
            with open(config_filename) as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {
                "ha_url": "http://your_ha_ip:8123",
                "ha_token": "YOUR_LONG_LIVED_ACCESS_TOKEN",
                "light_entity_id": "light.light_id",
                "colour_changing_icon": True
            }
            with open(config_filename, 'w') as f:
                json.dump(config, f, indent=4)
            print(
                f"Template configuration file '{config_filename}' created. Please edit it with your actual configuration.")
            sys.exit()

        self.ha_url = config['ha_url']
        self.ha_token = config['ha_token']
        self.light_entity_id = config['light_entity_id']
        self.colour_changing_icon = config['colour_changing_icon']

        self.headers = {
            "Authorization": f"Bearer {self.ha_token}",
            "Content-Type": "application/json",
        }

        self.service_data = {
            "entity_id": self.light_entity_id
        }

        colour = self.get_light_colour()
        if self.get_light_colour() == None:
            image = Image.open("icon_off.png")
        else:
            if self.colour_changing_icon:
                image = self.coloured_image(colour)
            else:
                image = Image.open("icon_on.png")

        menu = (
            item('Click', self.on_click, default=True, visible=False),
            item('Quit', self.quit_program),
            item('Reload', self.reload_program)
        )

        self.icon = pystray.Icon(name="LightToggle", icon=image, title="Toggle Lights", menu=menu)

    def get_light_colour(self):
        response = requests.get(f"{self.ha_url}/api/states/{self.light_entity_id}", headers=self.headers)

        if response.status_code == 200:
            light_state = response.json()
            colour = light_state["attributes"]["rgb_color"]
            print("Colour of the light:", colour)
            return colour
        else:
            print(f"Failed to get light colour. Status code: {response.status_code}")
            return None

    def coloured_image(self, new_colour):
        to_replace = (246, 211, 97)
        new_colour = (new_colour[0], new_colour[1], new_colour[2])

        image = Image.open("icon_on_colour.png").convert("RGBA")
        width, height = image.size
        pixels = image.load()

        for y in range(height):
            for x in range(width):
                current_colour = pixels[x, y][:3]

                if current_colour == to_replace:
                    pixels[x, y] = new_colour + (pixels[x, y][3],)

        return image

    def toggle_light(self):
        response = requests.post(f"{self.ha_url}/api/services/light/toggle", headers=self.headers,
                                 json=self.service_data)

        if response.status_code == 200:
            pass
        else:
            print(f"Failed to toggle light. Status code: {response.status_code}")
            self.err_icon()

    def err_icon(self):
        self.icon.icon = Image.open("icon_err.png")

    def toggle_icon(self):
        colour = self.get_light_colour()
        if colour == None:
            self.icon.icon = Image.open("icon_off.png")
        else:

            if self.colour_changing_icon:
                self.icon.icon = self.coloured_image(colour)
            else:
                self.icon.icon = Image.open("icon_on.png")

    def on_click(self):
        self.toggle_light()
        self.toggle_icon()

    def quit_program(self):
        print("Quitting program")
        self.icon.stop()
        sys.exit()

    def reload_program(self):
        print("Reloading program")
        self.icon.stop()
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def run(self):
        self.icon.run()


main = Main()
main.run()
