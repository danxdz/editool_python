import json
import os
import asyncio
import wx
import re
import logging

import aiohttp
import asyncio
from playwright.async_api import async_playwright

from locateTools.parse_data import parse_tool_data
from importTools.import_xml_wx import select_xml_type



async def send_post_request( reference_code):
    url = "https://dixipolytool.ch/shop/fr/family/search"
    payload = {
        "_token": "GVeVJ8uPuYSaMbSEiDl8_Lt1ZT5R8RMrHHtf_XjTHVo",
        "search_term": reference_code
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    }
    cookies = {
        "hl": "fr",
        "PHPSESSID": "tetest709v9j8oac25kqp1855u",
        "isLogged": "false"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers, cookies=cookies) as response:
            if response.status == 200:
                text = await response.text()
                print("Response received successfully!")
                #print(text)  # Optionally process the response
                #search the div class product-list

                '''<a href="/shop/fr/family/567" class="card card-product filterable-card" data-cut-direction="" data-mat="mat_acier_pb / mat_acier_faiblement_allie / mat_acier_fortement_allie / mat_acier_inoxydable / mat_fontes / mat_super_alliages / mat_titane / mat_alliages_cuivres / mat_alliages_cuivres_difficiles / mat_alu / mat_gold / mat_silver" data-matters="matter_tialn" data-d1="2.99;16.01" data-l1="27.99;83.01" data-d="5.99;16.01" data-l="65.99;133.01" data-z="1;3">
                <div class="card-image">
                    <img src="/shop/images/img_60e84bd5317211.42283292.jpg" class="card-img-top">
                </div>
                <div class="card-body">
                    <h5 class="card-title">DIXI 1345-5D-HH</h5>
                    <h6 class="card-subtitle mb-2 text-muted"></h6>
                </div>
                </a>'''
                #get all numbers in the href just after /family/ and before "
                num = re.search(r'<a href="/shop/fr/family/(.*?)"', text)
    
                if num:
                    link = "https://dixipolytool.ch/shop/fr/family/" + num.group(1)
                    print(f"Found link: {link}")
                    return link
                else:
                    print("Link not found")

async def download_step_file(reference_code, url):
    # Construct the URL
    print(f"Attempting to download from URL: {url}")

    # Headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    # Read content and save the file
                    content = await response.read()
                    file_path = f"{reference_code}.step"
                    with open(file_path, "wb") as file:
                        file.write(content)
                    print(f"STEP file saved as {file_path}")
                else:
                    print(f"Failed to download STEP file. HTTP Status: {response.status}")
        except aiohttp.ClientError as e:
            print(f"Client error occurred: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

async def download_xml_file(reference_code, url):
    # Construct the URL
    print(f"Attempting to download from URL: {url}")

    # Headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    # Async HTTP session and request
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    # Read content and save the file
                    content = await response.read()
                    file_path = f"{reference_code}.xml"
                    with open(file_path, "wb") as file:
                        file.write(content)
                    print(f"XML file saved as {file_path}")
                    return file_path
                else:
                    print(f"Failed to download XML file. HTTP Status: {response.status}")
        except aiohttp.ClientError as e:
            print(f"Client error occurred: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


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

async def search_tool(ref, file_path , toolData):
    keys = await read_keys_from_file(file_path)

    # app = wx.App(False) 

    try:
        tool = await browser_search_tool(ref, keys)
        #print(tool.getAttributes())
        return tool
        
    except Exception as e:        
        logging.error(f"Error: {e}")
       

    

async def browser_search_tool(reference, keys):
     async with async_playwright() as p:
            try:
                progress_dialog = wx.ProgressDialog("Tool Search Progress", "Initializing...", maximum=100, style=wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
                progress_dialog.Update(10, "Launching browser...")
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()
                if type(reference) == str:
                    reference = [reference]
                
                xml_file_path = None

                for ref in reference:
                    progress_dialog.Update(20, f"Searching for {ref}...")
                    google_url = f"https://www.google.com/search?q={ref}"
                    await page.goto(google_url, timeout=10000)
                    await asyncio.sleep(2)

                    progress_dialog.Update(30, "Locating manufacturer...")
                    links = await page.query_selector_all("a")
                    sandvik_link = None
                    seco_link = None
                    valid_mfr = False
                    for link in links:
                        href = await link.get_attribute("href")
                        
                        if href:
                            if "google" in href:
                                continue
                            data = {}
                            data["reference"] = ref
                            if href:
                                if ("ceratizit" in href):
                                    valid_mfr = True
                                    data["mfr"] = "Ceratizit"
                                    progress_dialog.Update(50, "Extracting data from Ceratizit...")
                                    ref_serial = ref
                                    mfr_link = f"https://cuttingtools.ceratizit.com/fr/fr/products/{ref_serial}.html"
                                    mfr_link = str(mfr_link)
                                    await page.goto(mfr_link, timeout=10000)
                                    await page.wait_for_load_state("domcontentloaded")
                                    await asyncio.sleep(2)
                                    try:
                                        #<span data-pheader="articleNo">50651101</span>
                                        name = await page.query_selector("span[data-pheader=articleNo]")
                                        data["name"] = await name.inner_text()
                                    except Exception:
                                        data["name"] = "Name not found"
                                    try:
                                        #<div class="wnt-image" data-dynamic-image="" data-src="https://cdn.plansee-group.com/is/image/planseemedia/pic_mat_mil_50651-kurz_all_pim" data-alt="Fraises toriques" data-alpha="true" data-png-alpha="false" data-fit="false"><img src="https://cdn.plansee-group.com/is/image/planseemedia/pic_mat_mil_50651-kurz_all_pim?dynamic=true&amp;hei=276&amp;fmt=webp-alpha" alt="Fraises toriques"></div>
                                        image = await page.query_selector("div.wnt-image data-dynamic-image img")
                                        image_url = await image.get_attribute("src")
                                        data["image_url"] = image_url
                                    except Exception:
                                        data["image_url"] = "Image not found"
                                    
                                    # Extract data from the <dl> tag
                                    rows = await page.query_selector_all("dl.wnt-definitionlist dt, dl.wnt-definitionlist dd")
                                    for i in range(0, len(rows), 2):
                                        try:
                                            key_element_text = await rows[i].inner_text()
                                            value_element_text = await rows[i+1].inner_text()
                                            
                                            # Extract the code from the key text
                                            if "/" in key_element_text:
                                                key_parts = key_element_text.split('/')
                                                if len(key_parts) > 1:
                                                    code_part = key_parts[1].strip()
                                                    # Remove any additional annotations (e.g., 'f8', '±0,05', etc.)
                                                    code = code_part.split()[0]
                                                else:
                                                    code = key_element_text.strip()
                                            else:
                                                code = key_element_text.strip()
                                            
                                            value = value_element_text.strip()
                                            if code:
                                                data[code] = value
                                        except Exception as e:
                                            print(f"Row parsing error: {e}")

                                    # Compare extracted data with tool_parameters
                                    try:
                                        for code, description in keys.items():
                                            if code in data:
                                                # Map the description to the value
                                                data[code] = data.pop(code)
                                            else:
                                                #print(f"Key {code} not found in extracted data")
                                                pass
                                    except Exception as e:
                                        print(f"Error comparing extracted data with tool_parameters: {e}")
                
                                    #need to find this element and extract the data
                                    #<div class="wnt-pheader__title-line">AluLine – Fraises deux tailles rayonnées</div>
                                    try:
                                        comment = await page.query_selector("div.wnt-pheader__title-line")
                                        data["comment"] = await comment.inner_text()
                                        #make comment all lower case
                                        data["comment"] = data["comment"].lower()
                                        #take off all the special characters
                                        data["comment"] = re.sub(r'[^\w\s]', '', data["comment"])

                                        #check we find the tool type in the text
                                        if "rayon" in data["comment"]:
                                            data["toolType"] = "1"
                                        elif ("hémisphériques" in data["comment"]) or ("hemispheriques" in data["comment"]):
                                            data["toolType"] = "2"
                                        elif "foret" in data["comment"]:
                                            data["toolType"] = "7"
                                            ### data["neckAngle"] = "140"
                                        else:
                                            data["toolType"] = "0"
                                    except Exception:
                                        data["toolType"] = "type not found"
                                    break

                                elif ("dixi" in href):
                                    valid_mfr = True
                                    data["mfr"] = "DIXI"
                                    link = href

                                    # DIXI 1345-5D-HH 387229
                                    # Need to post to DIXI website @ https://dixipolytool.ch/shop/fr/family/search to send value of reference as "search_term"
                                    ref_serial = ref.strip()

                                    #get the right side of ref_serial
                                    search_ref = ref_serial.split(" ")[-1]
                                    

                                    # Run the async function
                                    link = await send_post_request(search_ref)
                                    link = str(link)
                                    await page.goto(link, timeout=10000)
                                    await page.wait_for_load_state("load")                
                                    await asyncio.sleep(2)
                                    progress_dialog.Update(50, "Extracting data from Dixi...")
                                    try:
                                        # Extract the reference number from the data["reference"]
                                        ref_number = data["reference"].split(" ")[2]
                                        data["name"] = ref_number
                                        name = await page.query_selector("h1")
                                        data["reference"] = await name.inner_text()
                                    except Exception:
                                        data["name"] = "Name not found"
                                    try:
                                        image = await page.query_selector("img.product-image")
                                        image_url = await image.get_attribute("src")
                                        data["image_url"] = image_url
                                    except Exception:
                                        data["image_url"] = "Image not found"

                                    try:
                                        #try to download the step file
                                        #https://dixipolytool.ch/shop/STEP/all/387351.step
                                        step_link = f"https://dixipolytool.ch/shop/STEP/all/{data["name"]}.step"
                                        await download_step_file(ref, step_link)

                                    except Exception as e:
                                        print(f"Error downloading STEP file: {e}")
                                
                                    #need to extract the data from the dl tag 
                                    try:
                                        rows = await page.query_selector_all("dl.product-summary dt, dl.product-summary dd")
                                        for i in range(0, len(rows), 2):
                                            key = await rows[i].inner_text()
                                            value = await rows[i+1].inner_text()
                                            data[key] = value

                                            #check tool type
                                            if "rayon" in key:
                                                data["toolType"] = "1"
                                            elif "hémisphérique" in key:
                                                data["toolType"] = "2"
                                            elif "Perçage" in key:
                                                data["toolType"] = "7"
                                                ### data["neckAngle"] = "140"


                                    except Exception as e:
                                        print(f"Error extracting table data: {e}")
                                    try:
                                        # Find the table row that matches the reference number
                                        rows = await page.query_selector_all("#table-product tbody tr")
                                        for row in rows:
                                            ref_element = await row.query_selector("td:nth-child(1)")
                                            ref_value = await ref_element.inner_text()
                                            if ref_value == ref_number:
                                                # Extract values from the matching row
                                                d1 = await (await row.query_selector("td:nth-child(2)")).inner_text()
                                                l1 = await (await row.query_selector("td:nth-child(3)")).inner_text()
                                                d = await (await row.query_selector("td:nth-child(4)")).inner_text()
                                                l = await (await row.query_selector("td:nth-child(5)")).inner_text()
                                                z = await (await row.query_selector("td:nth-child(6)")).inner_text()
                                                matter = await (await row.query_selector("td:nth-child(7)")).inner_text()
                                                step = await (await row.query_selector("td:nth-child(9)")).inner_text()
                                                data["DC"] = d1
                                                data["APMXS"] = l1
                                                data["DCONMS"] = d
                                                data["OAL"] = l
                                                data["ZEFP"] = z
                                                data["toolMaterial"] = matter
                                                data["mfrRef"] = ref_serial
                                                #fix drill type
                                                data["FHA"] = '140'
                                                break
                                    except Exception as e:
                                        print(f"Error extracting table data: {e}")   
                                        
                                    break

                                elif ("fraisa" in href):
                                    valid_mfr = True
                                    data["mfr"] = "Fraisa"
                                    # Construct the URL for downloading the XML file
                                    reference_code = ref.strip()
                                    progress_dialog.Update(50, "Extracting data from Fraisa...")
                                    url = f"https://fsa.salessupportserver.com/CIMDataService_3S-FSA/DownloadService.svc/web/GetExport?OrderCode={reference_code}&ExportType=din4000xml2016"
                                    xml_file_path = await download_xml_file(reference_code, url)
                                    break

                                # Add after Fraisa block:

                    
                                elif ("hoffman" in href) or ("holex" in href):
                                    valid_mfr = True
                                    data["mfr"] = "Hoffman"
                                    #https://www.hoffmann-group.com/FR/fr/hof/p/203054-18?tId=4
                                    #203054 18
                                    num = ref.replace(" ", "-") 

                                    if num:
                                        ref_serial = str(num)
                                        mfr_link = f"https://www.hoffmann-group.com/FR/fr/hof/p/{ref_serial}?tId=4"
                                        await page.goto(mfr_link, timeout=10000)
                                        await page.wait_for_load_state("domcontentloaded")
                                        await asyncio.sleep(2)
                                        try:
                                            comment = await page.query_selector("h1")
                                            data["comment"] = await comment.inner_text()
                                            
                                            data["name"] = ref

                                        except Exception:
                                            data["comment"] = "Name not found"
                                        try:
                                            image = await page.query_selector("div.imagecontainer img")                                        
                                            image_url = await image.get_attribute("src")
                                            data["image_url"] = image_url
                                        except Exception:
                                            data["image_url"] = "Image not found"
                                        # Extract data from the 'Caractéristiques techniques' table
                                        try:
                                            # Wait for the table to be available
                                            await page.wait_for_selector('div#technicalData table')

                                            # Select all rows in the technical data table
                                            rows = await page.query_selector_all('div#technicalData table tbody tr')

                                            for row in rows:
                                                try:
                                                    # Get the key and value cells
                                                    key_element = await row.query_selector('td:nth-child(1)')
                                                    value_element = await row.query_selector('td:nth-child(3)')

                                                    # Extract text from the key and value cells
                                                    key = await key_element.inner_text()
                                                    value = await value_element.inner_text()

                                                    if key.strip() and value.strip():
                                                        data[key.strip()] = value.strip()
                                                except Exception as e:
                                                    print(f"Row parsing error: {e}")
                                        except Exception as e:
                                            print(f"Error extracting technical data: {e}")

                            
                                        # Map extracted data to standardized keys
                                        # D1
                                        data["D1"] = data.get("⌀ nom. DC", "")
                                        data["DC"] = data.get("⌀ dents DC", "")
                                        # D2
                                        data["DCONMS"] = data.get("⌀ queue Ds", "")
                                        # L1
                                        data["APMXS"] = data.get("Longueur de coupe Lc", "") 
                                        data["APMX"] = data.get("Profondeur de perçage maximale recommandée L2", "")
                                        # L2
                                        data["LH"] = data.get("Longueur de col L1 avec détalonnage", "")
                                        data["LN"] = data.get("Longueur des goujures Lc", "")
                                        # L3
                                        data["OAL"] = data.get("Longueur totale L", "")
                                        # Z
                                        data["ZEFP"] = data.get("Nombre de dents Z", "")
                                        data["toolMaterial"] = data.get("Type d'outils", "")
                                        data["CHW"] = data.get("Largeur du chanfrein", "")
                                        data["FHA"] = data.get("Angle d'hélice", "")
                                        data["CCC"] = data.get("Arrosage interne", "")
                                        data["CSP"] = data.get("Direction de l'approche", "")
                                        data["TCDCON"] = data.get("Queue", "")
                                        data["Code barre"] = data.get("EAN / GTIN", "")
                                        data["mfr"] = "Hoffman"
                                        data["mfrRef"] = ref
                                        data["mfrSecRef"] = data.get("Série", "")
                                        #data["comment"] = data.get("Manufacturer", "")

                                        #check tool type
                                        #Type de produit: Fraise à dresser
                                        if "toriques" in data["Type de produit"]:
                                            data["toolType"] = "1"                                    
                                        elif "hémisphérique" in data["Type de produit"]:
                                            data["toolType"] = "2"
                                        elif "Ebavureurs" in data["Type de produit"]:
                                            data["toolType"] = "3"
                                        elif "Fraises pour rainures en T" in data["Type de produit"]:
                                            data["toolType"] = "4"
                                        elif "Foret à centrer" in data["Type de produit"]:
                                            data["toolType"] = "5"
                                        elif "Foret à centrer" in data["Type de produit"]:
                                            data["toolType"] = "6"
                                        elif "Foret hélicoïdaux" in data["Type de produit"]:
                                            data["toolType"] = "7"
                                        else:
                                            data["toolType"] = "0"
                                    break
                                
                                elif ("jongen" in href):
                                    valid_mfr = True
                                    data["mfr"] = "Jongen"
                                    # Construct the URL for downloading the XML file
                                    reference_code = ref.strip()
                                    progress_dialog.Update(50, "Extracting data from Jongen...")
                                    url = f"https://jongen.salessupportserver.com/wcf-productive/CIMDataService.WebSiteServices.svc/web/ExportData?SessionIDString=bkVlT3FPT1Y1WUhZMWtBNkhlOHBaK0lqMjIvaHltV1BhWi9Mdm1OUW5rVkE5ZENtbVdrSzFGT09URkphdHo3RkJueWNOMHZXSDBoSFhodkNpZ1BZQjVjdDJRY1JIWjNxTE9CTlhFaVpFeGFIOWlZUG5mSE80WmtZdGtiRUc0Z3Vuemp5VGJscXBLNC8xTUtjbDB5dTFKeHZubnA0aGxDOW5Wa0t1UUVBNzlxeVgzVU4wejhSRjlubVNsbGVuTFhDdGFUMklnaWFSRHhWNy9NS3R4MFEyZkE5SmhSRzJLRmk0TERoRm1VaEFhT3JxcDVSZjJwcmRXRGt6S2ZVUGFpekZnajJIdk5OWkpiNUtwWTZkeWtZM2xJVTB1QmZmVXd1c1pSVDM3WVdIT3dZeUl0MDNYTXp5Z0pGVytId2xrb3c%3d&EDP={reference_code}&ExportFormat=DIN4000&ExportOption=XML2021&downloadfilename=&cuid="
                                    xml_file_path = await download_xml_file(reference_code, url)
                                    break

                                elif ("kennametal" in href):
                                    valid_mfr = True
                                    data["mfr"] = "Kennametal"
                                    # Extract data from the Kennametal website
                                    # Navigate to the main page
                                    url = f"https://www.kennametal.com/fr/fr/site-search.html?query={ref}"
                                    await page.goto(url)
                                    
                                    #<h3 class="product-code"><span class="label">Numéro de matériel</span><span class="value">5824171</span></h3>
                                    # extract the reference number
                                    try:
                                        ref_element = await page.query_selector("h3.product-code span.value")
                                        ref_number = await ref_element.inner_text()
                                        reference_code = ref_number.strip()
                                        progress_dialog.Update(50, "Extracting data from Fraisa...")
                                        #https://kennametal.salessupportserver.com/wcf-prod22/CIMDataService.Kennametalservices.svc/web/GetArticleExportREST?J21=2888306&ExportFormat=DIN4000&ExportOption=XML2016
                                        url = f"https://kennametal.salessupportserver.com/wcf-prod22/CIMDataService.Kennametalservices.svc/web/GetArticleExportREST?J21={reference_code}&ExportFormat=DIN4000&ExportOption=XML2016"
                                        xml_file_path = await download_xml_file(reference_code, url)
                                        data["name"] = ref
                                    except Exception:
                                        data["code"] = "code not found"
                                    break

                               
                                elif ("sandvik" in href):
                                    valid_mfr = True
                                    ref_serial = ref.replace(" ", "%20")
                                    sandvik_link = f"https://www.sandvik.coromant.com/fr-fr/search?q={ref_serial}&origin=top%20search%20bar"
                                    await page.goto(sandvik_link, timeout=10000)
                                    await page.wait_for_load_state("domcontentloaded")
                                    await asyncio.sleep(2)

                                    accept_cookies = await page.query_selector("button#onetrust-accept-btn-handler")
                                    if accept_cookies:
                                        await accept_cookies.click()
                                    await asyncio.sleep(5)
                                    bracket = await page.query_selector("i.icon-bracket-down")
                                    if bracket:
                                        await bracket.click()
                                    await asyncio.sleep(2)
                                    break

                                elif ("seco" in href):
                                    valid_mfr = True
                                    seco_link = href
                                    data["mfr"] = "Seco"
                                    await page.goto(seco_link, timeout=10000)
                                    await asyncio.sleep(2)
                                    break

                                elif ("walter" in href):
                                    valid_mfr = True
                                    data["mfr"] = "Walter"
                                    
                                        
                                    try:
                                        # Navigate to product page
                                        ref_code = ref.strip() 
                                        url = f"https://www.walter-tools.com/fr-fr/search/product/{ref_code}"
                                        await page.goto(url)
                                        await page.wait_for_load_state("domcontentloaded")
                                        await asyncio.sleep(2)

                                        # Click download button by span text
                                        download_button = await page.query_selector("span.l-btn-text:has-text('Télécharger')")
                                        if download_button:
                                            await download_button.click()
                                            await asyncio.sleep(2)

                                            # Find and click checkbox by label text
                                            checkbox = await page.query_selector("label.custom-checkbox-label:has-text('Je donne mon accord')")
                                            if checkbox:
                                                await checkbox.click()
                                                await asyncio.sleep(2)

                                                # Get download link from XML button
                                                xml_button = await page.query_selector("button:has-text('XML – DIN 4000  (standard)')")
                                                if xml_button:
                                                    # Get parent div that contains data-download-uri
                                                    download_div = await page.query_selector("div.group-item:has(button:has-text('XML – DIN 4000  (standard)'))")
                                                    if download_div:
                                                        download_uri = await download_div.get_attribute("data-download-uri")
                                                        if download_uri:
                                                            # Extract article number for filename
                                                            article_element = await page.query_selector("product-details-price .product-detail-data-table .value")
                                                            article_number = await article_element.inner_text()
                                                            xml_file_path = await download_xml_file(article_number.strip(), download_uri)
                                                            data["name"] = ref
                                                        else:
                                                            data["code"] = "download URI not found"
                                                    else:
                                                        data["code"] = "download div not found"
                                                else:
                                                    data["code"] = "XML button not found"
                                            else:
                                                data["code"] = "checkbox not found"
                                        else:
                                            data["code"] = "download button not found"
                                    except Exception as e:
                                        print(f"Error processing Walter tool: {e}")
                                        data["code"] = "code not found"
                                    break



                                    '''try:
                                    # Get article number (first .value)
                                    article_element = await page.query_selector("product-details-price .product-detail-data-table .value")
                                    # Get product code (second .value)
                                    product_element = await page.query_selector_all("product-details-price .product-detail-data-table .value")
                                    
                                    if article_element and len(product_element) > 1:
                                        article_number = await article_element.inner_text()
                                        product_code = await product_element[1].inner_text()
                                        
                                        # Use article number for EDP, full reference for filename
                                        edp = article_number.strip()
                                        filename = f"{article_number.strip()}_{product_code.strip()}_DIN4000_strict.xml"
                                        progress_dialog.Update(50, "Extracting data from Walter...")
                                        
                                        session_id = "OEU4cGZJQm9VV2cybkNFcjNTNzlQdGsyVjIzN3dkd1JpRmZGM1JkUVJTeFhHTG1YdkdRSU1CeVpodnFBaTNNTGEzY1BGUjRqZlFlVUIxeyhIWG93T3dWTWtqdDF0NVMzRkRFTTVzSlNnZ2NqUkpLSFFzcFI5UXpSci9MdXlQZVVtaG94Sm1rb2RzcFdPcWVEdHh5dTNnbGdVZEtBTkxEUm10ekZnYlpyRzlEYTBVRU9NZFZSMk9rRkJ2Skk1WWF0SE11cDlNSEszZkhpbElkMnlDVzdXRzl3R3AzM2ZSdmFnL2RocGJsWkhYZEJlTTM4VFRKOVJ0Vk1USFJnUDFneWZpSFJXazhJdFEwSFpEVll4NFpuOXhUbEY0bUNsUDBRNEFyK0lFOTRFQm89"
                                        url = f"https://productdata.walter-tools.com/CIMDataService_3S_WR_HTML/CIMDataService.WebSiteServices.svc/web/ExportData?SessionIDString={session_id}&EDP={edp}&ExportFormat=DIN4000&ExportOption=XML2016&downloadfilename={filename}&auth=4pHbRtSmjga9I2m19rgiiFBqilM%3d&cuid="
                                        
                                        xml_file_path = await download_xml_file(edp, url)
                                        data["name"] = ref
                                    else:
                                        data["code"] = "reference not found"
                                except Exception as e:
                                    print(f"Error extracting Walter reference: {e}")
                                    data["code"] = "code not found"
                                break'''
                                                                                                
                    if valid_mfr:
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

                        elif xml_file_path:
                            progress_dialog.Update(80, "Processing data...")
                            tool = select_xml_type( "Null", xml_file_path)
                            
                            # remove the xml file after parsing
                            os.remove(xml_file_path)

                        elif seco_link: 
                            progress_dialog.Update(50, "Extracting data from Seco...")
                        
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


                            
                                                
                    
                        try: 
                            if  data["name"]:
                                if not xml_file_path:

                                    progress_dialog.Update(70, "Processing data...")
                                    print("\nTool Data:")

                                    '''for key, value in data.items():
                                        print(f"{key}: {value}")'''

                                    # Save the image if available
                                    '''if "image_url" in data and data["image_url"] != "Image not found":
                                        try:
                                            response = await page.goto(data["image_url"])
                                            image_data = await response.body()
                                            with open(f"{data['name']}.png", "wb") as file:
                                                file.write(image_data)
                                        except Exception as e:
                                            print(f"Error saving image: {e}")'''

                                    progress_dialog.Update(90, "Saving data...")
                                    # Save the data to a JSON file
                                    try:
                                        with open(f"{data['name']}_data.json", "w") as json_file:
                                            json.dump(data, json_file, indent=4)
                                        tool = parse_tool_data(f"{data['name']}_data.json")
                                        print(tool.getAttributes())
                                        # remove the json file after parsing
                                        os.remove(f"{data['name']}_data.json")
                                    except Exception as e:
                                        print(f"Error saving tool data to JSON: {e}")
                        except Exception as e:
                            print(f"Error processing data: {e}")
                            

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
