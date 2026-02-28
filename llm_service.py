from dotenv import load_dotenv
import os

load_dotenv()

aws_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
region = os.getenv("AWS_REGION")