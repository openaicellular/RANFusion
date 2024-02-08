# logo.py
from pyfiglet import Figlet

def create_logo():
    # Create a Figlet object with the desired font
    f = Figlet(font='big')

    # Create the logo text
    text = "Welcome to RANFusion"

    # Create the logo
    logo = f.renderText(text)

    return logo
