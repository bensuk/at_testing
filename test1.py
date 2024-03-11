        
buffer = [b'vienas', b'du', b'trys', b'keturi']
buffer2 = [b'otther', b'1du', b'2trys', b'4keturi']




result = buffer[:-1] + buffer2[:2+1]

print(result)

buffer = buffer2[2+1:]

print(result)
print(buffer)
print(buffer2)
