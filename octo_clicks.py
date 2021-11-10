import requests
import json
import datetime
import traceback
import concurrent.futures
import argparse
import timeit
import re
from playwright.sync_api import sync_playwright


USER_ID = "Sribuu007"
USER_PASS = "Testing007!"

def get_title(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        print(page.title())
        browser.close()
        
def block_aggressively(route):
    excluded_resource_types = ["image", "font"]
    if (route.request.resource_type in excluded_resource_types):
        route.abort()
    else:
        route.continue_()

def handle_response(response, text): 
    # the endpoint we are insterested in 
    if (text in response.url): 
        items = response.json()["data"] 
        [print(item["symbol"], item["lastPrice"]) for item in items] 

def take_screenshot(url, output):
    with sync_playwright() as p:
        browser = p.firefox.launch(slow_mo=50, headless=False)
        page = browser.new_page(record_har_path="playwright_test.har")
        page.on("request", lambda request: print(">>", request.method, request.url, request.resource_type))
        page.on("response", lambda response: print("<<", response.status, response.url))
        # page.route("**/*", block_aggressively)
        page.set_default_timeout(100000)
        page.goto(url)
        # print(page.evaluate("JSON.stringify(window.performance)")) # Browser's Performance API
        page.screenshot(path=output)
        page.pause()
        page.close()
        
def shopee_fs(url):
    with sync_playwright() as p:
        browser = p.firefox.launch(slow_mo=50, headless=False)
        context = browser.new_context(storage_state="state.json")
        page = context.new_page()
        page.on("request", lambda request: print(">>", request.method, request.url, request.resource_type))
        page.on("response", lambda response: print("<<", response.status, response.url))
        # page.route("**/*", block_aggressively)
        page.set_default_timeout(100000)
        page.goto(url)

        # Click text=Log inLog in dengan QR >> svg
        page.click("text=Log inLog in dengan QR >> svg")
        # assert page.url == "https://shopee.co.id/buyer/login/qr"   
             
        page.pause()
        
        try:
            # Click #modal path
            page.click("#modal path", timeout=20000) 
        except:
            pass
        
        storage = context.storage_state(path="state.json")
        
        # Click text=Lihat Semua
        page.click("text=Lihat Semua")
        # assert page.url == "https://shopee.co.id/flash_sale?promotionId=2027090138"       
        
        
        # Click text=00:00
        page.click("text=00:00")
        # assert page.url == "https://shopee.co.id/flash_sale?promotionId=2027091985"
        
        # Click text=Apple iPhone 12 128GB Blue
        page.click("text=Apple iPhone 12 128GB Blue")
        # assert page.url == "https://shopee.co.id/Apple-iPhone-12-128GB-Blue-i.255563049.7467544018"
        
        # page.click("text=Penjepit Kemasan Snack")
        # page.click("text=Biru")
      
        # Click text=beli sekarang
        # with page.expect_navigation(url="https://shopee.co.id/cart?itemKeys=6757688356.31414558904.&shopId=18156457")
        while True:
            try:
                with page.expect_navigation(timeout=2000):
                    page.click("text=beli sekarang", timeout=3000)
                break
            except Exception as a:
                page.reload()
                
                
        # Click button:has-text("checkout")
        # with page.expect_navigation(url="https://shopee.co.id/checkout"):
        with page.expect_navigation():
            page.click("button:has-text(\"checkout\")")

        page.wait_for_timeout(5000)

        # Click :nth-match(:text("ubah"), 2)
        page.click(":nth-match(:text(\"ubah\"), 2)")
            
        # Click div[role="radio"]:has-text("Pengiriman setiap saatDisarankan untuk alamat rumah")
        page.click("div[role=\"radio\"]:has-text(\"Pengiriman setiap saatDisarankan untuk alamat rumah\")") 

        # Click button:has-text("OK")
        # with page.expect_navigation(url="https://shopee.co.id/checkout/?state=H8KLCAAAAAAAAAPChVXDicKOwqMwEMO9F8OOOUDCgGzCvzJqWQYXwonDlcOGZmzCk0nDlMOKwr9PwpUXQsKiwokmwpfDhsK1wr56wrXDtE%2FDgcO6w4EXwqdfVcO1wrUpwrwcw4F5Pk7DhcKpw5rDlcK7wrZtD03CuynDnMOFTMOGCsKwDg1%2Fw4LCszjDhcK%2FUsKgw6nCoWp3TcK7f2wKw6lhwoxGw7RFw4rDncK%2Bw53Drw7Ch8K6w51tworDkQhQJMKswqvCpmoww7jCsWw2w4XDr8KZay%2FDvR0DbQouBDPCmgnDoMKKwpFlwrPDnx3Dq0PCicKRHUs6N3fCjMKiF8KnwoErBzEpO1szT8OBwqVowpvCpsKsdsObw7pYN1VbbsK3w7vDsljCoMKVdsKzw6XCugfDgsO3w7XDuMKiwrLDpDRJfQ5eVcKQwoDCgsOewoNgE8K%2Fwo%2FCoD3Dqy9ca1BMcMOPwqlkM3nCiRDCpB4MJsOCwqgebj49w7XCrBRSMFkzwppgwpXCnWYHwqw3wph%2FQTxYAMK2wqTCv8KawrnCv8KATWF%2BPmkRZMO5w4nCtUdmIyAhHcOvFMKWYMKBO8KjI8KsTcORUR3DjxTCoztHcwXDnGo2Ggssw4keVMKDw6J%2BMHbDjMOxA2VxDsOeRMO4w5l%2FwrPCtcKCIW%2FCmcOnVC7Cn8K9YXzCmsOUw73DhTLDqTHDn8Ogwq4scsKfw5lNw6EFXGUPC8Osw7wUwqnDlsO4HMKQCcKwwpPClcOawqfCphh9FsKzZsKdw6LDvXdnblHDmsONd0TClzvCm0JSwrVRwpFzwrgLRzIQw7BgJWjDocKew4nCpUNew67CqDrCnxUsw4XCgSbCvsOfwqVcKcOzwofCosKEcMOPSgNfZsO2DEYuVcOgG8KFw5x6w6bDrxPChA7Dt0oGwoDCscOfwp7DnxYEw6FbJCdhw43DtMKcw6BkEcOBwogFwobDpmPCmsKLw6liNDA9wo8dER8iLMOew6vDncK%2Bw6vCvjh5O0PDpgXCt8OOwoJzw4s0wqc3w6E4w6zDq8ODdsObNMKbLHwWQVDCkzBnw4vCu8Klw4xZOi%2FDu8K8XCFSWcOWw68LwrnCujtYwp%2FCgFvDmMOcw7JraVjCvypnwr3CuxYGwrAWwr%2FDqMOaXMOBYsOLw7DCrsKxwrzCu8KRw5fDv8KaO2ViE8OCXmPDlsKIZMKewpDCiGUiw5cdw4UBw4Rhw4w0wo1gwqk%2BHBrCoMKLw6XCjcOnw5jDrsKKfiXDvWhKUUTDs0gtwqMrWi%2FCqsKFwojCp8OnflvClsKfwrTCrMKDwoE2GMKTw7VmwqYtw7jCl3XDlsKuwoLCpkYtGMOSG8KpHgNZcR5nw6fDjcOISMOxw6IZDh0dwp7CsMOaEkTCvjU9wpIpw7F2ckvDrMKma8KYwpXDlFNIw7cQb8KUABjCn8Kew7HCiGN7V8KlwpTDlG8tcMOFw6jCn8KCW2nDkmULw4PDoG%2FCmg0QS1guw70rw57Cp8O4wo3Crk9mw7%2FDll%2FDucKLw6DDscO4C8OswpXDrBVDBwAA"):
        page.click("button:has-text(\"OK\")")
            
        page.click("text=Buat Pesanan")

        page.pause()
        
if __name__ == '__main__':
    # get_title("http://whatsmyuseragent.org/")
    # take_screenshot("https://shopee.co.id/buyer/login/otp", "shopee.png")
    shopee_fs("https://shopee.co.id/buyer/login")
