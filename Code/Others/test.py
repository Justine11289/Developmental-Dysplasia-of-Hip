def process_data(data):
    recording = False
    result = ""
    
    for char in data:
        if char == 'D':
            recording = True
            result = ""
        elif char == 'o' and recording:
            result += char
        elif char == 'n' and result == 'o':
            result += char
        elif char == 'e' and result == 'on':
            result += char
        elif char == '!':
            if result == 'Done!':
                recording = False
            else:
                result = ""
        elif recording:
            result += char
    
    return result


# 假設你從某個地方取得即時資訊，例如串流、網路等等
data_stream = "This is a test. D"
result = process_data(data_stream)
print(result)

data_stream = "on"
result = process_data(data_stream)
print(result)

data_stream = "e!"
result = process_data(data_stream)
print(result)

data_stream = "Another Done! message"
result = process_data(data_stream)
print(result)
