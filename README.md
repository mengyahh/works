# Understory（understory.mengyahh.com）

萌芽的作品與接案品牌網站（靜態網站，GitHub Pages，網域 DNS 在 Cloudflare、灰雲）。

```
index.html               首頁（產品介紹）：手寫的 HTML
about.html               關於頁：由 content/about.md 產生，不要直接改
portfolio/<名稱>/        作品集頁：由 content/portfolio/*.md 產生，不要直接改
content/                 用 Markdown 寫的內容（寫法見 content/README.md）
assets/site.css          關於頁與作品頁共用的樣式
assets/portfolio/        作品圖片、影片封面
assets/js/               放大檢視、YouTube 按了才載入
screenshots/             首頁 App 畫面截圖
scripts/                 build.py（Markdown → 網頁）、preview.py、photo.py
preview.bat / publish.bat  雙擊預覽／雙擊上線
```

日常：改 `content/*.md` → 雙擊 `preview.bat` 預覽 → 雙擊 `publish.bat` 上線。
只需要 Python 3；`scripts/photo.py` 另外需要 Pillow（`pip install pillow`）。

首頁的導覽列在 `index.html` 裡有一份，`scripts/build.py` 的 `nav_html()` 也有一份（關於頁、作品頁用），改導覽列時兩邊都要改。
