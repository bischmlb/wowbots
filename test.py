import time

if __name__ == '__main__':
    old_ts = 0
    while True:
        new_ts = time.time()
        print(new_ts - old_ts)
        if new_ts - old_ts > 10:
            old_ts = new_ts
            print('test')