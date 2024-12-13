import os
import requests
import bs4
from fpdf import FPDF
from PIL import Image
import google.generativeai as genai

class Extractor:
    """
    Classe para extrair textos e imagens de um site e salvá-los localmente.
    """

    def __init__(self, model: str = "gemini-1.5-pro", api_key: str = None, output_folder: str = "./"):
        """
        Inicializa a classe Extractor com um modelo de IA, uma chave de API e uma pasta de saída.

        :param model: Nome do modelo de IA (padrão: "gemini-1.5-pro").
        :param api_key: Chave da API para autenticação.
        :param output_folder: Pasta padrão para salvar os arquivos extraídos.
        """
        if api_key is None:
            raise ValueError("A chave da API (api_key) deve ser fornecida.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.output_folder = output_folder

    def extract_text(self, url: str, doc_type: str = "txt", save_path: str = "./") -> str:
        """
        Extrai o texto principal da página HTML, retorna como string e salva no formato especificado.

        :param url: URL da página para extração do texto.
        :param doc_type: Tipo de documento para salvar o texto ("txt" ou "pdf").
        :param save_path: Caminho para salvar o arquivo extraído.
        :return: O texto extraído da página.
        """

        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Erro ao acessar a URL: {url}. Código de status: {response.status_code}")

        #corrige o encoding para evitar erros em caracteres acentuados
        response.encoding = response.apparent_encoding
        soup = bs4.BeautifulSoup(response.text, "html.parser")

        text = soup.get_text()
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        text = " ".join(text.split())

        #verifica se o caminho para salvar o texto já existe. Caso não exista, é criado.
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        file_path = os.path.join(save_path, f"extracted_text.{doc_type}")
        
        if doc_type == "txt":
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text)
        elif doc_type == "pdf":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, text.encode('latin-1', 'replace').decode('latin-1'))
            pdf.output(file_path)
        else:
            raise ValueError("Tipo de documento não suportado. Use 'txt' ou 'pdf'.")

        return text

    def extract_images(self, url: str, save_path: str = None, include_descriptions: bool = False) -> list:
        """
        Extrai os URLs das imagens da página HTML, salva as imagens e retorna a lista de URLs.

        :param url: URL da página para extração das imagens.
        :param save_path: Caminho para salvar as imagens extraídas.
        :param include_descriptions: Indica se as descrições das imagens devem ser geradas e salvas.
        :return: Uma lista de URLs das imagens.
        """
        if save_path is None:
            save_path = os.path.join(self.output_folder, "images")

        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Erro ao acessar a URL: {url}. Código de status: {response.status_code}")

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        images = soup.find_all("img")

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        image_urls = []
        descriptions_folder = f"{save_path}_descriptions"

        if include_descriptions and not os.path.exists(descriptions_folder):
            os.makedirs(descriptions_folder)

        file_index = 1  # Controle do índice dos arquivos salvos

        for img in images:
            img_url = img.get("src")
            if not img_url:
                continue

            if not img_url.startswith("http"):
                img_url = requests.compat.urljoin(url, img_url)

            image_urls.append(img_url)

            try:
                img_data = requests.get(img_url).content
                img_path = os.path.join(save_path, f"image_{file_index}.jpg")
                with open(img_path, "wb") as img_file:
                    img_file.write(img_data)

                if include_descriptions:
                    image = Image.open(img_path)
                    response = self.model.generate_content(
                        ["Faça a descrição textual da imagem", image],
                        stream=True,
                        generation_config=genai.types.GenerationConfig(temperature=1)
                    )
                    response.resolve()
                    description = response.text
                    desc_file_path = os.path.join(descriptions_folder, f"image_{file_index}_description.txt")
                    with open(desc_file_path, "w", encoding="utf-8") as desc_file:
                        desc_file.write(description)

                file_index += 1  # Incrementa o índice apenas quando a imagem é salva com sucesso

            except Exception as e:
                print(f"Erro ao baixar ou descrever imagem {img_url}: {e}")

        return image_urls