"""Essai d'accès depuis une machine de GitHub : une requête publique par source, sans clé.
Écrit essai/resultats.json et essai/resultats.md ; ne s'arrête jamais sur une erreur."""
import json, os, time, datetime as dt, urllib.request, urllib.error

UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) essai-acces'}
J2 = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=2)).strftime('%Y-%m-%d')
D0 = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT00:00:00.000Z')
D7 = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=7)).strftime('%Y-%m-%dT00:00:00.000Z')
F = 'https://fapi.binance.com'
TESTS = [
    ('machine', 'où tourne la machine', 'https://ipinfo.io/json', {}),
    ('binance_perp_bougies', 'Binance perpétuels : bougies 1 h', F + '/fapi/v1/klines?symbol=BTCUSDT&interval=1h&limit=3', {}),
    ('binance_perp_funding', 'Binance perpétuels : funding', F + '/fapi/v1/fundingRate?symbol=BTCUSDT&limit=3', {}),
    ('binance_perp_oi', 'Binance perpétuels : open interest', F + '/futures/data/openInterestHist?symbol=BTCUSDT&period=1h&limit=3', {}),
    ('binance_perp_ratio', 'Binance perpétuels : ratio long/short', F + '/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=1h&limit=3', {}),
    ('binance_spot', 'Binance spot : bougies 1 h', 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=3', {}),
    ('binance_spot_miroir', 'Binance spot, miroir de données publiques', 'https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=3', {}),
    ('binance_archives', 'Binance perpétuels : archive journalière (fichier)', f'https://data.binance.vision/data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-{J2}.zip', {}),
    ('bybit_bougies', 'Bybit perpétuels : bougies 1 h', 'https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval=60&limit=3', {}),
    ('bybit_funding', 'Bybit perpétuels : funding', 'https://api.bybit.com/v5/market/funding/history?category=linear&symbol=BTCUSDT&limit=3', {}),
    ('bybit_oi', 'Bybit perpétuels : open interest', 'https://api.bybit.com/v5/market/open-interest?category=linear&symbol=BTCUSDT&intervalTime=1h&limit=3', {}),
    ('okx_bougies', 'OKX perpétuels : bougies 1 h', 'https://www.okx.com/api/v5/market/candles?instId=BTC-USDT-SWAP&bar=1H&limit=3', {}),
    ('okx_funding', 'OKX perpétuels : funding', 'https://www.okx.com/api/v5/public/funding-rate-history?instId=BTC-USDT-SWAP&limit=3', {}),
    ('yahoo_spy', 'Yahoo : SPY, barres journalières', 'https://query1.finance.yahoo.com/v8/finance/chart/SPY?range=5d&interval=1d', {}),
    ('yahoo_bnp', 'Yahoo : BNP Paribas (Paris)', 'https://query1.finance.yahoo.com/v8/finance/chart/BNP.PA?range=5d&interval=1d', {}),
    ('yahoo_eurusd', 'Yahoo : EUR/USD', 'https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?range=5d&interval=1d', {}),
    ('yahoo_us10y', 'Yahoo : taux US 10 ans', 'https://query1.finance.yahoo.com/v8/finance/chart/%5ETNX?range=5d&interval=1d', {}),
    ('yahoo_vix', 'Yahoo : VIX', 'https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?range=5d&interval=1d', {}),
    ('yahoo_spy_15m', 'Yahoo : SPY, bougies 15 min', 'https://query1.finance.yahoo.com/v8/finance/chart/SPY?range=1d&interval=15m', {}),
    ('stooq_spy', 'Stooq : SPY, barres journalières', 'https://stooq.com/q/d/l/?s=spy.us&i=d', {}),
    ('stooq_bnp', 'Stooq : BNP Paribas', 'https://stooq.com/q/d/l/?s=bnp.fr&i=d', {}),
    ('calendrier_tradingview', 'Calendrier économique (flux public de TradingView)', f'https://economic-calendar.tradingview.com/events?from={D0}&to={D7}&countries=US,EU,JP,CH,GB', {'Origin': 'https://www.tradingview.com'}),
    ('calendrier_forexfactory', 'Calendrier économique (Forex Factory, semaine)', 'https://nfs.faireconomy.media/ff_calendar_thisweek.json', {}),
    ('peur_avidite', 'Indice peur et avidité (alternative.me)', 'https://api.alternative.me/fng/?limit=1', {}),
    ('coingecko', 'CoinGecko : cours', 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd', {}),
]

def essai(url, entetes):
    t0 = time.time(); r = {'http': None, 'octets': 0, 'debut': '', 'erreur': None}
    try:
        q = urllib.request.Request(url, headers={**UA, **entetes})
        with urllib.request.urlopen(q, timeout=25) as x:
            b = x.read(200000); r['http'] = x.status; r['octets'] = len(b)
            r['debut'] = b[:160].decode('utf-8', 'replace') if not url.endswith('.zip') else '(archive zip)'
    except urllib.error.HTTPError as e:
        r['http'] = e.code
        try: r['debut'] = e.read(300).decode('utf-8', 'replace')
        except Exception: pass
        r['erreur'] = str(e)
    except Exception as e:
        r['erreur'] = f'{type(e).__name__}: {e}'
    r['ms'] = int((time.time() - t0) * 1000)
    d = r['debut'].lower()
    r['ok'] = r['http'] == 200 and r['octets'] > 40 and 'exceeded' not in d and 'no data' not in d and 'restricted' not in d
    return r

res = {'quand': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), 'essais': []}
for cle, nom, url, ent in TESTS:
    r = essai(url, ent); r.update(cle=cle, nom=nom, url=url)
    if cle == 'machine':
        try:
            i = json.loads(r['debut'] if r['debut'].rstrip().endswith('}') else '{}') or {}
        except Exception: i = {}
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as x: i = json.loads(x.read().decode())
        except Exception: pass
        res['machine'] = {k: i.get(k) for k in ('country', 'region', 'city', 'org')}; r['debut'] = json.dumps(res['machine'], ensure_ascii=False)
    res['essais'].append(r); print(('OK   ' if r['ok'] else 'ÉCHEC'), r['http'], cle, '|', (r['debut'] or r['erreur'] or '')[:110].replace('\n', ' '))
    time.sleep(0.4)

os.makedirs('essai', exist_ok=True)
json.dump(res, open('essai/resultats.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
L = [f"# Essai d'accès — {res['quand']}", '', f"Machine : {json.dumps(res.get('machine'), ensure_ascii=False)}", '', '| Source | Résultat | HTTP | ms |', '|---|---|---|---|']
for r in res['essais']: L.append(f"| {r['nom']} | {'OK' if r['ok'] else 'ÉCHEC'} | {r['http']} | {r['ms']} |")
open('essai/resultats.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
if os.environ.get('GITHUB_STEP_SUMMARY'): open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8').write('\n'.join(L) + '\n')
