with open("image/qlue.png", "rb") as image:
    f = image.read()
    qlue = bytes(f)

with open("image/invalid.png", "rb") as image:
    f = image.read()
    invalid = bytes(f)