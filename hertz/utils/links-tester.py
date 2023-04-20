import webbrowser

import time

# Register Firefox as the preferred browser
webbrowser.register('debug_chrome', None, webbrowser.BackgroundBrowser("/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --auto-open-devtools-for-tabs"))

# Open the file containing the URLs
with open('links.txt', 'r') as f:
    urls = f.readlines()

# Loop through each URL and open it in Firefox
# for url in urls:
#     webbrowser.open_new_tab(url.strip())

for i,url in enumerate(urls):
    if i<2:
        webbrowser.open_new_tab(url.strip())