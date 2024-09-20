from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from peft import AutoPeftModelForSequenceClassification
import os
import spacy
from spellchecker import SpellChecker
from sentence_transformers import SentenceTransformer
import datasets
import requests
import re
from utils.logging_config import logger
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")


try:
    load_dotenv('config.env')
except Exception as e:
    logger.error(f"An error occurred while loading the config.env file: {e}")
    sys.exit(1)
    


try:
    tags_dataset_path = os.getenv("TAGS_DATASET_PATH")
    answers_fr_dataset_path = os.getenv("ANSWERS_FR_DATASET_PATH")
    answers_ar_dataset_path = os.getenv("ANSWERS_AR_DATASET_PATH")
    
    tags_faiss_index = os.getenv("TAGS_FAISS_INDEX")
    answers_fr_faiss_index = os.getenv("ANSWERS_FR_FAISS_INDEX")
    answers_ar_faiss_index = os.getenv("ANSWERS_AR_FAISS_INDEX")
    
    sentence_model_path = os.getenv("sentence_model_path")
    translation_model_path = os.getenv("translation_model_path")
    intent_classify_model_path = os.getenv("intent_classify_model_path")
    
    HF_TOKEN = os.getenv("HF_TOKEN")
    
    sentence_model_name = os.getenv("SENTENCE_MODEL_NAME")
    
    # Check if any required environment variable is None
    required_vars = [
        "TAGS_DATASET_PATH", 
        "ANSWERS_FR_DATASET_PATH", 
        "ANSWERS_AR_DATASET_PATH", 
        "TAGS_FAISS_INDEX", 
        "ANSWERS_FR_FAISS_INDEX", 
        "ANSWERS_AR_FAISS_INDEX", 
        "HF_TOKEN", 
        "sentence_model_path",
        "translation_model_path",
        "intent_classify_model_path"
        
    ]
    
    missing_vars = [var for var in required_vars if os.getenv(var) is None]
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")
        
except Exception as e:
    logger.error(f"An error occurred while loading environment variables: {e}")
    sys.exit(1)



try:
    #load models locally by executing init_models.sh
    nlp_pipeline_class = pipeline("text-classification", intent_classify_model_path) #classify intents
    model = SentenceTransformer(sentence_model_path, device="cpu") #sentence similarity
    translation = pipeline("translation", translation_model_path) #translation from arabic to french
    
    #load spacy french model
    spell = SpellChecker(language='fr')
    nlp = spacy.load("fr_core_news_md")
except Exception as e:
    logger.error(f"An error occurred during model loading: {e}")
    sys.exit(1)

try:

    dataset_tags = datasets.load_dataset("json", data_files=[tags_dataset_path], split="train")
    dataset_tags.load_faiss_index("embeddings", tags_faiss_index)
    dataset_answers_fr = datasets.load_dataset("json", data_files=[answers_fr_dataset_path], split="train")
    dataset_answers_fr.load_faiss_index("embeddings", answers_fr_faiss_index)
    dataset_answers_ar = datasets.load_dataset("json", data_files=[answers_ar_dataset_path], split="train")
    dataset_answers_ar.load_faiss_index("embeddings", answers_ar_faiss_index)
except Exception as e:
    logger.error(f"An error occurred while loading datasets: {e}")
    sys.exit(1)

def correct_spelling_french(text):
    try:
        corrected_words = []
        for word in text.split():
            correction = spell.correction(word)
            # Handle cases where no correction is found
            corrected_words.append(correction if correction is not None else word)
        corrected_text = " ".join(corrected_words)
        return corrected_text
    except Exception as e:
        logger.error(f"An error occurred in correct_spelling_french: {e}")
        return text  # Return the original text if there is an error
    return corrected_text


def correct_spelling_tokens(text):
    doc = nlp(text)
    corr = []
    for t in doc:
        corr.append(correct_spelling_french(t.text))

    return " ".join(corr)

def search(query, data, k, lang='fr'):
    try:
        if lang == 'fr':
            query = correct_spelling_tokens(query)
        query_embedding = model.encode(query)
        _, retrieved_examples = data.get_nearest_examples("embeddings", query_embedding, k=int(k))
        return retrieved_examples
    except Exception as e:
        logger.error(f"An error occurred during search: {e}")
        return None
        

def search_general_qst(query, data, k):
    try:
        query_embedding = model.encode(query)
        _, retrieved_examples = data.get_nearest_examples("embeddings", query_embedding, k=int(k))
        return retrieved_examples
    except Exception as e:
        logger.error(f"An error occurred during search: {e}")
        return None



def keep_only_matters(text):
    try:
        terms = nlp(text)
        # Use a list to collect the relevant tokens
        filtered_terms = [token.text for token in terms if token.pos_ not in ["VERB", "DET", "ADP", "PRON"]]
        # Join the filtered terms into a single string
        req = ' '.join(filtered_terms)
        return req
    except Exception as e:
        logger.error(f"An error occurred in keep_only_matters: {e}")
        return text  # Return the input text as a fallback

def create_dataset_general(data_file_path, faiss_index):
    try:
        dataset = datasets.load_dataset("json", data_files=[data_file_path], split="train")
        dataset.load_faiss_index("embeddings", faiss_index)
        return dataset
    except Exception as e:
        logger.error(f"An error occurred while creating dataset: {e}")
        return None
    
def general_qst_v1(text, token):
    try:
        dataset_path = os.getenv(f"{token}_DATASET_PATH")
        faiss_index_path = os.getenv(f"{token}_FAISS_INDEX")
        dataset = create_dataset_general(dataset_path, faiss_index_path)

        quest = search_general_qst(text, dataset, 1)['text']
        return quest[0]
    except Exception as e:
        logger.info(f"An error occured in general_qst : {e}")
        return f"Erreur lors de la réponse sur la documentation"


def general_v1(text, lang = 'fr'):
    try:
        if lang == 'fr':
            
            # res = keep_only_matters(text)
            quest = search(text, dataset_answers_fr, 1)['text']
            return quest[0]
        else:
            quest = search(text, dataset_answers_ar, 1)['text']
            return quest[0]
    except Exception as e:
        logger.info(f"An error occured in general_v1 : {e}")
        return f"Erreur lors de la réponse sur la documentation"


def chercher_data(mot, lang="fr", titles=None, links=None):
    if titles is None:
        titles = []
    if links is None:
        links = []
    try:
        response = requests.get(f"https://data.gov.ma/data/{lang}/dataset", params={'q': mot})
        if response.status_code != 200:
            return titles, links, response.url, 0
        soup = BeautifulSoup(response.text, features="lxml")
        nb_text = soup.find('h1').text
        nombre_don = re.findall(r'\d+', nb_text)
        media = soup.find('ul', class_='dataset-list list-unstyled')
        if media:
            thm = media.find_all('li', class_='dataset-item')
            for m in thm:
                link = m.find('a')['href']
                links.append('https://data.gov.ma' + link)
                title = m.find('h2').text.strip()
                titles.append(title)
        else:
            return titles, links, response.url, 0

        if not titles:
            return titles, links, response.url, 0

        return titles, links, response.url, nombre_don[0]
    except Exception as e:
        logger.error(f"An error occurred in chercher_data: {e}")
        return titles, links, "", 0  # Return empty values in case of an error


def format_reponse(data, lang="fr"):
    try:
        if lang == 'fr':
            if len(data[0]) == 1:
                response = f"Ici le lien vers la donnée correspondant au mot recherché : {data[-2]}\n"
                response += f"Voici le seul résultat trouvé :\n"
                response += f"Titre : {data[0][0]}\n"
                response += f"Lien : {data[1][0]}\n"
                return response
            else:
                response = f"Ici le lien vers toutes les {data[-1]} données correspondant au mot recherché : {data[-2]}\n"
                response += f"Voici un exemple parmi les résultats trouvés :\n"
                response += f"Titre : {data[0][-1]}\n"
                response += f"Lien : {data[1][-1]}\n"
                return response, data[-1]
        else:
            if len(data[0]) == 1:
                response = f"هنا الرابط للبيانات المطابقة للكلمة المطلوبة: {data[-2]}\n"
                response += f"إليك النتيجة الوحيدة التي تم العثور عليها:\n"
                response += f"العنوان: {data[0][0]}\n"
                response += f"الرابط: {data[1][0]}\n"
                return response
            else:
                response = f"هنا الرابط لجميع {data[-1]} البيانات المطابقة للكلمة المطلوبة: {data[-2]}\n"
                response += f"إليك مثال من بين النتائج التي تم العثور عليها:\n"
                response += f"العنوان: {data[0][-1]}\n"
                response += f"الرابط: {data[1][-1]}\n"
                return response, data[-1]
    except Exception as e:
        logger.error(f"An error occurred in format_reponse: {e}")
        return "Erreur dans le formatage de la réponse"



def req_dt(query, lang="fr"):
    try:
        rg = chercher_data(query, lang)
        if len(rg[0]):
            reponse_final = format_reponse(rg, lang)
            return reponse_final
        else:
            return query
    except Exception as e:
        logger.error(f"An error occurred in req_dt: {e}")
        return query
      
def request_data_v2(text, lang='fr'):
    try:
        reponses = []
        req = ""
        if lang == 'fr':
            doc = nlp(text)
            for token in doc:
                if token.pos_ not in ["VERB", "DET", "ADP", "PRON"]:
                    req += f"{token.text} "
            rs = search(req, dataset_tags, 2)
            if rs:
                dis = rs['text']
                for d in dis:
                    fre = req_dt(d)
                    reponses.append(fre)
            result_final = get_text_of_max_number(reponses)
            if result_final:
                return result_final
            return reponses
        else:
            rs = search(text, dataset_tags, 2)
            if rs:
                dis = rs['text']
                for d in dis:
                    fre = req_dt(d, 'ar')
                    reponses.append(fre)
            result_final = get_text_of_max_number(reponses)
            if result_final:
                return result_final
    except Exception as e:
        logger.error(f"An error occurred in request_data_v2: {e}")
        return "Désolé, un problème s'est produit"
    

def get_text_of_max_number(data):
    max_number = float('-inf')
    max_text = None
    for item in data:
        if isinstance(item, tuple) and len(item) > 1 and item[1].isdigit():
            number = int(item[1])
            if number > max_number:
                max_number = number
                max_text = item[0]
    return max_text

 
 
def classify_intent_v4(text, lang='fr'):
    try:
        executed_function = ""
        if lang == 'fr':
            text = correct_spelling_tokens(text)
            label = nlp_pipeline_class(text)[0]['label']
            if label == 'LABEL_0':
                response = general_v1(text)
                executed_function = "general_v1"
            else:
                response = request_data_v2(text)
                executed_function = "request_data"
            return {
                'output': response,
                'language': lang,
                'executed_function': executed_function,
                'input_text': text
            }
        else:
            trans = translation(text)[0]['translation_text']
            deci = correct_spelling_tokens(trans)
            label = nlp_pipeline_class(deci)[0]['label']
            if label == 'LABEL_0':
                response = general_v1(text, 'ar')
                executed_function = "general_v1"
            else:
                response = request_data_v2(text, 'ar')
                executed_function = "request_data"
            return {
                'output': response,
                'language': lang,
                'executed_function': executed_function,
                'input_text': text
            }
    except Exception as e:
        logger.error(f"An error occurred in classify_intent_v4: {e}")
        return {
            'output': "Erreur lors de la classification de l'intention",
            'language': lang,
            'executed_function': "error",
            'input_text': text
        }
        

