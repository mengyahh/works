# 用 Markdown 改 Understory 的內容

```
content/about.md                      關於頁（about.html）
content/portfolio/daodu-hexi.md       作品集頁（島讀河溪）：一個 .md 檔 ＝ 一個作品頁
content/portfolio/lecheng.md          作品集頁（樂城生活節）
content/portfolio/_專項（暫不顯示）.md   檔名開頭是 _ 的不會發布（先收起來的內容放這裡）
content/products/freelance.md         產品頁：自由工作者管理大師
content/products/poultry.md           產品頁：白肉雞養殖紀錄系統
```

首頁（`index.html`）還是手寫的 HTML，沒有改成 Markdown；它只放產品的簡短介紹，完整內容在產品頁。

## 日常流程

1. 改 `.md` 檔（記事本、VS Code 都能開）
2. 雙擊 `preview.bat`，瀏覽器開 http://localhost:8000，存檔後按 F5 就看得到
3. 滿意了，雙擊 `publish.bat`，確認後上傳到 understory.mengyahh.com

（也可以用 `python scripts/preview.py`、`python publish.py`。）

## 關於頁 `content/about.md`

開頭是設定，接著是一段一段的「區塊」，每個區塊用 `::: 類型 小標` 開頭、單獨一行 `:::` 結尾。**區塊的順序就是頁面的順序**，可以搬動。

```
---
title: 關於 | Understory                ← 瀏覽器分頁標題
description: 搜尋結果下面的那一兩句簡介
email: mengyahh@gmail.com               ← 聯絡區塊的 email
---
```

| 區塊 | 寫法重點 |
|---|---|
| `::: hero` | 第一行是小字標題；`# ` 開頭是大標題，`**粗體**` 的部分會變成綠色強調；後面的文字是簡介 |
| `::: skills 能力` | `## ` 大標、下面一段是簡介；每個 `### 名稱` 是一張卡片（文字一段、`> ` 開頭是灰色備註、`- 標籤：內容` 條列會排成兩欄）；單獨一行 `---` 之後的那一段是「合作單位…」；`#### 常用工具` 底下 `- 類別：A、B、C` 會變成一個個小標籤 |
| `::: projects 專案類型` | `## ` 大標、簡介；每個 `### 專案名稱` 是一列，**同一行最後面可以放連結** `[名稱](網址)`，下一行用「、」隔開的是標籤；`---` 之後那段是結語 |
| `::: process 合作方式` | 每個 `### 步驟名稱` 後面一段說明，依序自動編號；`---` 之後那段是補充 |
| `::: why 為什麼找我` | `- **標題**：說明` |
| `::: name Understory` | 一段文字 |
| `::: contact` | `## ` 標題、一段說明，`- [文字](網址)` 是下面的連結 |

專案連結的網址如果是 `http` 開頭，會自動加上「↗」（另開網站）；如果是站內的（例如 `portfolio/lecheng/`），會加上「→」。

## 作品頁 `content/portfolio/<網址名稱>.md`

檔名就是網址：`lecheng.md` → `understory.mengyahh.com/portfolio/lecheng/`（檔名請用英文、數字、`-`）。

```
---
title: 【樂城生活節】藝文市集             ← 頁面大標題
description: （選填）搜尋結果的簡介
---

## 社群圖片製作                          ← 每個 ## 是一列：左邊是說明、右邊是作品
這一列的說明文字（可以有好幾段）

⮕ [文字](https://網址) 也可以放連結

![](portfolio/11.webp)                  ← 作品圖片（一行一張）
![](portfolio/12.webp "圖片說明")       ← 加引號＝圖片下方的說明文字
[![](portfolio/24.webp "說明")](https://網址)   ← 圖片本身連到外部網址（不放大，另開頁面）
![](youtube:qbjOpJ7ApBo "說明")         ← YouTube 影片（按了播放才載入）
```

- 圖片放在 `assets/portfolio/`，小圖用 `xx-t.webp`；影片的封面圖是 `assets/portfolio/yt-影片代碼.webp`。
- 加新圖片：`python scripts/photo.py D:\照片\a.jpg`（需要 `pip install pillow`），它會縮小、去掉 EXIF（含 GPS 位置）、編號，並印出要貼進去的那幾行。
- 新增一個作品頁：複製一個現有的 `.md` 改內容，檔名取新的網址名稱；記得到 `about.md` 的專案列表加上連結。
- 想暫時不發布：檔名前面加 `_`。

## 產品頁 `content/products/<網址名稱>.md`

每個產品一頁：`freelance.md` → `understory.mengyahh.com/products/freelance/`。首頁只放產品的簡短說明（小卡片），完整介紹在這裡。

```
---
title: 給自由工作者的生活工作管理大師
eyebrow: Product 01 · 開放試用中       ← 標題上方的小字（產品編號 · 狀態）
description: 搜尋結果的簡介
---

開頭一兩段介紹文字（不需要區塊符號）。

::: features                       ← 功能卡片：每個 ### 是一張（標題＋下一段說明）
### 接案追蹤
記錄合作單位、專案、費用方式。
:::

::: screens App 實際畫面             ← 畫面截圖：圖片一行一張，引號裡是圖說；--- 之後那段是備註
![畫面說明](screenshots/xxx.png "圖說")
---
畫面中的資料皆為測試資料。
:::

::: note                            ← 灰色小字的補充說明
:::

::: callout open                    ← 「目前狀態」方塊（open ＝ 邊框用強調色；不寫就是一般樣式）
**目前狀態：**……

- [按鈕文字 →](https://網址)          ← 列表會變成按鈕，第一個是主要按鈕
:::
```

新增產品：複製一個 `.md` 改內容，再到首頁 `index.html` 的「AppSheet 管理系統」區塊加一張小卡片，並在導覽列的下拉選單加上連結（導覽列在 `index.html` 和 `scripts/build.py` 各有一份）。

## 出錯時

`preview.py` / `build.py` 會直接說是哪個檔案、哪裡有問題（例如找不到圖片、區塊類型打錯）。
