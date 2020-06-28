def save(j: str, file_name: str):
  with open(file_name, "w", encoding = "utf-8") as f:
    f.write(j)
