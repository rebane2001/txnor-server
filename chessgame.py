from PIL import Image, ImageFont, ImageDraw
from cairosvg import svg2png
import random
import re
import io

import chess
import chess.engine
import chess.svg

# Start the stockfish engine
engine = chess.engine.SimpleEngine.popen_uci("stockfish")

valid_move_pattern = re.compile("^[a-h][0-8][a-h][0-8]q?$")
valid_move_pattern_open = re.compile("[a-h][0-8][a-h][0-8]q?")

board_colors = {
    "square light": "#FFFFFF",
    "square dark": "#5865F2",
    "square light lastmove": "#57F287",
    "square dark lastmove": "#57F287",
}

"""
The implementation of python-chess and stockfish in this file was rushed and isn't very good.
Please refer to the actual documentation if you wish to use them in your own project.
"""


def process_url(url):
    """Generate moves from a URL."""
    url = url.lower()
    moves = valid_move_pattern_open.findall(url)[::-1]

    # Generate a seed from the URL
    seed = 0
    seed_str = url.split("/")[-1]
    if "vieag" in seed_str or "vixag" in seed_str:
        seed_str = ""
    for c in seed_str:
        seed = (seed + ord(c)) % 1024

    return generate_state(moves, seed)


def generate_state(moves, seed):
    """Generate a game state from the moves."""

    # Create a new board and game
    board = chess.Board()
    game_id = random.random()
    result = None

    for move in moves:
        try:
            # Just skip invalid moves
            if not valid_move_pattern.match(move):
                continue
            if chess.Move.from_uci(move) not in board.legal_moves:
                continue

            # Add player move
            board.push(chess.Move.from_uci(move))
            if board.is_game_over():
                break

            # Add stockfish move
            # The way the engine is configured/seeded is bad, it is only left this way to keep older play URLs intact
            result = engine.play(board, chess.engine.Limit(depth=1024 + seed, nodes=1024 + seed), game=game_id)
            result = result.move
            board.push(result)
            if board.is_game_over():
                break
        except Exception as e:
            # If a move errors, we just skip over the move
            print(e)
            continue

    # Generate an SVG of the board
    svg = chess.svg.board(board, lastmove=result, colors=board_colors, size=300)
    board_png = io.BytesIO()
    svg2png(bytestring=svg, write_to=board_png)

    # Generate an empty image
    base = Image.new("RGBA", (395, 300), (0, 0, 0, 0))
    img = Image.open(board_png).convert("RGBA")

    # Generate an empty image
    base.paste(img, (0, 0), img)

    # Draw moves list as text
    draw = ImageDraw.Draw(base)
    font = ImageFont.truetype("impact.ttf", 24)
    draw.text((323, 3), "\n".join([str(stack).upper() for stack in board.move_stack[::-1]]), (255, 255, 255), font=font,
              stroke_width=2, stroke_fill=(0, 0, 0))

    # Draw example move text
    font = ImageFont.truetype("impact.ttf", 14)
    draw.text((304, 260), "example move:", (255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
    font = ImageFont.truetype("impact.ttf", 18)
    draw.text((304, 276), "s/g/$&b1c3", (255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0))

    # If the game is over, draw the outcome
    if board.is_game_over():
        outcome = board.outcome()
        font = ImageFont.truetype("impact.ttf", 96)
        if outcome.winner is None:
            draw.text((4, 84), "wtf draw?", (255, 255, 255), font=font, stroke_width=4, stroke_fill=(0, 0, 0))
        elif outcome.winner == chess.WHITE:
            draw.text((46, 84), "u win", (255, 255, 255), font=font, stroke_width=4, stroke_fill=(0, 0, 0))
        elif outcome.winner == chess.BLACK:
            draw.text((33, 84), "u lose", (255, 255, 255), font=font, stroke_width=4, stroke_fill=(0, 0, 0))

    # Return the image to the client
    out = io.BytesIO()
    base.save(out, "PNG")
    return out.getvalue()

# You can quit the engine like this:
# engine.quit()
