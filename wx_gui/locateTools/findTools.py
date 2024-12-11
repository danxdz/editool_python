import json
import os
import asyncio
import wx
from playwright.async_api import async_playwright

from locateTools.parse_data import parse_tool_data

async def read_keys_from_file(file_path):
    keys = {}
    try:
        #get local path
        path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(path, file_path)
        with open(file_path, "r") as file:
            for line in file:
                code, description = line.strip().split(",")
                keys[code] = description
    except Exception as e:
        print(f"Error reading parameter file: {e}")
    return keys

async def search_tool(reference, file_path):
    keys = await read_keys_from_file(file_path)

    app = wx.App(False)
    progress_dialog = wx.ProgressDialog("Tool Search Progress", "Initializing...", maximum=100, style=wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)

    async with async_playwright() as p:
        try:
            progress_dialog.Update(10, "Launching browser...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            if type(reference) == str:
                reference = [reference]

            for ref in reference:
                progress_dialog.Update(20, f"Searching for {ref}...")
                google_url = f"https://www.google.com/search?q={ref}"
                await page.goto(google_url, timeout=10000)
                await asyncio.sleep(2)

                progress_dialog.Update(30, "Locating manufacturer link...")
                links = await page.query_selector_all("a")
                sandvik_link = None
                for link in links:
                    href = await link.get_attribute("href")
                    data = {}
                    data["reference"] = ref
                    if href:
                        if ("seco" in href):
                            seco_link = href
                            data["mfr"] = "Seco"
                            await page.goto(seco_link, timeout=10000)
                            await asyncio.sleep(2)
                            break
                        elif ("sandvik" in href):
                            ref_serial = ref.replace(" ", "%20")
                            sandvik_link = f"https://www.sandvik.coromant.com/fr-fr/search?q={ref_serial}&origin=top%20search%20bar"
                            await page.goto(sandvik_link, timeout=10000)
                            await page.wait_for_load_state("domcontentloaded")
                            accept_cookies = await page.query_selector("button#onetrust-accept-btn-handler")
                            if accept_cookies:
                                await accept_cookies.click()
                            await asyncio.sleep(5)
                            bracket = await page.query_selector("i.icon-bracket-down")
                            if bracket:
                                await bracket.click()
                            await asyncio.sleep(2)
                            break

                if sandvik_link:
                    progress_dialog.Update(50, "Extracting data from Sandvik...")
                    
                    data["mfr"] = "Sandvik"
                    try:
                        name = await page.query_selector("h1.product-title")
                        data["name"] = await name.inner_text()
                    except Exception:
                        data["name"] = "Name not found"
                    try:
                        image = await page.query_selector("img.cursor-pointer")
                        image_url = await image.get_attribute("src")
                        data["image_url"] = image_url
                    except Exception:
                        data["image_url"] = "Image not found"
                    rows = await page.query_selector_all("div.row, div.col-12")
                    for row in rows:
                        try:
                            key_element = await row.query_selector("span.pe-1")
                            iso_code_element = await row.query_selector("span:not(.pe-1)")
                            value_element = await row.query_selector(".fw-bold, .cursor-alias, .material-box-v5")
                            if key_element and iso_code_element and value_element:
                                key_text = await iso_code_element.inner_text()
                                key = key_text[key_text.find("(")+1:key_text.find(")")]
                                value = await value_element.inner_text()
                                if key.strip():
                                    data[key.strip()] = value.strip()
                        except Exception as e:
                            print(f"Row parsing error: {e}")
                else:
                    progress_dialog.Update(50, "Extracting data from other sources...")
                   
                    try:
                        name = await page.query_selector("span.ps-designation")
                        grade = await page.query_selector("h2 a span.ps-grade")
                        if name and grade:
                            data["name"] = (await name.inner_text()).strip() + " " + (await grade.inner_text()).strip()
                        else:
                            if name:
                                data["name"] = await name.inner_text()
                            else:
                                data["name"] = "Name not found"
                    except Exception:
                        data["name"] = "Name not found"
                    try:
                        image = await page.query_selector("div.illustration-container img")
                        image_url = await image.get_attribute("src")
                        data["image_url"] = image_url
                    except Exception:
                        data["image_url"] = "Image not found"
                    try:
                        rows = await page.query_selector_all("table.product-attribute-table tbody tr")
                        for row in rows:
                            try:
                                key_element = await row.query_selector("td:nth-child(1)")
                                description_element = await row.query_selector("td:nth-child(2)")
                                value_element = await row.query_selector("td:nth-child(3)")
                                key = await key_element.inner_text()
                                description = await description_element.inner_text()
                                value = await value_element.inner_text()
                                data[key] = {"description": description, "value": value}
                            except Exception as e:
                                print(f"Row parsing error: {e}")
                    except Exception as e:
                        print(f"Error extracting table data: {e}")

                progress_dialog.Update(70, "Processing data...")
                print("\nTool Data:")
                for key, value in data.items():
                    print(f"{key}: {value}")

                '''if "image_url" in data and data["image_url"] != "Image not found":
                    try:
                        response = await page.goto(data["image_url"])
                        image_data = await response.body()
                        with open(f"{data['name']}.png", "wb") as file:
                            file.write(image_data)
                    except Exception as e:
                        print(f"Error saving image: {e}")'''

                progress_dialog.Update(90, "Saving data...")
                try:
                    with open(f"{data['name']}_data.json", "w") as json_file:
                        json.dump(data, json_file, indent=4)
                    tool = parse_tool_data(f"{data['name']}_data.json")
                    print(tool.getAttributes())
                    # remove the json file after parsing
                    os.remove(f"{data['name']}_data.json")
                except Exception as e:
                    print(f"Error saving tool data to JSON: {e}")

            await browser.close()
            progress_dialog.Update(100, "Completed")
            progress_dialog.Destroy()
            return tool

        except Exception as e:
            print(f"Error: {e}")
            await browser.close()
            progress_dialog.Destroy()

# Example usage
# asyncio.run(search_tool("1B230-1400-XA 1630", "keys.txt"))
# Example usage
#1B230-1400-XA 1630
#1K212-0500-XA 1730
#2B284-0500-TA T2CH
#CCET 06 02 01-UM 1105
#RCGX 08 03 M0-AL H10
#930-C6-HD-20-084
#LPHT060310TR-M06 MS2050
#JS754030F1R020.0Z4-HXT
#S4531-060D2C.0Z3 AXT
#JS754030F1R020.0Z4-HXT
