from textual.app import App, ComposeResult
from textual.containers import Center
from textual.widgets import TabPane, Header, TabbedContent, Input, Static, Button, ProgressBar, Pretty
from textual.validation import ValidationResult, Validator
from modulos.main import get_list_content, get_user_watchlist, existe_usuario, existe_lista, get_film_info
from random import choice
from re import findall


class Application(App[None]):
    CSS_PATH = "styles/application.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(id="tabs"):
            with TabPane(":person_standing: Watchlists", id="watchlists"):
                yield UserInput()
            with TabPane(":film_frames: Lista"):
                yield ListInput()

    def on_mount(self) -> None:
        self.title = "Letterboxd Tools"

class UserInput(Static):
    def __init__(self):
        super().__init__()
        self.usuarios = []
        self.input_widget = Input(placeholder="Inserte un usuario", id="user-input")
        self.custom_button = Button("Ir a ruleta", id="button-roulette")
        self.roulette = Roulette()
        self.roulette.display = False

    def compose(self) -> ComposeResult:
        with Center():
            yield self.input_widget
        with Center():
            yield self.custom_button
        with Center():
            yield self.roulette

    def on_input_submitted(self, subm):
        if subm.value != "" and existe_usuario(subm.value):
            self.usuarios.append(subm.value)
            self.input_widget.clear()
            self.notify("Usuario agregado", timeout=1)
        else:
            self.notify("Usuario no existente", timeout=1, severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.usuarios != []:
            if event.button.id == "button-roulette":
                self.input_widget.display = False
                self.custom_button.display = False
                self.roulette.set_users(self.usuarios)
                self.roulette.display = True
        else:
            self.notify("Inserte por lo menos un usuario", severity="error")


class ListInput(Static):
    def __init__(self):
        super().__init__()
        self.url = None
        self.input_widget = Input(placeholder="Inserte una lista", 
                                  id="list-input",
                                  validators=[
                                      ListURL(),
                                  ])
        self.roulette = Roulette()
        self.roulette.display = False

    def compose(self) -> ComposeResult:
        with Center():
            yield self.input_widget
        with Center():
            yield self.roulette

    
    def on_input_submitted(self, subm):
        if subm.value != "" and existe_lista(subm.value):
            self.url = subm.value
            self.input_widget.clear()
            self.notify("Lista registrada", timeout=1)
            self.input_widget.display = False
            self.roulette.set_list(self.url)
            self.roulette.display = True
        else:
            self.notify("Lista inexistente", timeout=1, severity="error")


class Roulette(Static):
    def __init__(self, list_url=None, users=[]):
        super().__init__()
        self.films_list = []
        self.film_displayed = ""
        self.film_displayed_info = ""
        self.film_title = Static(renderable="[b]"+self.film_displayed, id="film-title")
        self.film_info = Static(id="film-info")
        self.film_review = Static(id="film-review")
        self.progress_bar = ProgressBar(total=0, show_eta=False)
        self.watched_button = Button("Vista\n:eye:", id="watched-button")

    def compose(self) -> ComposeResult:
        with Center():
            yield self.film_title
        with Center():
            yield self.film_info
        with Center():
            yield self.film_review
        with Center():
            yield self.watched_button
        with Center():
            yield self.progress_bar

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "watched-button":
            self.films_list.remove(self.film_displayed)
            self.update_info()
            self.progress_bar.advance(1)

    def set_users(self, users):
        for user in users:
            self.films_list += get_user_watchlist(user)
        self.largo_inicial = len(self.films_list)
        self.vistas = 0
        self.progress_bar.total = self.largo_inicial
        self.update_info()

    def set_list(self, url):
        self.films_list += get_list_content(url)
        self.largo_inicial = len(self.films_list)
        self.vistas = 0
        self.progress_bar.total = self.largo_inicial
        self.update_info()

    def update_info(self):
        self.film_displayed = choice(self.films_list)
        self.film_displayed_info = get_film_info(f"https://letterboxd.com{self.film_displayed[1]}")
        self.film_title.update("[link=https://letterboxd.com"+self.film_displayed[1]+"]"+self.film_displayed[0]+"[/link]")
        self.film_info.update(f"{self.film_displayed_info['anio']} - {self.film_displayed_info['director']}")
        self.film_review.update(f"{self.film_displayed_info['review']}")

class ListURL(Validator):  
    def validate(self, value: str) -> ValidationResult:
        if self.is_list_url(value):
            return self.success()
        else:
            return self.failure("No es una url válida.")

    @staticmethod
    def is_list_url(value: str) -> bool:
        return findall(pattern=r"https:\/\/letterboxd.com\/\w+\/list\/",
                       string=value) != []


if __name__ == "__main__":
    Application().run()
