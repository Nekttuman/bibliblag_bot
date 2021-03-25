
import time

browser_instance = {}

if __name__ == "__main__":  
    print(browser_instance)  
    while True:
        for i in browser_instance:
            if time.time() - browser_instance[i][1] > 1:
                print(browser_instance[i])
                print('hello')
                break

