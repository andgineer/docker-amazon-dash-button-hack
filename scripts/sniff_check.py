import os.path
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

if __name__ == "__main__":
    from amazon_dash import AmazonDash

    amazon_dash = AmazonDash()
    amazon_dash.run()
