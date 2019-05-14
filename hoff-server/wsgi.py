import os, sys
sys.path.append('/home/ubuntu/hemelb-hoff')
from app import app as application

if __name__ == "__main__":
    application.run()
