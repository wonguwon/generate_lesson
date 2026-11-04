import sys
from google import genai

print("파이썬 버전:", sys.version.split()[0])
print("google-genai 버전:", genai.__version__)
print("실행 중인 환경:", sys.prefix)
