import pygame
import pytmx

class QuestGame:
    """ This class is a basic game.

    This class will load data, create a pyscroll group, a hero object.
    It also reads input and moves the Hero around the map.
    Finally, it uses a pyscroll group to render the map and Hero.
    """

    def __init__(self):
        """ Init the game here
        """

    def draw(self, surface):
        """ Drawing code goes here
        """

    def handle_input(self):
        """ Handle pygame input events
        """

    def update(self, dt):
        """ Tasks that occur over time should be handled here
        """

    def run(self):
        """ Run the game loop
        """

# simple wrapper to keep the screen resizeable
def init_screen(width, height):
    global temp_surface
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    temp_surface = pygame.Surface((width / 2, height / 2)).convert()
    return screen


def main() -> None:
    pygame.init()
    pygame.font.init()
    screen = init_screen(800, 600)
    pygame.display.set_caption('Quest - An epic journey.')

    try:
        game = QuestGame()
        game.run()
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()