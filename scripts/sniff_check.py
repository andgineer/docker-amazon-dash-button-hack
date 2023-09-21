import os.path
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from amazon_dash import AmazonDash

amazon_dash = AmazonDash()
amazon_dash.run()
