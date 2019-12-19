def save(j: str, file_name: str):
  f = open(file_name, 'w', encoding = 'utf-8')
  f.write(j)
