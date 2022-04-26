import interpreter


while True:
    text = input('boo > ')
    result, error = interpreter.run('<stdin>', text)

    if error:
        print(error.as_string())
    else:
        print(result)
