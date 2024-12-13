from extrator import Extractor

from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
   
extractor = Extractor(api_key=api_key)

images = extractor.extract_images("https://docs.pje.jus.br/manuais-de-uso/Manual%20do%20advogado", include_descriptions=True)

