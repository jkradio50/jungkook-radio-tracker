from playwright.async_api import async_playwright

async def scrape_stations():
    artist_url = "https://onlineradiobox.com/artist/785052275-jung-kook"
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = await browser.new_page()
        await page.goto(artist_url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        rows = await page.query_selector_all("tr.now_playing_tr")

        for row in rows:
            song_el = await row.query_selector("div.table__track-title span")
            if not song_el:
                continue
            song = await song_el.inner_text()
            if "unknown" in song.lower() or not song.strip():
                continue

            station_el = await row.query_selector("div.table__track-onair")
            station = await station_el.inner_text() if station_el else "Unknown Station"

            btn = await row.query_selector("button.station_play")
            radio_id = await btn.get_attribute("radioid") if btn else None

            if radio_id and "." in radio_id:
                country, slug = radio_id.split(".", 1)
                station_url = f"https://onlineradiobox.com/{country}/{slug}/?played=1&cs={radio_id}"
            else:
                continue

            station_page = await browser.new_page()
            try:
                await station_page.goto(station_url)
                await station_page.wait_for_timeout(2000)

                # Website fallback
                website_el = await station_page.query_selector("a.station__reference--web")
                website = await website_el.get_attribute("href") if website_el else station_url
                website = website if website else station_url

                # Twitter (if not a share or intent link)
                twitter_el = await station_page.query_selector(
                    'a[href*="twitter.com"]:not([href*="intent"]):not([href*="share"])')
                twitter = await twitter_el.get_attribute("href") if twitter_el else "n/a"
                if not twitter or twitter.strip() == "" or "onlineradiobox" in twitter:
                    twitter = "n/a"

                # Facebook (skip share.php)
                facebook_el = await station_page.query_selector('a.i-fb--reference') or \
                              await station_page.query_selector('a[href*="facebook.com"]:not([href*="share.php"])')
                facebook = await facebook_el.get_attribute("href") if facebook_el else "n/a"

                results.append({
                    "song": song,
                    "station": station,
                    "station_url": station_url,
                    "website": website,
                    "twitter": twitter,
                    "facebook": facebook
                })

            except Exception as e:
                print(f"❌ Error: {e}")
            await station_page.close()

        await browser.close()
    return results
