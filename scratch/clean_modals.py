with open('frontend/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = lines[:1649] + lines[1801:1879] + lines[2031:2081] + lines[2233:]
content = ''.join(new_lines)
count = content.count('id="parameterDetailModal"')
print(f'New count: {count}')
assert count == 1, f'Expected 1, got {count}'

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Successfully cleaned up extra duplicate modals!')
