import os
import emoji

for root, _, files in os.walk('.'):
    if '.git' in root or '.venv' in root: continue
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            new_content = emoji.replace_emoji(content, replace='')
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Removed emojis from {path}')
