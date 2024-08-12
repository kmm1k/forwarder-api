import os

if __name__ == '__main__':
    print("hello")
    number = 20

    # reading the file and deleting it
    try:
        with open('./clean_message_count.txt', 'r') as f:
            clean_message_count = int(f.read())
    except Exception as e:
        print("File not found")
        clean_message_count = 0
    finally:
        # delete file if exists
        try:
            os.remove('./clean_message_count.txt')
        except Exception as e:
            pass
    print(clean_message_count)

    # deleting the file and writing to it
    try:
        os.remove('./clean_message_count.txt')
    except Exception as e:
        pass

    try:
        with open('./clean_message_count.txt', 'w') as f:
            f.write(str(number))
    except Exception as e:
        pass

    try:
        with open('./clean_message_count.txt', 'r') as f:
            clean_message_count = int(f.read())
    except Exception as e:
        print("File not found")
        clean_message_count = 0
    finally:
        # delete file if exists
        try:
            os.remove('./clean_message_count.txt')
        except Exception as e:
            pass
    print(clean_message_count)
