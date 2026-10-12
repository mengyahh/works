# Understory（understory.mengyahh.com）

萌芽的作品與接案品牌網站（靜態網站，GitHub Pages，網域 DNS 在 Cloudflare、灰雲）。

```
index.html               首頁：由 content/index.md 產生，不要直接改
en/  ja/                 英文版、日文版：由 content/en/、content/ja/ 產生，不要直接改
about.html               關於頁：由 content/about.md 產生，不要直接改
portfolio/<名稱>/        作品集頁：由 content/portfolio/*.md 產生，不要直接改
products/<名稱>/         產品頁：由 content/products/*.md 產生，不要直接改
content/                 用 Markdown 寫的內容（寫法見 content/README.md）
assets/site.css          各頁共用的樣式（首頁另有 assets/home.css）
assets/portfolio/        作品圖片、影片封面
assets/js/               放大檢視、YouTube 按了才載入
screenshots/             作品（自由工作者套件）的 App 畫面截圖
scripts/                 build.py（Markdown → 網頁）、preview.py、photo.py
preview.bat / publish.bat  雙擊預覽／雙擊上線
```

日常：改 `content/*.md` → 雙擊 `preview.bat` 預覽 → 雙擊 `publish.bat` 上線。
只需要 Python 3；`scripts/photo.py` 另外需要 Pillow（`pip install pillow`）。

導覽列與網站框架文字（按鈕、返回連結）在 `scripts/build.py` 的 `nav_html()` 與 `STRINGS`，所有頁面共用。服務與市場策略、語言版本的更新順序見 `CLAUDE.md`。
