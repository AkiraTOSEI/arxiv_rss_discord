# arxiv_rss_discord

arxiv api を使って所望の最新論文を取得し、discordに投稿するスクリプト

## 事前準備

### Deep L API の API key と Discord Webhook 

- Deep L API の取得方法: [https://www.deepl.com/ja/pro-api?cta=header-pro-api/](https://www.deepl.com/ja/pro-api?cta=header-pro-api/)
- Discord Webhook: [https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)

取得したら、以下の `RSS_task` 関数の中に書き込む

``` python
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
```        


必要なライブラリのインストール

 ```
 pip install arxiv schedule discordwebhook 
 ```

## arxiv api

arxiv api を使って検索するときは、以下の特殊文字を使う必要がある。詳細は、[arxiv API User's Manual](https://info.arxiv.org/help/api/user-manual.html) を参照。

- 熟語で検索したい場合は、`%22` で囲む。
  - 例) "deep learning" ->  "%22deep learning%22"
- 条件文のかっこ書きは、、"("として`%27`、")"として`%28`を使う
  - 例) cond-mat.mtrl-sciとcond-mat.softの 2 つのカテゴリにおいて、deep learningの研究を調べたい
  - `query = "%28 cat:'cond-mat.mtrl-sci' OR cat:'cond-mat.soft' %29 AND all:'%22deep learning%22'"`
 


