"""Fix sys import"""
filepath = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\rl_training_data.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old = '''if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")'''

new = '''if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")'''

content = content.replace(old, new)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed!')
