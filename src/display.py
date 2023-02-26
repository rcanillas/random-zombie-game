import math
import sys

from asciimatics.screen import Screen
from asciimatics.renderers import BarChart, StaticRenderer
from asciimatics.scene import Scene
from asciimatics.sprites import Sprite
from asciimatics.paths import Path
from asciimatics.widgets import (
    Frame,
    Widget,
    ListBox,
    Layout,
    Button,
    Divider,
    Text,
    TextBox,
)
from asciimatics.exceptions import NextScene, StopApplication, ResizeScreenError
from time import sleep
from random import randint


def find_contact(data, contact_id):
    return data[[c["id"] for c in data].index(contact_id)]


class ContactModel(object):
    def __init__(self) -> None:
        self.data = []
        self.id_count = 1
        self.current_id = None

    def add(self, contact):
        contact["id"] = self.id_count
        self.id_count += 1
        self.data.append(contact)

    def get_summary(self):
        return [[str(c["id"]), c["name"]] for c in self.data]

    def get_contact(self, contact_id):
        return [c for c in self.data if c["id"] == contact_id][0]

    def get_current_contact(self):
        if self.current_id is None:
            return {"name": "", "address": "", "phone": "", "email": "", "notes": ""}
        else:
            return self.get_contact(self.current_id)

    def update_current_contact(self, details):
        if self.current_id is None:
            self.add(details)
        else:
            current_contact = find_contact(self.data, self.current_id)
            for key, value in details.items:
                current_contact[key] = value

    def delete_contact(self, contact_id):
        contact_to_delete = find_contact(self.data, contact_id)
        self.data.remove(contact_to_delete)


class ListView(Frame):
    def __init__(self, screen, model):
        super(ListView, self).__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            on_load=self._reload_list,
            hover_focus=True,
            title="Contact List",
        )
        # Save off the model that accesses the contacts database.
        self._model = model

        # Create the form for displaying the list of contacts.
        self._list_view = ListBox(
            Widget.FILL_FRAME,
            model.get_summary(),
            name="contacts",
            on_select=self._on_pick,
        )
        self._edit_button = Button("Edit", self._edit)
        self._delete_button = Button("Delete", self._delete)
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._list_view)
        layout.add_widget(Divider())
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("Add", self._add), 0)
        layout2.add_widget(self._edit_button, 1)
        layout2.add_widget(self._delete_button, 2)
        layout2.add_widget(Button("Quit", self._quit), 3)
        self.fix()

    def _on_pick(self):
        self._edit_button.disabled = self._list_view.value is None
        self._delete_button.disabled = self._list_view.value is None

    def _reload_list(self):
        self._list_view.options = self._model.get_summary()
        self._model.current_id = None

    def _add(self):
        self._model.current_id = None
        raise NextScene("Edit Contact")

    def _edit(self):
        self.save()
        self._model.current_id = self.data["contacts"]
        raise NextScene("Edit Contact")

    def _delete(self):
        self.save()
        self._model.delete_contact(self.data["contacts"])
        self._reload_list()

    @staticmethod
    def _quit():
        raise StopApplication("User pressed quit")


class ContactView(Frame):
    def __init__(self, screen, model):
        super(ContactView, self).__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            hover_focus=True,
            title="Contact Details",
        )
        # Save off the model that accesses the contacts database.
        self._model = model

        # Create the form for displaying the list of contacts.
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Text("Name:", "name"))
        layout.add_widget(Text("Address:", "address"))
        layout.add_widget(Text("Phone number:", "phone"))
        layout.add_widget(Text("Email address:", "email"))
        layout.add_widget(TextBox(5, "Notes:", "notes", as_string=True))
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("OK", self._ok), 0)
        layout2.add_widget(Button("Cancel", self._cancel), 3)
        self.fix()

    def reset(self):
        # Do standard reset to clear out form, then populate with new data.
        super(ContactView, self).reset()
        self.data = self._model.get_current_contact()

    def _ok(self):
        self.save()
        self._model.update_current_contact(self.data)
        raise NextScene("Main")

    @staticmethod
    def _cancel():
        raise NextScene("Main")


def fn():
    return randint(0, 40)


def demo(screen):
    centre = (screen.width // 2, screen.height // 2)
    curve_path = []
    for i in range(0, 11):
        curve_path.append(
            (
                centre[0] + (screen.width / 4 * math.sin(i * math.pi / 5)),
                centre[1] - (screen.height / 4 * math.cos(i * math.pi / 5)),
            )
        )
    path = Path()
    path.jump_to(centre[0], centre[1] - screen.height // 4),
    path.move_round_to(curve_path, 60)
    sprite = Sprite(
        screen,
        renderer_dict={"default": StaticRenderer(images=["X"])},
        path=path,
        colour=Screen.COLOUR_RED,
        clear=False,
    )
    screen.play([Scene([sprite], 200)])


def demo2(screen, scene):
    scenes = [
        Scene([ListView(screen, contacts)], -1, name="Main"),
        Scene([ContactView(screen, contacts)], -1, name="Edit Contact"),
    ]

    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)


contacts = ContactModel()
last_scene = None
while True:
    try:
        Screen.wrapper(demo2, catch_interrupt=True, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene

Screen.wrapper(demo)
