import datetime
import json
import time
from typing import Tuple

import arxiv
import requests
import schedule
from discordwebhook import Discord
from tqdm import tqdm


def InvProbQuery():
    """
    逆問題のクエリを作る関数

    
    """
    interested_categories = [
        "cond-mat.dis-nn",
        "cond-mat.mes-hall",
        "cond-mat.mtrl-sci",
        "cond-mat.other",
        "cond-mat.quant-gas",
        "cond-mat.soft",
        "cond-mat.stat-mech",
        "cond-mat.str-el",
        "cond-mat.supr-con",
        "hep-lat",
        "hep-ph",
        "hep-th",
        "physics.app-ph",
        "physics.atm-clus",
        "physics.atom-ph",
        "physics.chem-ph",
        "physics.comp-ph",
        "physics.data-an",
        "physics.flu-dyn",
        "physics.gen-ph",
        "physics.optics",
        "physics.plasm-ph",
        "physics.pop-ph",
    ]
    # %22は複数獄の
    query = "%28 "
    for cat in interested_categories:
        query += f"cat:'{cat}' OR "
    query = query[:-3] + "%29"
    query = (
        query
        + " AND all:'%22inverse problems%22' AND %28 all:'deep learning' OR all:'neural network' %29"
    )
    return query, interested_categories


# inverse problem
def PhysicsInverseProblem_papers(num_papers=100):
    """
    物理系の逆問題の論文を探す関数
    """
    query, int_cats = InvProbQuery()
    search_results = arxiv.Search(
        query=query, max_results=num_papers, sort_by=arxiv.SortCriterion.SubmittedDate
    )
    a = search_results.results()
    papers_dict = {}
    papers_set = set([])

    for _ in tqdm(range(num_papers)):

        try:
            paper = a.__next__()
        except StopIteration:
            continue

        if _ == 0:
            print("Inverse Problems:", paper.published, "->", end="")

        # test
        flg = 0
        for cat in paper.categories:
            if cat in int_cats:
                flg = 1
        assert flg == 1

        # 追加情報を入れる
        info = {"inverse-problem": 1}

        papers_set.add(paper.title)
        papers_dict[paper.title] = (
            paper.published,
            paper.title,
            paper.entry_id,
            info,
            paper.summary,
        )

    print(paper.published)
    return papers_set, papers_dict


# NNP系を探す
def NNP_papers(num_papers=100):
    """
    物理系の逆問題の論文を探す関数
    """
    query = (
        "all:'%22neural network potentials%22' OR all:'%22interatomic potentials%22'"
    )
    search_results = arxiv.Search(
        query=query, max_results=num_papers, sort_by=arxiv.SortCriterion.SubmittedDate
    )
    a = search_results.results()
    papers_dict = {}
    papers_set = set([])

    for _ in tqdm(range(num_papers)):
        try:
            paper = a.__next__()
        except StopIteration:
            continue

        if _ == 0:
            print("NNPs:", paper.published, "->", end="")

        # 追加情報を入れる
        info = {"inverse-problem": 0}
        if "inverse problem" in paper.summary:
            info["inverse-problem"] = 1

        papers_set.add(paper.title)
        papers_dict[paper.title] = (
            paper.published,
            paper.title,
            paper.entry_id,
            info,
            paper.summary,
        )
    print(paper.published)
    return papers_set, papers_dict


# PINN系を探す
def PINN_papers(num_papers=100):
    """
    物理系の逆問題の論文を探す関数
    """
    query = "all:'%22physics informed neural networks%22' OR all:'%22physics-informed neural networks%22'"
    # query = "all:'%22physics-informed neural networks%22'"
    search_results = arxiv.Search(
        query=query, max_results=num_papers, sort_by=arxiv.SortCriterion.SubmittedDate
    )
    a = search_results.results()
    papers_dict = {}
    papers_set = set([])

    for _ in tqdm(range(num_papers)):
        try:
            paper = a.__next__()
        except StopIteration:
            continue

        if _ == 0:
            print(" PINN:", paper.published, "->", end="")

        # 追加情報を入れる
        info = {"inverse-problem": 0}
        if "inverse problem" in paper.summary:
            info["inverse-problem"] = 1

        papers_set.add(paper.title)
        papers_dict[paper.title] = (
            paper.published,
            paper.title,
            paper.entry_id,
            info,
            paper.summary,
        )
    print(paper.published)
    return papers_set, papers_dict


def PickUpPapers(thres_weeks=2) -> Tuple[set, set, dict]:
    """直近の論文を取得するコード
    Args:
        thres_week(int) : 直近何週間分の論文を取得するか
    Outputs:
        must_papers(set): 優先度の高い論文リスト
        want_papers(set): 論文リスト
        result_papers_dict(dict): 取得した論文の情報を格納する辞書
    """
    PI_papers_set, PI_papers_dict = PINN_papers()
    NNP_papers_set, NNP_papers_dict = NNP_papers()
    Inv_papers_set, Inv_papers_dict = PhysicsInverseProblem_papers()

    result_paper_dict = {}
    must_papers = set([])
    want_papers = set([])
    for papers_dict in [PI_papers_dict, NNP_papers_dict, Inv_papers_dict]:
        for key in papers_dict.keys():
            p_time, title, entry_id, info, summary = papers_dict[key]
            time_delta = datetime.datetime.now() - p_time.replace(tzinfo=None)
            if time_delta.days < 7 * thres_weeks:
                result_paper_dict[key] = p_time, title, entry_id, info, summary
                want_papers.add(title)
                if info["inverse-problem"] == 1:
                    must_papers.add(title)

    print("must_papers:", len(must_papers))
    print("want_papers:", len(want_papers))

    return must_papers, want_papers, result_paper_dict


def DeepL_Translation(deepl_api_key, text, use_break: bool = True):
    """Translate the summary using the DeepL API"""
    # Remove inappropriate line breaks
    text = text.replace("。\n", "。")

    if use_break:
        # Include line breaks to prevent sentence skipping
        text = (
            text.replace("\n", "")
            .replace("i.e.", "IE")
            .replace("e.g.", "EG")
            .replace(". ", ".\n ")
        )

    # translation
    url = "https://api-free.deepl.com/v2/translate"
    params = {"auth_key": deepl_api_key, "text": text, "target_lang": "JA"}
    response = requests.post(url, data=params)
    translation = response.json()["translations"][0]["text"]

    if use_break:
        translation = translation.replace("。\n", "。")  # Remove line breaks
    return translation


def PaperInfo_DiscordPosting(
    discord: Discord,
    deepl_api_key: str,
    paper_title: str,
    paper_summary: str,
    p_url: str,
    must_check: bool = True,
):
    # 重複して取得するのを避ける
    previous_results = []
    try:
        with open("previous_results.json", "r") as f:
            previous_results = json.load(f)
    except FileNotFoundError:
        pass
    if p_url in previous_results:
        print("we already got ", paper_title)
        return

    while True:
        translation = DeepL_Translation(deepl_api_key, paper_summary, True)
        if translation is not None:
            break

    while True:
        title_ja = DeepL_Translation(deepl_api_key, paper_title, False)
        if title_ja is not None:
            break

    if must_check:
        check = "**<MUST CHECK!!!>   **"
    else:
        check = ""
    post_text = f"\n \n \n {check}**{paper_title}**\n **{title_ja}** \n {p_url} \n \n {translation}"
    discord.post(content=post_text)


def RSS_Feed(discord, deepl_api_key):
    # pick up new papers
    must_papers, want_papers, result_paper_dict = PickUpPapers(thres_weeks=2)

    # translate, post the papers to discod
    for paper_title in must_papers:
        _, title, url, _, paper_summary = result_paper_dict[paper_title]
        PaperInfo_DiscordPosting(
            discord, deepl_api_key, title, paper_summary, url, True
        )
    for paper_title in want_papers - must_papers:
        _, title, url, _, paper_summary = result_paper_dict[paper_title]
        PaperInfo_DiscordPosting(
            discord, deepl_api_key, title, paper_summary, url, False
        )

    # save paper entry_id picked up.
    with open("previous_results.json", "w") as f:
        json.dump([result_paper_dict[paper_title][2] for paper_title in want_papers], f)


def RSS_task():
    discord = Discord(url="your_url")
    deepl_api_key = "your_api_key"
    print("current time:", datetime.datetime.now())
    RSS_Feed(discord, deepl_api_key)


if __name__ == "__main__":
    RSS_task()
    schedule.every().monday.at("07:00").do(RSS_task)
    while True:
        schedule.run_pending()
        time.sleep(1)

