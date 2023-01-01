import io
import re

from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import random
import os

fonts = {
    "med": "swordgame/font/Ginto Nord Medium.ttf",
    "blk": "swordgame/font/Ginto Nord Black.ttf",
}

images = {}
poses_path = "swordgame/art"
for file in os.listdir(poses_path):
    with open(f"{poses_path}/{file}", "rb") as f:
        images[file[:-4]] = f.read()


class Creature:
    def __init__(self, rand):
        self.rand = rand
        self.hp_max = 10
        self.hp = self.hp_max
        self.attack = [8, 12]
        self.love = 10
        self.name = "Creature"
        self.images = ["frame"]

    def give_hug(self):
        self.love -= 1

    def turn(self):
        dmg = self.rand.randint(*self.attack)
        return f"The {self.name} attacks you for {dmg} DMG.", dmg

    def deal_attack(self, dmg):
        self.hp -= dmg


class Dog(Creature):
    def __init__(self, rand):
        super().__init__(rand)
        self.attack = [1, 4]
        self.love = 2
        self.hp_max = 10
        self.hp = self.hp_max
        self.name = "Dog"
        self.images = ["dog_normal"]

    def give_hug(self):
        super().give_hug()
        self.images = ["dog_bark"]

    def deal_attack(self, dmg):
        super().deal_attack(dmg)
        self.images = ["dog_normal"]


class Bear(Creature):
    def __init__(self, rand):
        super().__init__(rand)
        self.attack = [1, 10]
        self.hp_max = 20
        self.hp = self.hp_max
        self.love = 3
        self.name = "Bear"
        self.images = ["bear_normal"]

    def turn(self):
        dmg = self.rand.randint(*self.attack)
        if self.rand.randint(0, 1) == 1:
            return f"The {self.name} attacks you for {dmg} DMG.", dmg
        else:
            return f"The {self.name} attacks you clumsily and misses.", 0


class Horse(Creature):
    def __init__(self, rand):
        super().__init__(rand)
        self.attack = [0, 8]
        self.love = 5
        self.hp_max = 13
        self.hp = self.hp_max
        self.name = "Horse"
        self.images = ["horse_normal"]
        self.hugged = False

    def give_hug(self):
        super().give_hug()
        self.hugged = True

    def turn(self):
        if self.hugged:
            self.hugged = False
            return f"The {self.name} hugs you back!", 0
        dmg = self.rand.randint(*self.attack)
        return f"The {self.name} attacks you for {dmg} DMG.", dmg


class Skeleton(Creature):
    def __init__(self, rand):
        super().__init__(rand)
        self.attack = [1, 7]
        self.love = 4
        self.hp_max = 10
        self.hp = self.hp_max
        self.name = "Skeleton"
        self.images = ["skeleton_normal"]


class Snake(Creature):
    def __init__(self, rand):
        super().__init__(rand)
        self.attack = [2, 4]
        self.love = 4
        self.hp_max = 6
        self.hp = self.hp_max
        self.name = "Snake"
        self.color = rand.choice(["magenta", "green", "yellow"])
        self.images = [F"snake_{self.color}"]


class Dragon(Creature):
    def __init__(self, rand):
        super().__init__(rand)
        self.attack = [8, 16]
        self.hp_max = 100
        self.hp = self.hp_max
        self.love = 20
        self.name = "Dragon"
        self.color = rand.choice(["blue", "green", "orange", "red"])
        self.images = [f"dragon_{self.color}_idle"]
        self.move_count = 0

    def turn(self):
        if self.move_count == 2:
            self.move_count = 0
            dmg = self.rand.randint(*self.attack)
            self.images = ["dragon_fire", f"dragon_{self.color}_fire"]
            return f"The {self.name} attacks you for {dmg} DMG.", dmg
        else:
            self.move_count += 1
            self.images = [f"dragon_{self.color}_idle"]
            return "The Dragon looks at you...", 0


class Wumpus:
    def __init__(self, rand):
        self.rand = rand
        self.hp_max = 10
        self.hp = self.hp_max
        self.attack = [3, 8]
        self.defending = False
        self.name = "Wumpus"
        self.images = ["wumpus_violent_pose"]

    def action_def(self, msg):
        possible_images = [
            "angry",
            "bush",
            "scared",
            "shield",
            "violent_pose",
            "wave",
        ]
        self.images = ["wumpus_" + self.rand.choice(possible_images)]
        for img in possible_images:
            if img in msg:
                self.images = [f"wumpus_{img}"]

    def action_atk(self, msg):
        self.images = ["wumpus_" + self.rand.choice([
            "angry",
            "sword_1",
            "sword_2",
            "violent_pose",
        ])]
        if "nae nae" in msg or "violent pose" in msg:
            self.images = ["wumpus_violent_pose"]
        if "sword" in msg:
            self.images = [f"wumpus_sword_{self.rand.randint(1,2)}"]

    def action_hug(self, msg):
        self.images = ["wumpus_" + self.rand.choice([
            "bush",
            "scared",
            "wave",
        ]), "wumpus_heart"]
        if "wave" in msg:
            self.images = ["wumpus_wave"]


def process_url(url):
    """Generate moves from a URL."""
    valid_moves = re.compile("(ATK|DEF|HUG)")
    moves = []
    for part in url.upper().split("/"):
        if "VIEORD" in part or "VIXORD" in part:
            moves = valid_moves.findall(part)[::-1]

    url = url.lower()
    seed = 0
    seed_str = url.split("/")[-1]
    if "vieord" in seed_str or "vixord" in seed_str:
        seed_str = ""
    for c in seed_str:
        seed = (seed + ord(c)) % 8096

    rand = random.Random()
    rand.seed(seed)

    return process_game(rand, moves)


you_defend_msgs = [
    "You hide behind a bush.",
    "You close your eyes.",
    "You use a massive shield.",
    "You defend yourself.",
    "You ignore the damage.",
    "You smile at the CREATURE.",
    "You solemnly swear not to be scared.",
    "You dance aggressively.",
    "You shake a fist at the CREATURE.",
]

you_attack_msgs = [
    "You attack the CREATURE for DAMAGE DMG.",
    "You charge at the CREATURE for DAMAGE DMG.",
    "You swing your sword for DAMAGE DMG.",
    "You hit the CREATURE for DAMAGE DMG.",
    "You nae nae the CREATURE for DAMAGE DMG.",
    "You strike a violent pose for DAMAGE DMG.",
]

you_hug_msgs = [
    "You hug the CREATURE.",
    "You wave at the CREATURE.",
    "You say \"hi\"",
    "You say \"I love you!\"",
    "You challenge the CREATURE to a CoD 1v1.",
    "You invite the CREATURE over.",
]


def render_image(state, messages, wumpus, creature):
    board = Image.open(io.BytesIO(images["board"])).convert("RGBA")
    for img in wumpus.images + creature.images:
        i = Image.open(io.BytesIO(images[img])).convert("RGBA")
        i = ImageEnhance.Color(i).enhance(0.0)
        i = ImageEnhance.Brightness(i).enhance(100.0)
        board = Image.alpha_composite(board, i)
        board = Image.alpha_composite(board, i)
        board = Image.alpha_composite(board, i)
        i = Image.open(io.BytesIO(images[img])).convert("RGBA")
        board = Image.alpha_composite(board, i)

    i = Image.open(io.BytesIO(images["frame"])).convert("RGBA")
    board = Image.alpha_composite(board, i)

    # Creature infobox
    draw = ImageDraw.Draw(board)
    font = ImageFont.truetype(fonts['blk'], 10)
    draw.text((228, 139), creature.name, (0, 0, 0), font=font)
    font = ImageFont.truetype(fonts['med'], 9)
    draw.text((363, 139), f"{creature.attack[0]}-{creature.attack[1]}ATK", (0, 0, 0), font=font, anchor="ra")

    # Messages
    font = ImageFont.truetype(fonts['blk'], 11)
    for i, msg in enumerate(messages):
        draw.text((46, 184 + i * 12), msg, (0, 0, 0), font=font)

    # Health bars
    # 30x47 - 140x10
    # 227x152 - 140x10
    for health_bar in [((30, 47), wumpus), ((227, 152), creature)]:
        health_size = (140, 10)
        health_pos = health_bar[0]
        health_delta = int(max(140 * health_bar[1].hp / health_bar[1].hp_max, 0))
        crop_coords = (
            health_pos[0] + health_delta, health_pos[1],
            health_pos[0] + health_size[0], health_pos[1] + health_size[1]
        )
        health = board.crop(crop_coords)
        health = ImageEnhance.Color(health).enhance(0.0)
        health = ImageEnhance.Brightness(health).enhance(2.0)
        board.paste(health, crop_coords[:2])

    if state:
        i = Image.open(io.BytesIO(images[f"end_{state}"])).convert("RGBA")
        board = Image.alpha_composite(board, i)
        draw = ImageDraw.Draw(board)
        font = ImageFont.truetype(fonts['med'], 14)
        msg = {
            "good": f"You successfully\ndefeated the {creature.name}!",
            "bad": f"You got your rear-end\nhanded to you!",
            "best": f"You successfully\nbefriended the {creature.name}!",
        }[state]
        for i, line in enumerate(msg.split("\n")):
            draw.text((395//2, 105 + i*15), line, (255, 255, 255), font=font, anchor="ma")

    # Return the image to the client
    out = io.BytesIO()
    board.save(out, "PNG")
    return out.getvalue()


def process_game(rand, moves):
    wumpus = Wumpus(rand)
    creature = rand.choice([Dog, Bear, Horse, Skeleton, Snake, Dragon])(rand)
    messages = [f"You are fighting a {creature.name}!"]

    state = None
    for move in moves:
        messages.clear()

        wumpus.defending = move == "DEF"
        if wumpus.defending:
            msg = rand.choice(you_defend_msgs).replace("CREATURE", creature.name)
            messages.append(msg)
            wumpus.action_def(msg)
        if move == "ATK":
            dmg = rand.randint(*wumpus.attack)
            creature.deal_attack(dmg)
            msg = rand.choice(you_attack_msgs).replace("CREATURE", creature.name).replace("DAMAGE", str(dmg))
            messages.append(msg)
            wumpus.action_atk(msg)
        if move == "HUG":
            msg = rand.choice(you_hug_msgs).replace("CREATURE", creature.name)
            messages.append(msg)
            creature.give_hug()
            wumpus.action_hug(msg)

        if creature.hp <= 0:
            state = "good"
            break

        if creature.love <= 0:
            state = "best"
            break

        creature_move = creature.turn()
        if wumpus.defending:
            creature_move = (creature_move[0].replace(str(creature_move[1]), "0"), creature_move[1])
        messages.append(creature_move[0])
        if not wumpus.defending:
            wumpus.hp -= creature_move[1]

        if wumpus.hp <= 0:
            state = "bad"
            break

    return render_image(state, messages, wumpus, creature)
