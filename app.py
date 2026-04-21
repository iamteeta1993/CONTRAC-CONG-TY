import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime

# Cấu hình file dữ liệu của bạn
DATA_FILE = "data_congty.xlsx"
COLUMNS = ["Tên Công Ty", "Mã Số Thuế", "Chủ Doanh Nghiệp", "Địa Chỉ", "Liên Hệ", "Ghi Chú", "Zalo", "Cập Nhật Cuối"]

def scrape_trang_vang_by_keyword(keyword="khuôn mẫu", max_pages=5):
    all_results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Format từ khóa để đưa vào URL
    search_keyword = keyword.replace(" ", "+")
    
    for page in range(1, max_pages + 1):
        print(f"--- Đang quét trang {page} cho từ khóa '{keyword}' ---")
        url = f"https://trangvangvietnam.com/search.asp?key={search_keyword}&page={page}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                break
                
            soup = BeautifulSoup(response.content, "html.parser")
            listings = soup.find_all('div', class_='boxlisting')
            
            if not listings:
                print("Hết dữ liệu.")
                break
                
            for item in listings:
                name = item.find('h2').get_text(strip=True) if item.find('h2') else ""
                # Chỉ lấy nếu tên công ty hoặc mô tả có chữ "khuôn mẫu" (để lọc chính xác)
                if keyword.lower() in name.lower() or keyword.lower() in item.get_text().lower():
                    address = item.find('div', class_='addresslisting').get_text(strip=True) if item.find('div', class_='addresslisting') else ""
                    phone = item.find('div', class_='phonelisting').get_text(strip=True) if item.find('div', class_='phonelisting') else ""
                    
                    # Làm sạch số điện thoại cho Zalo
                    clean_p = "".join(filter(str.isdigit, phone))
                    zalo_link = f"https://zalo.me/{clean_p[:10]}" if clean_p else ""
                    
                    all_results.append({
                        "Tên Công Ty": name,
                        "Mã Số Thuế": "", # Thường phải vào chi tiết mới thấy
                        "Chủ Doanh Nghiệp": "",
                        "Địa Chỉ": address,
                        "Liên Hệ": phone,
                        "Ghi Chú": f"Nguồn: TrangVang - Từ khóa: {keyword}",
                        "Zalo": zalo_link,
                        "Cập Nhật Cuối": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
            
            # Nghỉ 1 chút để tránh bị web chặn (Anti-bot)
            time.sleep(2)
            
        except Exception as e:
            print(f"Lỗi tại trang {page}: {e}")
            break
            
    return all_results

# Thực hiện quét
data = scrape_trang_vang_by_keyword("khuôn mẫu", max_pages=10)

# Cập nhật vào file Excel hiện tại của bạn
if data:
    new_df = pd.DataFrame(data)
    if os.path.exists(DATA_FILE):
        old_df = pd.read_excel(DATA_FILE)
        final_df = pd.concat([old_df, new_df], ignore_index=True).drop_duplicates(subset=['Tên Công Ty'])
    else:
        final_df = new_df
        
    final_df.to_excel(DATA_FILE, index=False)
    print(f"✅ Đã thu thập thành công {len(data)} công ty và lưu vào {DATA_FILE}")
else:
    print("❌ Không tìm thấy dữ liệu mới.")
