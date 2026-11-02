from datetime import datetime
import os
import csv
from bs4 import BeautifulSoup
import requests

BRANDS = [
    "Ansmann", "Blaser", "Fenix", "Feuerhand", "HyCell", 
    "INFORCE", "Ledlenser", "NEBO", "NEXTORCH", "P2P", 
    "Parforce Active", "Parforce Essential", "Petromax", "THERMACELL", "Walther"
]

def scrape_all_brands():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    
    all_products = []
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    for brand in BRANDS:
        url = f"https://www.frankonia.de/ausruestung/lampen/Artikel.html?lastSelected=f_s_marke&f_s_marke={brand.replace(' ', '+')}"
        print(f"正在抓取品牌: {brand} -> 链接: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=20)
            print(f"  -> 状态码: {response.status_code}")
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            # 尝试多种可能的商品卡片选择器
            product_cards = soup.select(".product-tile, .article-item, article, div[data-product-id], .list-item")
            print(f"  -> 找到商品卡片数量: {len(product_cards)}")
            
            for card in product_cards:
                title_elem = card.select_one(".title, .product-title, h2, h3, a.title, a.product-name")
                price_elem = card.select_one(".price, .product-price, span.price, .m-price")
                stock_elem = card.select_one(".availability, .stock-status, .lieferbarkeit")
                
                title = title_elem.get_text(strip=True) if title_elem else "未知型号"
                price = price_elem.get_text(strip=True) if price_elem else "未知价格"
                stock = stock_elem.get_text(strip=True) if stock_elem else "有货/未知"
                
                all_products.append({
                    "timestamp": current_time, "brand": brand,
                    "title": title, "price": price, "stock": stock
                })
        except Exception as e:
            print(f"  -> 抓取异常: {e}")
            
    # 即使没抓到商品，也创建一个空表或写入一条提示，防止后续 Git 报错
    filename = "all_brands_lampen_history.csv"
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["抓取时间", "品牌", "商品型号/名称", "价格", "库存状态"])
        
        if all_products:
            for item in data if 'data' in locals() else all_products:
                writer.writerow([item["timestamp"], item["brand"], item["title"], item["price"], item["stock"]])
            print(f"成功写入 {len(all_products)} 条记录。")
        else:
            # 写入一条空记录，确保文件一定存在，避免触发 128 报错
            writer.writerow([current_time, "System", "未抓取到商品（可能触发反爬或结构变更）", "-", "-"])
            print("未抓取到有效商品，已写入一条提示记录。")

if __name__ == "__main__":
    scrape_all_brands()
