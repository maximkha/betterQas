import json
from typing import List, Tuple
import requests
from difflib import SequenceMatcher
from sentence_transformers import SentenceTransformer, util
from bs4 import BeautifulSoup

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

StartKey = '"termIdToTermsMap":{'
EndKey = '},"termSort":'
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 OPR/73.0.3856.400"

def sequence_similarity(original: str, sample: str) -> float:
    return SequenceMatcher(lambda x: x in " \t?.", original, sample).ratio()

def rankQA(question: str, QAs: List[Tuple[str, str]], similarity_engine: str = "hybrid", cutoff=.5) -> List[Tuple[float, str, str]]:
    if len(QAs) == 0: return QAs

    if similarity_engine == "simple":
        ranked_QA = [(sequence_similarity(question, qa[0]), qa[0], qa[1]) for qa in QAs]

        return sorted(ranked_QA, key=lambda x:x[0], reverse=True)
    elif similarity_engine == "neural":
        target_embedding = model.encode(question)
        source_embeddings = model.encode([qa[0] for qa in QAs])

        similarities = list(util.pytorch_cos_sim(target_embedding, source_embeddings).flatten().numpy())

        return sorted([(similarities[i], QAs[i][0], QAs[i][1]) for i in range(len(QAs))], key=lambda x:x[0], reverse=True)
    elif similarity_engine == "hybrid":
        if not(0 <= cutoff <= 1):
            raise ValueError("Invalid cutoff!")

        # first do the simple fast method
        # no recursive call so that we don't waste time sorting the list!
        ranked_QA = [(sequence_similarity(question, qa[0]), qa[0], qa[1]) for qa in QAs]
        ranked_QA = list(filter(lambda x: x[0] > cutoff, ranked_QA))

        # then do the neural comparison
        # recursive call :)
        return rankQA(question, [(rqa[1], rqa[2]) for rqa in ranked_QA], similarity_engine="neural")
    else:
        raise ValueError("Invalid similarity engine!")

def GetQAUrl(quizlet_url: str) -> List[Tuple[str, str]]:
    try:
        req = requests.get(quizlet_url, data=None, headers={'User-Agent': USER_AGENT})
        page_text = req.text
        card_json = "{" + page_text[page_text.find(StartKey)+len(StartKey):page_text.find(EndKey)] + "}"
        card_data = json.loads(card_json)
        QA_tuples = [(card_data[id]["word"], card_data[id]["definition"]) for id in card_data.keys()]

        return QA_tuples
    except Exception:
        return []

def GetRelevantQuizlets(query: str) -> List[str]:
    urls = []
    req = requests.get(
        "https://www.bing.com/search", 
        data=None, 
        headers={
            'User-Agent': USER_AGENT,
        },
        params={
          'q': f"site:quizlet.com {query}",
      }
    )
    soup = BeautifulSoup(req.text, features="lxml")

    for el in soup.select("li.b_algo > div.b_title > h2 > a"):
        t_url = el.attrs["href"]
        if "https://quizlet.com" in t_url:
            urls.append(t_url)
    
    return urls

def QAs(question: str, num_quizlets_consider:int=5, similarity_engine:str="hybrid", cutoff:float=.5) -> List[Tuple[float, str, str]]:
    relevant_urls = GetRelevantQuizlets(question)
    if num_quizlets_consider != None: relevant_urls[:num_quizlets_consider]

    return rankQA(question, sum([GetQAUrl(url) for url in relevant_urls], start=[]), similarity_engine=similarity_engine, cutoff=cutoff)

def preprocess(question: str) -> List[str]:
    #this should split multi question queries and remove "this/that".
    raise NotImplementedError()