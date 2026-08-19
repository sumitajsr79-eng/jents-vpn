import urllib.request
import csv
import io
import base64

url = 'http://www.vpngate.net/api/iphone/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=6) as resp:
    data = resp.read().decode('utf-8', 'ignore')
    lines = [l for l in data.splitlines() if not l.startswith('*') and l.strip()]
    reader = csv.reader(io.StringIO('\n'.join(lines)))
    header = next(reader)
    for row in reader:
        if len(row) > 14:
            ip = row[1]
            country = row[5]
            ovpn_b64 = row[14]
            if ovpn_b64:
                try:
                    ovpn_text = base64.b64decode(ovpn_b64).decode('utf-8', 'ignore')
                    # Find remote lines
                    remote_lines = [l for l in ovpn_text.splitlines() if l.startswith('remote ')]
                    proto_lines = [l for l in ovpn_text.splitlines() if l.startswith('proto ')]
                    print(f"Server {country} ({ip}) -> Remote: {remote_lines}, Proto: {proto_lines}")
                except Exception as e:
                    print(e)
            break
