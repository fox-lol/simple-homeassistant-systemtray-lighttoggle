import json
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
                "light_entity_id": "light.light_id"
            }
            with open(config_filename, 'w') as f:
                json.dump(config, f, indent=4)
            print(
                f"Template configuration file '{config_filename}' created. Please edit it with your actual configuration.")
            sys.exit()

        self.ha_url = config['ha_url']
        self.ha_token = config['ha_token']
        self.light_entity_id = config['light_entity_id']

        self.headers = {
            "Authorization": f"Bearer {self.ha_token}",
            "Content-Type": "application/json",
        }

        self.service_data = {
            "entity_id": self.light_entity_id
        }

        self.light_state = self.are_lights_on()

        if self.light_state:
            image = Image.open("icon_on.png")
        else:
            image = Image.open("icon_off.png")

        menu = (item('Click', self.on_click, default=True, visible=False), item('Quit', self.quit_program))

        self.icon = pystray.Icon(name="LightToggle", icon=image, title="Toggle Lights", menu=menu)

    def toggle_light(self):
        response = requests.post(f"{self.ha_url}/api/services/light/toggle", headers=self.headers,
                                 json=self.service_data)

        if response.status_code == 200:
            print("Light toggled successfully")
        else:
            print(f"Failed to toggle light. Status code: {response.status_code}")
            self.err_icon()

    def are_lights_on(self):
        response = requests.get(f"{self.ha_url}/api/states/{self.light_entity_id}", headers=self.headers)

        if response.status_code == 200:
            light_state = response.json()["state"]
            return light_state == "on"
        else:
            print(f"Failed to get light state. Status code: {response.status_code}")
            self.err_icon()
            return None

    def err_icon(self):
        self.icon.icon = Image.open("icon_err.png")

    def toggle_icon(self):
        if self.light_state:
            print("make on icon")
            self.light_state = False
            self.icon.icon = Image.open("icon_off.png")
        else:
            print("make off icon")
            self.light_state = True
            self.icon.icon = Image.open("icon_on.png")

    def on_click(self):
        print("Icon clicked!")
        self.toggle_icon()
        self.toggle_light()

    def quit_program(self):
        self.icon.stop()
        sys.exit()

    def run(self):
        self.icon.run()


main = Main()
main.run()
