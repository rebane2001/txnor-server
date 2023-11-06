from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import requests
import random
import web
import io
import re

# Chess
import chessgame

# Configure the app
import swordgame

app = web.application(('(.*)', 'SexHack'), globals())
web.config.debug = False
host = "127.0.0.1"
port = 8000

# Load images into memory
with open("img/sex_default.png", "rb") as f:
    default_img = f.read()
with open("img/sex_base_game.png", "rb") as f:
    base_img = f.read()
with open("img/6969th.png", "rb") as f:
    six_nine = f.read()

# User-Agent for Tenor requests, it's nice to tell them who you are
headers = {
    'User-Agent': 'A Discord Bot by an unknown person using github.com/rebane2001/txnor-server',
}


class SexHack:
    @staticmethod
    def default_response():
        """Return default image"""
        return default_img

    @staticmethod
    def pony():
        """Return an image from Derpibooru"""
        r = requests.get(
            "https://derpibooru.org/api/v1/json/search/images?"
            "q=pony,score.gte:1000,aspect_ratio:1,safe&sf=random&per_page=1",
            headers=headers, timeout=3)
        medium = r.json()["images"][0]["representations"]["medium"]
        content = requests.get(medium, headers=headers, timeout=3).content
        return content

    @staticmethod
    def math_challenge():
        """Return a random math challenge"""
        # Create new image
        img = Image.new("RGBA", (450, 135), (255, 255, 255, 255))

        # Draw text on the image
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("impact.ttf", 32)
        draw.text((450 / 2, 10), f"Math challenge (99% fail):", (255, 255, 255), font=font, anchor="ma",
                  stroke_width=2, stroke_fill=(0, 0, 0))

        # Generate a random math challenge
        num_a = random.randint(2, 6)
        num_b = int(random.randint(3, 12) * num_a)
        num_c = random.randint(3, 24)

        # Draw the math challenge as text
        font = ImageFont.truetype("impact.ttf", 64)
        draw.text((450 / 2, 50), f"{num_b} / {num_a} + {num_c}", (255, 255, 255), font=font, anchor="ma",
                  stroke_width=2, stroke_fill=(0, 0, 0))

        # Return the image to the client
        out = io.BytesIO()
        img.save(out, "PNG")
        return out.getvalue()

    @staticmethod
    def generate_img(name):
        """Generate s/e/x or double s/e/x image"""
        url = f"https://tenor.com/view/{name[6:]}"
        r = requests.get(url, headers=headers, timeout=3)
        search = re.search(r'<meta class="dynamic" name="twitter:image" content="https://(?:c|media).tenor.com/([^"]*)">',
                           r.text)
        img_url = f"https://c.tenor.com/{search.group(1)}".replace("AAC/", "AAe/")
        img_raw = requests.get(img_url, stream=True, headers=headers, timeout=3).raw

        img = Image.open(img_raw).resize((350, 185)).convert("RGB")

        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("impact.ttf", 32)
        draw.text((350 / 2, 0), "WTF DISCORD SEX", (255, 255, 255), font=font, anchor="ma", stroke_width=2,
                  stroke_fill=(0, 0, 0))
        draw.text((350 / 2, 185), "??? WTF ??? SEX ???", (255, 255, 255), font=font, anchor="md", stroke_width=2,
                  stroke_fill=(0, 0, 0))

        # JPEGify the image slightly
        jpg = io.BytesIO()
        img.save(jpg, "JPEG", quality=10)
        img = Image.open(jpg).resize((190, 135)).convert("RGBA")

        # Apply the GIF thumbnail to the template
        base = Image.open(io.BytesIO(base_img))
        base.paste(img, (5, 159))

        double_sex = name[3] == "x"
        if double_sex:
            # Draw text
            draw = ImageDraw.Draw(base)
            font = ImageFont.truetype("impact.ttf", 36)
            draw.text((394 / 2, -10), "ULTRA DOUBLE SEX", (255, 255, 255), font=font, anchor="ma", stroke_width=2,
                      stroke_fill=(0, 0, 0))
            draw.text((394 / 2, 295), "ACTIVATED ??? HOW", (255, 255, 255), font=font, anchor="md", stroke_width=2,
                      stroke_fill=(0, 0, 0))

            # Add a red-ish background
            bg = Image.new("RGBA", base.size, (35, 0, 0, 255))
            bg.paste(base, (0, 0), base)

            # JPEGify and saturate the image
            jpg = io.BytesIO()
            bg.convert("RGB").resize((300, 200)).save(jpg, "JPEG", quality=50)
            base = Image.open(jpg).convert("RGB")
            base = ImageEnhance.Color(base).enhance(10.5).resize((395, 300))

        # Return the image to the client
        out = io.BytesIO()
        base.save(out, "PNG")
        return out.getvalue()

    def handle_request(self, name):
        try:
            # 6969th winner image (disable for chess)
            if random.randint(0, 6969) == 6969 and "ag" not in name:
                web.header('Cache-Control', 'no-store')
                return six_nine

            # Math challenge
            if re.search(r'^/(math|math_?challenge)/?[A-Za-z0-9_-]*$', name):
                web.header('Cache-Control', 'no-store')
                return self.math_challenge()

            # /viqw/
            if re.search(r'^/vi(q|questrian?)w/[A-Za-z0-9_-]*$', name):
                web.header('Cache-Control', 'no-store')
                return self.pony()

            # Enable caching from this point onward
            web.header('Cache-Control', 'public, max-age=86400')

            # /vieord/ and /vixord/
            if re.search(r'^/vi[ex]ord[A-Za-z]*/[A-Za-z0-9_-]*$', name):
                return swordgame.process_url(name)

            # /vieag/ and /vixag/
            if re.search(r'^/vi[ex]ag[A-Za-z0-9]*/[A-Za-z0-9_-]*$', name):
                return chessgame.process_url(name)

            # /view/ and /vixw/
            if re.search(r'^/vi[ex]w/[A-Za-z0-9_-]*$', name):
                return self.generate_img(name)
        except Exception as e:
            """We catch Exceptions because we want to show the default image instead of an error page"""
            print(e)

    def GET(self, name):
        """Handle a request"""
        web.header('Content-type', 'image/png')
        # Filter the name so unicode paths don't error
        filtered_name = re.sub(r'[^\.\/A-Za-z0-9_-]+', '', name)
        # Filter out languages in URL and handle edge-case for english double sex
        filtered_name = re.sub(r'^/xn-../view', '/vixw', filtered_name)
        filtered_name = re.sub(r'^/[A-Za-z-]*/vi', '/vi', filtered_name)
        # Return default image if one was not generated
        return self.handle_request(filtered_name) or self.default_response()


if __name__ == "__main__":
    web.httpserver.runsimple(app.wsgifunc(), (host, port))
