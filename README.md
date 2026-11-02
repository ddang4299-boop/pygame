# Flappy Bird with Pygame

This is a personal project I made to learn Python and out of curiosity about how a simple game is built with the [Pygame](https://www.pygame.org/) library. If you find it useful, feel free to take a look!

## Features

- Bird flight, gravity, and continuously moving pipes
- Score display using digit images
- Start screen and game over screen
- Sound effects, with an on/off button in the top-left corner

## How to run

Install [Python 3](https://www.python.org/downloads/) first, then run these commands in the project folder:

```bash
pip install pygame
python flappybird.py
```

Make sure to run the game from the folder containing `flappybird.py`, because images and sounds are loaded using relative paths.

## How to play

| Action | Result |
|---|---|
| Left-click or press Space | Start the game, or make the bird fly up |
| Left-click or press Space after game over | Return to the start screen |
| Click the speaker icon | Turn sound on or off |

## Credits

Most of the images and sounds come from [flappy-bird-assets](https://github.com/samuelcust/flappy-bird-assets) by Samuel Custodio, under the MIT License. See [LICENSE-flappy-bird-assets.txt](LICENSE-flappy-bird-assets.txt) for details.

This is a non-commercial learning project and is not affiliated with the original Flappy Bird game or its creator.
