from playwright.async_api import async_playwright

async def scrape_stations():
    artist_url = "https://onlineradiobox.com/artist/785052275-jung-kook"
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        page = await context.new_page()

        try:
            await page.goto(artist_url, timeout=20000, wait_until="networkidle")
            await page.wait_for_selector("tr.now_playing_tr", timeout=5000)
        except Exception as e:
            print(f"🔥 Failed to load artist page: {e}")
            await browser.close()
            return []

        rows = await page.query_selector_all("tr.now_playing_tr")

        for row in rows:
            try:
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

                if not radio_id or "." not in radio_id:
                    continue

                country, slug = radio_id.split(".", 1)
                station_url = f"https://onlineradiobox.com/{country}/{slug}/?played=1&cs={radio_id}"

                station_context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
                station_page = await station_context.new_page()

                try:
                    await station_page.goto(station_url, timeout=5000, wait_until="networkidle")
                    await station_page.wait_for_timeout(1000)

                    # Website
                    website_el = await station_page.query_selector("a.station__reference--web")
                    website = await website_el.get_attribute("href") if website_el else station_url

                    # Twitter
                    twitter_el = await station_page.query_selector('a.i-tw--reference') or \
                                 await station_page.query_selector('a[href*="twitter.com"]:not([href*="intent"]):not([href*="share"])')
                    twitter_href = await twitter_el.get_attribute("href") if twitter_el else None
                    if twitter_href and "twitter.com" in twitter_href and not twitter_href.endswith("/share"):
                        twitter_handle = twitter_href.split("twitter.com/")[-1].split("/")[0].replace("@", "")
                        twitter = f"https://twitter.com/intent/tweet?text=Thank%20you%20%40{twitter_handle}%20for%20playing%20%23{song.replace(' ', '')}%20by%20Jung%20Kook."
                    else:
                        twitter = "n/a"

                    # Facebook
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
                    print(f"❌ Error loading station page: {e}")
                finally:
                    await station_page.close()
                    await station_context.close()

            except Exception as e:
                print(f"❌ Error parsing row: {e}")

        await browser.close()
    return results
