def main():

    value = int(input())
    from time import sleep
    for i in range(10):
        value += 100500
        sleep(1)
    print(value)


if __name__ == '__main__':
    main()
