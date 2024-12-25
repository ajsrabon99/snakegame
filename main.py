import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Rectangle, Color
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.clock import Clock

Clock.schedule_interval(lambda dt: print(f"FPS: {Clock.get_fps()}"), 1)



import random

kivy.require('2.1.0')  # Ensure you have the correct Kivy version

# Constants
GRID_SIZE = 20  # Grid size for the game
SPEED = 10  # Speed of the snake

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Add background image
        with self.canvas.before:
            self.bg_image = Rectangle(source="assets/images/home_screen.jpg", pos=(0, 0), size=Window.size)

        # Add "Play" button
        self. play_button = Button(
            text="Play",
            font_size=32,
            size_hint=(None, None),
            size=(Window.width * 0.3, Window.height * 0.1),  # Scaled size
            pos=(Window.width / 2 - Window.width * 0.15, Window.height / 2 - Window.height * 0.05),
            background_color=(0.53, 0.81, 0.92, 1),  # Sky blue
        )
        # Change the color on press and release
        def on_button_press(instance):
            instance.background_color = (0, 0.5, 0, 1)  # Dark green (pressed state)

        def on_button_release(instance):
            instance.background_color = (0, 1, 0, 1)  # Green (normal state)

        self.play_button.bind(on_press=on_button_press)
        self.play_button.bind(on_release=on_button_release)
        self.play_button.bind(on_press=self.start_game)
        self.add_widget(self.play_button)

        # Bind to resize events
        Window.bind(on_resize=self.on_resize)


    def start_game(self, instance):
        """Switch to the SnakeGame screen."""
        self.manager.current = "game"

    def on_resize(self, instance, width, height):
        """Update background and button size/position on resize."""
        self.bg_image.size = (width, height)
        self.play_button.size = (width * 0.3, height * 0.1)
        self.play_button.pos = (width / 2 - self.play_button.size[0] / 2, height / 2 - self.play_button.size[1] / 2)

    def on_size(self, *args):
        """Update background size when window size changes."""
        self.bg_image.size = Window.size


class SnakeGame(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Add background image
        with self.canvas.before:
            self.bg_image = Rectangle(source="assets/images/Snake_back.jpg", pos=(0, 0), size=Window.size)

        self.init_game()

        # Draw the snake and food
        with self.canvas:
            self.snake_rectangles = [Rectangle(pos=self.snake[0], size=(GRID_SIZE, GRID_SIZE))]
            self.food_rect = Rectangle(pos=self.food, size=(GRID_SIZE, GRID_SIZE))
            self.score_label = Label(text=f'Score: {self.score}', font_size=24, pos=(10, Window.height - 40))
            self.add_widget(self.score_label)

        # Bind key events
        Window.bind(on_key_down=self.on_key_down)

        # Schedule the update function
        Clock.schedule_interval(self.update, 1.0 / SPEED)

    def init_game(self):
        """Initialize or reset the game state."""
        self.snake = [(100, 100), (80, 100), (60, 100)]  # Initial snake body
        self.snake_direction = (GRID_SIZE, 0)  # Initial movement direction (right)
        self.food = (200, 200)  # Food position
        self.score = 0  # Player's score
        self.game_over = False  # Game over flag

        # Hide the restart button initially
        if hasattr(self, 'restart_button'):
            self.remove_widget(self.restart_button)

    def generate_food(self):
        """Generate food at a random position."""
        self.food = (random.randint(0, (Window.width - GRID_SIZE) // GRID_SIZE) * GRID_SIZE,
                     random.randint(0, (Window.height - GRID_SIZE) // GRID_SIZE) * GRID_SIZE)

    def update(self, dt):
        """Update the game state: move the snake, check for collisions."""
        if self.game_over:
            return

        # Resize background dynamically
        self.bg_image.size = Window.size

        # Move the snake
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.snake_direction[0], head_y + self.snake_direction[1])

        # Add the new head
        self.snake = [new_head] + self.snake[:-1]

        # Check for collisions with walls or itself
        if new_head in self.snake[1:] or not (0 <= new_head[0] < Window.width and 0 <= new_head[1] < Window.height):
            self.game_over = True
            self.score_label.text = f'Game Over!'
            self.show_restart_button()
            return

        # Check if snake eats food
        if new_head == self.food:
            self.snake.append(self.snake[-1])  # Add a new body part
            self.score += 5  # Increase score
            self.score_label.text = f'Score: {self.score}'

            # Generate new food position
            self.generate_food()

        # Clear the canvas and redraw everything
        self.canvas.clear()
        with self.canvas.before:
            # Redraw the background
            self.bg_image = Rectangle(source="assets/images/Snake_back.jpg", pos=(0, 0), size=Window.size)

        with self.canvas:
            for segment in self.snake:
                Color(0, 1, 0)  # Green snake
                Rectangle(pos=segment, size=(GRID_SIZE, GRID_SIZE))
            Color(1, 0, 0)  # Red food
            self.food_rect.pos = self.food
            Rectangle(pos=self.food, size=(GRID_SIZE, GRID_SIZE))

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        """Handle key presses to change the snake's direction."""
        if self.game_over:
            return

        # Arrow keys and WASD controls
        if keycode == 275 or text == 'd' and self.snake_direction != (-GRID_SIZE, 0):  # Right arrow or D
            self.snake_direction = (GRID_SIZE, 0)
        elif keycode == 276 or text == 'a' and self.snake_direction != (GRID_SIZE, 0):  # Left arrow or A
            self.snake_direction = (-GRID_SIZE, 0)
        elif keycode == 273 or text == 'w' and self.snake_direction != (0, -GRID_SIZE):  # Up arrow or W
            self.snake_direction = (0, GRID_SIZE)
        elif keycode == 274 or text == 's' and self.snake_direction != (0, GRID_SIZE):  # Down arrow or S
            self.snake_direction = (0, -GRID_SIZE)

    def generate_food(self):
        """Generate food at a random position."""
        self.food = (random.randint(0, (Window.width - GRID_SIZE) // GRID_SIZE) * GRID_SIZE,
                     random.randint(0, (Window.height - GRID_SIZE) // GRID_SIZE) * GRID_SIZE)

    def show_restart_button(self):
        """Display the Restart button and final score when the game is over."""
        # Change the "Game Over" label
        self.game_over_label = Label(
            text="Game Over\nFinal Score: {}".format(self.score),  # Combine the two texts
            font_size=36,
            bold=True,
            color=(1, 0, 0, 1),  # Red color
            halign='center',
            valign='middle',
            size_hint=(None, None),
            size=(300, 100),
            pos=(Window.width / 2 - 150, Window.height / 2 - 50),
        )
        self.add_widget(self.game_over_label)

        # Show Restart button at the bottom side
        self.restart_button = Button(
            text="Restart",
            size_hint=(None, None),
            size=(200, 50),
            pos=(Window.width / 2 - 100, 50),
            background_color=(0.53, 0.81, 0.92, 1),  # Sky blue color
            background_down="darkskyblue.png",  # Hover effect
        )
        self.restart_button.bind(on_press=self.restart_game)
        self.add_widget(self.restart_button)


    def restart_game(self, instance):
        """Restart the game when the button is pressed."""
        self.init_game()
        self.score_label.text = f'Score: {self.score}'  # Reset score
        self.canvas.clear()  # Clear the canvas for new game

        # Redraw the initial snake and food
        with self.canvas:
            for segment in self.snake:
                Color(0, 1, 0)
                Rectangle(pos=segment, size=(GRID_SIZE, GRID_SIZE))
            Color(1, 0, 0)
            self.food_rect.pos = self.food
            Rectangle(pos=self.food, size=(GRID_SIZE, GRID_SIZE))

        # Start the game again
        self.game_over = False
        Clock.schedule_interval(self.update, 1.0 / SPEED)  # Restart game loop


class ReptileRun(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(SnakeGame(name="game"))
        return sm


if __name__ == "__main__":
    ReptileRun().run()
